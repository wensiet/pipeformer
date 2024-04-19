import logging
import time

import yaml

from src.integrations.timeweb.wrapper import TimewebWrapper

logging.basicConfig(level=logging.INFO)

# TODO detect changes (unhardcode)
logging.info("Started provisioning...")
changed_file = "compute/some-project/awesome-compute-instance.yaml"
wrapper = TimewebWrapper()
data = yaml.safe_load(open(changed_file))
logging.info(f"Data loaded from {changed_file}")
key = wrapper.create_ssh_key(changed_file, data["ssh_key"])
logging.info(f"SSH key created: {key}")
compute = wrapper.create_compute(data["name"], data["preset"], data["os"], [key])
logging.info(f"Compute created: {compute}")

logging.info("Waiting the compute to be ready...")
while compute.status != "on":
    compute = wrapper.get_compute(compute.id)
    time.sleep(30)
    logging.info(f"Compute status: {compute.status}")

logging.info("Compute is ready!")

logging.info("Executing custom scripts...")

logging.info("Custom scripts execution finished!")

ipv4 = None
for network in compute.networks:
    if network.type == "ipv4":
        ipv4 = network
        break
logging.info("Provisioning finished, your SSH key may be not available yet.")
logging.info(f" ----- Compute data ----- ")
logging.info(f" - Name: {compute.name}")
logging.info(f" - OS: {compute.os.name}")
logging.info(f" - CPU: {compute.cpu}")
logging.info(f" - RAM: {compute.ram}")
logging.info(f" - IP: {ipv4.ips[0]}")
logging.info(f" ------------------------ ")
