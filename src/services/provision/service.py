import logging
import time
import paramiko

from src.integrations.timeweb.wrapper import TimewebWrapper
from src.integrations.zabbix.wrapper import ZabbixWrapper
from src.services.provision.dto import ProvisionConfig
from src.services.utils import extract_compute_name, get_id_by_uniq
from src.services.validation.dto import Flavor
from src.services.validation.service import ValidationService
from src.settings import AppSettings


class ProvisionService:
    def __init__(self):
        self.timeweb = TimewebWrapper()
        self.zabbix = ZabbixWrapper()

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

    @staticmethod
    def _map_preset(preset: Flavor):
        preset_str = (f"c{preset.cpu_cores}r{preset.RAM.replace('GB', '')}"
                      f"d{preset.disk_space.replace('GB', '')}")
        return preset_str

    @staticmethod
    def _load_new_ssh(server_address, ssh_username, ssh_password, new_keys):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh.connect(server_address, username=ssh_username, password=ssh_password)

            create_ssh_folder_command = "mkdir -p ~/.ssh"
            ssh.exec_command(create_ssh_folder_command)

            for new_key in new_keys:
                command = f"echo '{new_key}' >> ~/.ssh/authorized_keys"
                stdin, stdout, stderr = ssh.exec_command(command)

                if stderr.channel.recv_exit_status() != 0:
                    logging.error("Error occurred while adding public key to authorized_keys.")
                else:
                    logging.info("Public key added to authorized_keys successfully.")

        except paramiko.AuthenticationException:
            logging.error("Authentication failed. Please check your credentials.")
        except paramiko.SSHException as e:
            logging.error(f"SSH connection failed: {e}")

        ssh.close()

    @staticmethod
    def _add_zabbix_metrics(server_address, ssh_username, ssh_password):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh.connect(server_address, username=ssh_username, password=ssh_password)

            configure_command = ("wget -O - https://gist.githubusercontent.com"
                                 "/wensiet/ad357c3fcbb2edd1dc236038c3faf109/raw/"
                                 "30383a561a895696c019def559ce1adf0347f96d/connect_zabbix.sh | bash")
            ssh.exec_command(configure_command)

        except paramiko.AuthenticationException:
            logging.error("Authentication failed. Please check your credentials.")
        except paramiko.SSHException as e:
            logging.error(f"SSH connection failed: {e}")

        ssh.close()

    def _create_compute(self, config: ProvisionConfig):
        logging.info(f"Initialized compute creation with name: {config.name}")
        compute = self.timeweb.create_compute(config.name, self._map_preset(config.flavor),
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

        self._load_new_ssh(ipv4.ip, "root", compute.root_pass, [config.ssh, AppSettings.service_key])

        logging.info("SSH keys added")

        logging.info("Configuring metrics scraping")
        self._add_zabbix_metrics(ipv4.ip, "root", compute.root_pass)
        self.zabbix.connect_host(ipv4.ip, compute.name)
        logging.info("Metrics scraping configured")

        logging.info("+" + "-" * 22 + " Compute Data " + "-" * 22 + "+")
        logging.info("|{:<25} {:<25}|".format("Name:", compute.name))
        logging.info("|{:<25} {:<25}|".format("OS:", compute.os.name))
        logging.info("|{:<25} {:<25}|".format("CPU:", compute.cpu))
        logging.info("|{:<25} {:<25}|".format("RAM:", compute.ram))
        logging.info("|{:<25} {:<25}|".format("IP:", ipv4.ip))
        logging.info("+" + "-" * 55 + "+")

    def _delete_compute(self, uniq: str):
        compute_id = get_id_by_uniq(self.timeweb, uniq)
        logging.info(f"Deleting compute with id: {compute_id}")
        self.timeweb.delete_compute(compute_id)
        logging.info(f"Compute with id: {compute_id} deleted")
        logging.info("Compute deletion finished")
