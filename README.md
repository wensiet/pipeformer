# Pipeformer

## How to create compute?
1) Fork the repository
2) Create new directory in `compute`, created directory will be your project
3) Create `.yaml` file with the name of your compute
4) Fill the `.yaml` file according to your needs, following this example
    ```yaml
    ssh: your-public-key
    flavor:
        operating_system: linux
        disk_space: 50GB
        cpu_cores: 2
        RAM: 4GB
        region: AMS-1
    playbooks:
        - name: playbook1
          link: http://google.com
          vars: []
        - name: playbook2
          link: http://google.com
          vars: [ ]
    ```
5) Create merge request to the main repository and wait for approval
6) After approve you will see the pipeline, that will create the compute
7) After the pipeline is finished, you will see your compute information in pipelien logs

## How to delete compute?
1) Fork the repository
2) Delete corresponding `.yaml` file
3) Create merge request to the main repository and wait for approval

# Development

## Setting up interpreter

1. Install Python 3.12 or later
2. Install Poetry
3. Run `poetry install` in the root directory of the project
4. Run `poetry shell` to activate the virtual environment

