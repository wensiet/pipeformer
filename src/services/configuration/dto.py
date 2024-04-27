import logging
import subprocess

from pydantic import BaseModel

from src.services.validation.dto import Playbook


class PlaybookRunnable(BaseModel):
    initial: Playbook
    file_name: str

    def run(self, inv_file: str = "inventory.ini"):
        command = [
            'ansible-playbook', self.file_name,
            '-i', inv_file,
            '--private-key', '~/.ssh/id_rsa'
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        for line in iter(process.stdout.readline, ''):
            logging.info(line.strip())

        process.wait()

        if process.returncode == 0:
            logging.info(f"Playbook '{self.initial.name}' executed successful!")
        else:
            logging.error(f"Playbook '{self.initial.name}' has failed!")
            print("STDERR:\n", process.stderr.read())
