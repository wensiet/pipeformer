import logging
import time

from src.integrations.timeweb.wrapper import TimewebWrapper
from src.services.validation.dto import ComputeConfig
from src.settings import AppSettings


class ProvisionService:
    def __init__(self):
        self.timeweb = TimewebWrapper()

    def create_compute(self, config: ComputeConfig, service_key: int = AppSettings.service_key_id):
        logging.info(f"Initialized compute creation with name: {config.name}")
        user_key = self.timeweb.create_ssh_key(f"compute-{config.name}", config.ssh_key)
        logging.info(f"User-key created with id: {user_key}")
        compute = self.timeweb.create_compute(config.name, config.preset, config.os, [user_key, service_key])
        logging.info(f"Compute created with id: {compute.id}")

        logging.info(f"Waiting for compute to be ready...")
        while compute.status != "on":
            compute = self.timeweb.get_compute(compute.id)
            logging.info(f"Compute status: {compute.status}")
            time.sleep(15)

        logging.info("Provisioning finished, your SSH key may be not available yet.")

        ipv4 = None
        for network in compute.networks:
            for ip in network.ips:
                if ip.type == "ipv4":
                    ipv4 = ip
                    break

        logging.info("+" + "-" * 22 + " Compute Data " + "-" * 22 + "+")
        logging.info("|{:<25} {:<25}|".format("Name:", compute.name))
        logging.info("|{:<25} {:<25}|".format("OS:", compute.os.name))
        logging.info("|{:<25} {:<25}|".format("CPU:", compute.cpu))
        logging.info("|{:<25} {:<25}|".format("RAM:", compute.ram))
        logging.info("|{:<25} {:<25}|".format("IP:", ipv4.ip))
        logging.info("+" + "-" * 55 + "+")

    def delete_compute(self, compute_id: int):
        logging.info(f"Deleting compute with id: {compute_id}")
        self.timeweb.delete_compute(compute_id)
        logging.info(f"Compute with id: {compute_id} deleted")
        logging.info("Compute deletion finished")
