import json
import logging
import subprocess

from pydantic import BaseModel
from typing import List

from src.services.validation.dto import Playbook, Var
from src.integrations.vault.extractor import VaultSecretExtractor


class PlaybookRunnable(BaseModel):
    initial: Playbook
    file_name: str

    def run(self, inv_file: str = "inventory.ini"):
        self._load_variables(self.initial.vars)
        command = [
            'ansible-playbook', self.file_name,
            '-i', inv_file,
            '--private-key', '~/.ssh/id_rsa',
            '-e', '@extra-vars.json'
        ]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        for line in iter(process.stdout.readline, ''):
            logging.info(line.strip())

        process.wait()

        if process.returncode == 0:
            logging.info(f"Playbook '{self.initial.name}' executed successfully!")
        else:
            logging.error(f"Playbook '{self.initial.name}' has failed!")
            print("STDERR:\n", process.stderr.read())

    @staticmethod
    def _load_variables(var_list: List[Var]):
        extractor = VaultSecretExtractor()

        var_list_dict = {}
        for elem in var_list:
            if isinstance(elem.value, str) and elem.value.startswith("vault@"):
                var_list_dict[elem.name] = extractor.get_secret(elem.value)
            else:
                var_list_dict[elem.name] = elem.value

        with open("extra-vars.json", 'w') as f:
            f.write(json.dumps(var_list_dict))
