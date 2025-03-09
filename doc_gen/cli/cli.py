import click

@click.command()
def desafio_globo():
    click.echo("STARTING...")
    xd = click.edit(text="__# Paste your function code below:__\n")
    xd = xd.replace("__# Paste your function code below:__\n", "")