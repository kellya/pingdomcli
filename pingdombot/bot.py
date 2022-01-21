import requests
import rich
from rich.console import Console
from rich.table import Table
import conf

conf.load('conf.yaml')

console = Console()

with console.status(f"Getting pingdom status...", spinner="point"):
    response = requests.get(conf.BASE_URL + '/checks', auth=(conf.API_KEY, ''))

table = Table(title='Pingdom Checks')
table.add_column('Name', justify='left')
table.add_column('Status', justify='center')
table.add_column('Last Response', justify='center')
for check in response.json()['checks']:
    if check['status'] == 'up':
        status = "[green]UP[/green]"
    elif check['status'] == 'paused':
        status = "[yellow]PAUSED[/yellow]"
    else:
        status = "[red]DOWN[/red]"
    table.add_row(check['name'], status, str(check['lastresponsetime']))
console.print(table)
