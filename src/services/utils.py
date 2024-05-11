import logging
import subprocess
import urllib.parse

import paramiko

from src.services.validation.dto import Flavor


def extract_compute_name(path: str):
    paths = path.replace(".yaml", "").replace(".yml", "").split("/")
    if "compute" in paths:
        paths.remove("compute")
    res = ""
    for p in paths:
        res += p + "-"
    res = res.rstrip("-")
    return res


def get_id_by_uniq(timeweb, uniq: str):
    computes = timeweb.list_computes()
    for compute in computes:
        if compute.name == uniq:
            return compute.id
    raise ValueError(f"Compute with name {uniq} not found")


def add_to_known_hosts(ip):
    command = [
        'ssh-keyscan', '-H', ip
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    process.wait()

    if process.returncode == 0:
        logging.info(f"IP {ip} added to known_hosts")
    else:
        logging.error(f"Failed to add IP {ip} to known_hosts")
        logging.error("STDERR:\n", process.stderr.read())


def add_zabbix_metrics(server_address, ssh_username, ssh_password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(server_address, username=ssh_username, password=ssh_password)

        configure_command = ("wget -O - https://gist.githubusercontent.com"
                             "/wensiet/ad357c3fcbb2edd1dc236038c3faf109/raw/"
                             "30383a561a895696c019def559ce1adf0347f96d/connect_zabbix.sh | bash")
        stdin, stdout, stderr = ssh.exec_command(configure_command)
        if stderr.channel.recv_exit_status() != 0:
            logging.error("Error occurred while adding zabbix metrics.")
        else:
            logging.info("Zabbix metrics reconfigured.")
    except paramiko.AuthenticationException:
        logging.error("Authentication failed. Please check your credentials.")
    except paramiko.SSHException as e:
        logging.error(f"SSH connection failed: {e}")

    ssh.close()


def url_encode(data: str):
    url_encoded = urllib.parse.quote(data)
    return url_encoded


def map_preset(preset: Flavor):
    preset_str = (f"c{preset.cpu_cores}r{preset.RAM.replace('GB', '')}"
                  f"d{preset.disk_space.replace('GB', '')}")
    return preset_str


def load_new_ssh(server_address, ssh_username, ssh_password, new_keys):
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
