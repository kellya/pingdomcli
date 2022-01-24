# pingdomcli

This CLI allows you to interact with pingdom via the API to:
 - get status of checks (can choose statuses of: up, down, paused)
 - add a new check
 - get a list of checks
 - remove checks

# installation
## via pypi
`pip install pingdomcli`
## via poetry
 1. Clone the repo
 2. `poetry shell`
 3. `poetry install`
 4. `python pingdomcli pdcli.py`

# usage
For full usage, run `pdcli --help`

The first task is to create a conf.yaml.  By default pdcli will look for this in
the current directory.  You may specify an alternate path with the `--config <file
path>` option.
