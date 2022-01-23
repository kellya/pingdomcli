"""main interface for the pingdombot"""
import sys
import requests
import click
import yaml
from rich.table import Table
from rich.console import Console

__version__ = "0.1.0"


def get_config(configfile):
    """read a yaml config file and return a dict"""
    with open(configfile, "r", encoding="utf-8") as f:  # pylint: disable=invalid-name
        config = yaml.safe_load(f)
    return config


@click.group(invoke_without_command=True)
@click.version_option(__version__, help="Show the version number and exit.")
@click.option(
    "--config", "-c", default="conf.yaml", type=click.Path(), help="config file to use"
)
@click.option(
    "--show",
    "-s",
    default=["up", "down", "paused"],
    multiple=True,
    help="The statuses to show",
)
@click.pass_context
def main(ctx, config, show):
    """main entry to the pingdombot"""
    if ctx.invoked_subcommand is None:
        ctx.invoke(status, config=config, show=show)
        sys.exit(0)


@main.command()
@click.option(
    "--config", "-c", default="conf.yaml", type=click.Path(), help="config file to use"
)
@click.option(
    "--show",
    "-s",
    default=["up", "down", "paused"],
    multiple=True,
    help="The statuses to show",
)
@click.pass_context
def status(ctx, config, show):  # pylint: disable=unused-argument
    """get the latest pingdom status"""

    conf = get_config(config)

    # initialize rich console
    console = Console()

    # create a wait spinner while we get data from pingdom api
    with console.status(f"Getting pingdom status...", spinner="point"):
        response = requests.get(
            conf["BASE_URL"] + "/checks", auth=(conf["API_KEY"], "")
        )
        if response.status_code != 200:
            console.print(
                "[red]Error[/red] obtaining status. "
                "Check your [yellow]API_KEY[/yellow] setting in "
                "[bold]{config}[/bold]"
            )
            sys.exit(1)

    # create a rich table to display the data
    table = Table(title="Pingdom Checks")
    table.add_column("Name", justify="left")
    table.add_column("Status", justify="center")
    table.add_column("Last Response", justify="center")
    # loop through all of the checks and add them to the table
    count = 0
    for check in response.json()["checks"]:
        if check["status"] == "up" and "up" in show:
            count += 1
            table.add_row(
                check["name"], "[green]UP[/green]", str(check["lastresponsetime"])
            )
        elif check["status"] == "down" and "down" in show:
            count += 1
            table.add_row(
                check["name"], "[red]DOWN[/red]", str(check["lastresponsetime"])
            )
        elif check["status"] == "paused" and "paused" in show:
            count += 1
            table.add_row(
                check["name"], "[yellow]Paused[/yellow]", str(check["lastresponsetime"])
            )
        else:
            # if there is another status, output it
            count += 1
            table.add_row(
                check["name"], "[blue]?[/blue]", str(check["lastresponsetime"])
            )

    if not count == 0:
        console.print(table)
    else:
        console.print("No hosts match your criteria")


@main.command()
@click.option(
    "--config", "-c", default="conf.yaml", type=click.Path(), help="config file to use"
)
@click.option(
    "--type",
    "-t",
    "type_",
    default="http",
    type=click.Choice(["http"]),
    prompt=True,
    help="type of check to add",
)
@click.option("--name", "-n", default="", prompt=True, help="name of the check")
@click.option("--url", "-u", default="", prompt=True, help="url of the check")
@click.option(
    "--integration",
    "-i",
    default="",
    prompt=True,
    help="Comma separated list of integration IDs",
)
def add(config, type_, name, url, integration):
    """add a new check to pingdom"""
    conf = get_config(config)
    console = Console()
    integrations = integration.split(",")
    response = requests.post(
        conf["BASE_URL"] + "/checks",
        auth=(conf["API_KEY"], ""),
        data={"name": name, "host": url, "type": type_, "integrationids": integrations},
    )
    if response.status_code == 200:
        console.print(f"[green]Successfully added {name}[/green]")
    else:
        console.print(f"[red]Error adding check[/red].\n{response.json()['error']}")


@main.command(name="list")
@click.option(
    "--config", "-c", default="conf.yaml", type=click.Path(), help="config file to use"
)
def list_checks(config):
    """list all of the checks in pingdom"""
    conf = get_config(config)
    console = Console()
    response = requests.get(conf["BASE_URL"] + "/checks", auth=(conf["API_KEY"], ""))
    if response.status_code != 200:
        console.print(
            "[red]Error[/red] obtaining status. "
            "Check your [yellow]API_KEY[/yellow] setting in "
            "[bold]{config}[/bold]"
        )
        sys.exit(1)

    # create a rich table to display the data
    table = Table(title="Pingdom Checks")
    table.add_column("Name", justify="left")
    table.add_column("URL", justify="center")
    table.add_column("ID", justify="center")
    # loop through all of the checks and add them to the table
    with console.status("Generating list...", spinner="point"):
        for check in response.json()["checks"]:
            url = requests.get(
                conf["BASE_URL"] + "/checks/" + str(check["id"]),
                auth=(conf["API_KEY"], ""),
            )
            try:
                path = url.json()["check"]["type"]["http"]["url"]
                url = f"{check['hostname']}{path}"
            except KeyError:
                url = "N/A"
            table.add_row(check["name"], url, str(check["id"]))

    console.print(table)


@main.command(name="del")
@click.option(
    "--config", "-c", default="conf.yaml", type=click.Path(), help="config file to use"
)
@click.option("--id", "-i", "id_", multiple=True, help="id of the check to delete")
def del_check(config, id_):
    """delete a check from pingdom"""
    conf = get_config(config)
    console = Console()
    # if the tuple has a single element, just pass that as the string of ids
    if len(id_) == 1:
        ids = id_[0]
    # if we have a tuple with multiple elements, join them as a single
    # comma-separated string
    elif len(id_) > 1:
        ids = ",".join(id_)
    else:
        console.print("[red]Error[/red] no check id specified")
        sys.exit(1)

    response = requests.delete(
        conf["BASE_URL"] + "/checks/" + ids,
        auth=(conf["API_KEY"], ""),
        data={"delcheckids": ids},
    )
    if response.status_code == 200:
        console.print(f"[green]Successfully deleted {ids}[/green]")
    else:
        console.print(f"[red]Error deleting check[/red].\n{response.json()['error']}")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
