import sentry_sdk

from src import settings
from src.services.provision.service import ProvisionService
from src.services.validation.service import ValidationService
import click


def create_compute_instance():
    provisioner = ProvisionService()


@click.group()
def cli():
    pass


@cli.command(name='validate')
@click.option('--file-name', '-f', help='Name of the file to process.')
@click.option('--change-type', '-c', type=click.Choice(['A', 'D', 'M', 'R']),
              help='Type of change to apply to the file content: uppercase or lowercase. Default is uppercase.')
def validate(file_name, change_type):
    validation = ValidationService()
    if change_type == 'D':
        return
    with open(file_name, 'r') as file:
        file_data = file.read()
        validation.get_config_from(file_data)
        click.echo(f"File {file_name} is valid")


if __name__ == "__main__":
    sentry_sdk.init(dsn=settings.AppSettings.sentry_dsn)
    cli()
