import logging
import re

import git
import sentry_sdk

from src import settings
from src.services.configuration.service import ConfigurationService
from src.services.provision.service import ProvisionService
from src.services.validation.service import ValidationService
import click

REPO_PATTERN = r"compute/([^/]+)/([^/]+\.yaml)"

validation = ValidationService()
provisioner = ProvisionService()
configuration = ConfigurationService()


def get_filepath_and_change_type(old_sha, new_sha):
    repo = git.Repo(".")
    old_commit = repo.commit(old_sha)
    new_commit = repo.commit(new_sha)

    diffs = new_commit.diff(old_commit)
    result = []
    for diff in diffs:
        filename = diff.a_path if diff.change_type != "R" else diff.b_path
        if re.match(REPO_PATTERN, filename):
            result.append(diff)

    if len(result) != 1:
        logging.error(f"Invalid amount of changes (expected 1 got {len(result)})")
        for diff in result:
            logging.error(f"- {diff.change_type} {diff.a_path if diff.change_type != 'R' else diff.b_path}")
        exit(1)

    filename = result[0].a_path if result[0].change_type != "R" else result[0].b_path
    logging.info(f"Changed config is '{result[0].change_type} {filename}'")
    return filename, result[0].change_type


@click.group()
@click.option('--old-sha', default='default_old_sha', help='Old commit SHA')
@click.option('--new-sha', default='default_new_sha', help='New commit SHA')
@click.pass_context
def cli(ctx, old_sha, new_sha):
    logging.getLogger().setLevel(logging.INFO)
    filename, change_type = get_filepath_and_change_type(old_sha, new_sha)
    ctx.obj = {
        "filename": filename,
        "change_type": change_type
    }


@cli.command(name='validate')
@click.pass_context
def validate(ctx):
    if ctx.obj["change_type"] == 'D':
        return
    with open(ctx.obj["filename"], 'r') as file:
        file_data = file.read()
        validation.get_config_from(file_data)
        click.echo(f"File {ctx.obj['filename']} is valid")


@cli.command(name='provision')
@click.pass_context
def provision(ctx):
    provisioner.provision(ctx.obj["filename"], ctx.obj["change_type"])


@cli.command(name='playbooks')
@click.pass_context
def playbooks(ctx):
    configuration.run_post_scripts(ctx.obj["filename"], ctx.obj["change_type"])


if __name__ == "__main__":
    sentry_sdk.init(dsn=settings.AppSettings.sentry_dsn)
    cli()
