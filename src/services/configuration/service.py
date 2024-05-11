import logging
import uuid

import httpx

from src.integrations.timeweb.wrapper import TimewebWrapper
from src.services.configuration.dto import PlaybookRunnable
from src.services.utils import add_to_known_hosts, extract_compute_name, get_id_by_uniq
from src.services.validation.service import ValidationService


class ConfigurationService:

    def __init__(self):
        self.validation_service = ValidationService()
        self._client = httpx.Client()
        self._timeweb = TimewebWrapper()

    def _parse_playbook(self, url):
        response = self._client.get(
            url=str(url)
        )
        response.raise_for_status()

        return response.text

    def _save_playbooks(self, config):
        playbooks = []
        for playbook in config.playbooks:
            logging.info(f"Saving '{playbook.name}' playbook")
            playbook_raw = self._parse_playbook(playbook.link)
            pb = f"{uuid.uuid4()}.yaml"
            with open(pb, 'w') as file:
                file.write(playbook_raw)
            playbooks.append(PlaybookRunnable(initial=playbook, file_name=pb))

        return playbooks

    def run_post_scripts(self, file_name, change_type):
        if change_type == 'D':
            logging.info("Chane type is delete, nothing to run")
            return

        with open(file_name, 'r') as file:
            file_data = file.read()
            config = self.validation_service.get_config_from(file_data)

        logging.info("Gathering info for compute")
        compute_id = get_id_by_uniq(self._timeweb, extract_compute_name(file_name))
        compute = self._timeweb.get_compute(compute_id)
        compute_ipv4 = compute.extract_ipv4()

        logging.info("Creating inventory file")
        with open("inventory.ini", 'w') as file:
            file.write(f"[servers]\n{compute_ipv4.ip} ansible_user=root "
                       f"ansible_ssh_common_args='-o StrictHostKeyChecking=no'")

        playbooks = self._save_playbooks(config)

        add_to_known_hosts(compute_ipv4.ip)
        for pb in playbooks:
            logging.info(f"Executing '{pb.initial.name}' playbook")
            pb.run()
