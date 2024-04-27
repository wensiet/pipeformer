import logging

import sentry_sdk

from src import settings
from src.services.configuration.service import ConfigurationService
from src.services.provision.service import ProvisionService
from src.services.validation.service import ValidationService
import click

validation = ValidationService()
provisioner = ProvisionService()
configuration = ConfigurationService()


@click.group()
def cli():
    logging.getLogger().setLevel(logging.INFO)


@cli.command(name='validate')
@click.option('--file-name', '-f', help='Name of the file to process.')
@click.option('--change-type', '-c', type=click.Choice(['A', 'D', 'M', 'R']))
def validate(file_name, change_type):
    if change_type == 'D':
        return
    with open(file_name, 'r') as file:
        file_data = file.read()
        validation.get_config_from(file_data)
        click.echo(f"File {file_name} is valid")


@cli.command(name='provision')
@click.option('--file-name', '-f', help='Name of the file to process.')
@click.option('--change-type', '-c', type=click.Choice(['A', 'D', 'M', 'R']))
def provision(file_name, change_type):
    provisioner.provision(file_name, change_type)


@cli.command(name='playbooks')
@click.option('--file-name', '-f', help='Name of the file to process.')
@click.option('--change-type', '-c', type=click.Choice(['A', 'D', 'M', 'R']))
def playbooks(file_name, change_type):
    configuration.run_post_scripts(file_name, change_type)


if __name__ == "__main__":
    sentry_sdk.init(dsn=settings.AppSettings.sentry_dsn)
    cli()
