import requests
import rich
from rich.console import Console
from rich.table import Table
import conf


def main():
    # Load configuration, this will eventuall be handled by click
    conf.load("conf.yaml")

    # initialize rich console
    console = Console()

    # create a wait spinner while we get data from pingdom api
    with console.status(f"Getting pingdom status...", spinner="point"):
        response = requests.get(conf.BASE_URL + "/checks", auth=(conf.API_KEY, ""))

    # create a rich table to display the data
    table = Table(title="Pingdom Checks")
    table.add_column("Name", justify="left")
    table.add_column("Status", justify="center")
    table.add_column("Last Response", justify="center")
    # loop through all of the checks and add them to the table
    for check in response.json()["checks"]:
        # colorize the status based on the status code
        if check["status"] == "up":
            status = "[green]UP[/green]"
        elif check["status"] == "paused":
            status = "[yellow]PAUSED[/yellow]"
        else:
            status = "[red]DOWN[/red]"
        table.add_row(check["name"], status, str(check["lastresponsetime"]))

    console.print(table)


if __name__ == "__main__":
    main()
