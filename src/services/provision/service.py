import logging
import time

from src.integrations.timeweb.wrapper import TimewebWrapper
from src.services.provision.dto import ProvisionConfig
from src.services.validation.dto import Flavor
from src.settings import AppSettings


class ProvisionService:
    def __init__(self):
        self.timeweb = TimewebWrapper()

    @staticmethod
    def _extract_compute_name(path: str):
        paths = path.replace(".yaml", "").replace(".yml", "").split("/")
        if "compute" in paths:
            paths.remove("compute")
        res = ""
        for p in paths:
            res += p + "-"
        res = res.rstrip("-")
        return res

    def provision(self, config, change_type, file_name):
        uniq = self._extract_compute_name(file_name)
        provision_config = ProvisionConfig(**config.dict(), name=uniq)
        if change_type == "D":
            self._delete_compute(provision_config)
        elif change_type == "A":
            self._create_compute(provision_config)
        else:
            raise ValueError(f"Git change {change_type} is not supported currently.")

    @staticmethod
    def _map_preset(preset: Flavor):
        preset_str = (f"c{preset.cpu_cores}r{preset.RAM.replace('GB', '')}"
                      f"d{preset.disk_space.replace('GB', '')}")
        return preset_str

    def _create_compute(self, config: ProvisionConfig, service_key: int = AppSettings.service_key_id):
        logging.info(f"Initialized compute creation wiath name: {config.name}")
        user_key = self.timeweb.create_ssh_key(f"compute-{config.name}", config.ssh)
        logging.info(f"User-key created with id: {user_key}")
        compute = self.timeweb.create_compute(config.name, self._map_preset(config.flavor),
                                              config.flavor.operating_system,
                                              [user_key, service_key])
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

    def _get_id_by_uniq(self, uniq: str):
        computes = self.timeweb.list_computes()
        for compute in computes:
            if compute.name == uniq:
                return compute.id
        raise ValueError(f"Compute with name {uniq} not found")

    def _delete_compute(self, config: ProvisionConfig):
        compute_id = self._get_id_by_uniq(config.name)
        logging.info(f"Deleting compute with id: {compute_id}")
        self.timeweb.delete_compute(compute_id)
        logging.info(f"Compute with id: {compute_id} deleted")
        logging.info("Compute deletion finished")
