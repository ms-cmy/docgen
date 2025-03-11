import click
import os
from doc_gen.agent_doc_gen import long_agents

@click.command()
@click.option('--file', '-f', multiple=False, help='um arquivo yaml')
def doc_gen(file):
    click.echo("STARTING...")
    if os.path.exists(file):
        click.echo(f"arquivo: {file}")
        long_agents.docgen_runner(file)
    else:
        click.echo("sem arquivo")