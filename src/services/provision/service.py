import logging
import time

from src.integrations.grafana.wrapper import GrafanaWrapper
from src.integrations.timeweb.wrapper import TimewebWrapper
from src.integrations.zabbix.wrapper import ZabbixWrapper
from src.services.provision.dto import ProvisionConfig
from src.services.utils import add_zabbix_metrics, extract_compute_name, get_id_by_uniq, load_new_ssh, map_preset
from src.services.validation.service import ValidationService
from src.settings import AppSettings, GrafanaSettings


class ProvisionService:
    def __init__(self):
        self.timeweb = TimewebWrapper()
        self.zabbix = ZabbixWrapper()
        self.grafana_settings = GrafanaSettings()
        self.grafana = GrafanaWrapper()

    def provision(self, file_name, change_type):
        uniq = extract_compute_name(file_name)
        if change_type == "D":
            self._delete_compute(uniq)
        elif change_type == "A":
            with open(file_name, 'r') as file:
                file_data = file.read()
                config = ValidationService().get_config_from(file_data)
                provision_config = ProvisionConfig(**config.dict(), name=uniq)
                self._create_compute(provision_config)
        else:
            raise ValueError(f"Git change {change_type} is not supported currently.")

    def _create_compute(self, config: ProvisionConfig):
        logging.info(f"Initialized compute creation with name: {config.name}")
        compute = self.timeweb.create_compute(config.name, map_preset(config.flavor),
                                              config.flavor.operating_system,
                                              [])
        logging.info(f"Compute created with id: {compute.id}")

        logging.info(f"Waiting for compute to be ready...")
        while compute.status != "on":
            compute = self.timeweb.get_compute(compute.id)
            logging.info(f"Compute status: {compute.status}")
            time.sleep(15)

        logging.info("Provisioning finished, adding SSH keys")

        ipv4 = compute.extract_ipv4()

        time.sleep(15)

        load_new_ssh(ipv4.ip, "root", compute.root_pass, [config.ssh, AppSettings.service_key])

        logging.info("SSH keys added")

        logging.info("Configuring metrics scraping")
        add_zabbix_metrics(ipv4.ip, "root", compute.root_pass)
        self.zabbix.connect_host(ipv4.ip, compute.name)
        self.grafana.refresh_datasource()
        logging.info("Metrics scraping configured")

        logging.info("+" + "-" * 22 + " Compute Data " + "-" * 22 + "+")
        logging.info("|{:<25} {:<25}|".format("Name:", compute.name))
        logging.info("|{:<25} {:<25}|".format("OS:", compute.os.name))
        logging.info("|{:<25} {:<25}|".format("CPU:", compute.cpu))
        logging.info("|{:<25} {:<25}|".format("RAM:", compute.ram))
        logging.info("|{:<25} {:<25}|".format("IP:", ipv4.ip))
        logging.info("|{:<25} {:<25}|".format("Dashboard:", self.grafana.make_dashboard_link(compute.name)))
        logging.info("+" + "-" * 55 + "+")

    def _delete_compute(self, uniq: str):
        compute_id = get_id_by_uniq(self.timeweb, uniq)
        logging.info(f"Deleting compute with id: {compute_id}")
        self.timeweb.delete_compute(compute_id)
        logging.info(f"Compute with id: {compute_id} deleted")
        logging.info("Compute deletion finished")
