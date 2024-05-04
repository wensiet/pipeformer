# Pipeformer

## How to create compute?

1) Fork the repository
2) Create new directory in `compute`, created directory will be your project name
3) Create `.yaml` file with the name of your compute
4) Fill the `.yaml` file according to your needs, follow this example, verify that
your preset is listed in [Flavors](#flavors)
    ```yaml
   ssh: your-public-key
   
   flavor:
     operating_system: ubuntu_22_04
     disk_space: 15GB
     cpu_cores: 1
     RAM: 1GB
     region: SPB-1
   
   playbooks:
     - name: playbook1
       link: http://google.com
       vars: [ ]
     - name: playbook2
       link: http://google.com
       vars: [ ]
   ```
5) Create merge request to the `main` branch of the parent repository and wait for approval
6) After approve you will see the pipeline, that will create the compute
7) After the pipeline is finished, you will see your compute information in pipelien logs

## How to delete compute?

1) Fork the repository
2) Delete corresponding `.yaml` file
3) Create merge request to the main repository and wait for approval

## Flavors

### Software configurations

| OS           |
|--------------| 
| ubuntu_22_04 |
| centos_7     |
| centos_8     | 
| ubuntu_18_04 | 
| ubuntu_20_04 | 
| ubuntu_22_04 |
| debian_10    |
| debian_11    |

### Hardware configurations

| CPU | RAM | Disk | Region        |
|-----|-----|------|---------------|
| 1   | 1GB | 15GB | SPB-1 / MSK-1 |
| 1   | 2GB | 30GB | SPB-1 / MSK-1 |
| 2   | 2GB | 40GB | SPB-1 / MSK-1 |
| 2   | 4GB | 50GB | SPB-1 / MSK-1 |
| 4   | 8GB | 80GB | SPB-1 / MSK-1 |


# Development

## Setting up interpreter

1. Install Python 3.12 or later
2. Install Poetry
3. Run `poetry install` in the root directory of the project
4. Run `poetry shell` to activate the virtual environment

