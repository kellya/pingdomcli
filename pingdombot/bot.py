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
    with open(configfile, 'r', encoding="utf-8")  as f:
        config = yaml.safe_load(f)
    return config

@click.group(invoke_without_command=True)
@click.version_option(__version__, help='Show the version number and exit.')
@click.option('--config', '-c', default='conf.yaml', type=click.Path(), help='config file to use')
@click.option(
    '--show', '-s',
    default=['up','down', 'paused'],
    multiple=True, help='The statuses to show'
)
@click.pass_context
def main(ctx,config,show):
    """main entry to the pingdombot"""
    if ctx.invoked_subcommand is None:
        ctx.invoke(status, config=config, show=show)
        sys.exit(0)

@main.command()
@click.option('--config', '-c', default='conf.yaml', type=click.Path(), help='config file to use')
@click.option(
    '--show', '-s',
    default=['up','down', 'paused'],
    multiple=True, help='The statuses to show'
)
@click.pass_context
def status(ctx, config, show):
    """get the latest pingdom status"""

    conf = get_config(config)

    # initialize rich console
    console = Console()

    # create a wait spinner while we get data from pingdom api
    with console.status("Getting pingdom status...", spinner="point"):
        response = requests.get(
            conf["BASE_URL"] + "/checks", auth=(conf["API_KEY"], ""))

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
            table.add_row(check["name"], "[green]UP[/green]", str(check["lastresponsetime"]))
        elif check["status"] == "down" and "down" in show:
            count += 1
            table.add_row(check["name"], "[red]DOWN[/red]", str(check["lastresponsetime"]))
        elif check["status"] == "paused" and "paused" in show:
            count += 1
            table.add_row(check["name"], "[yellow]Paused[/yellow]", str(check["lastresponsetime"]))
#        table.add_row(check["name"], status, str(check["lastresponsetime"]))

    if not count == 0:
        console.print(table)
    else:
        console.print("No hosts match your criteria")

@main.command()
def echo():
    print("echo")

if __name__ == "__main__":
    main()
