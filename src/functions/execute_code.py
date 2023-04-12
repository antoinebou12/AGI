import os

import docker


class DockerExecutor:
    def __init__(self, workspace_folder="auto_gpt_workspace"):
        self.workspace_folder = workspace_folder
        self.client = docker.from_env()

    def execute_file(self, file):
        if not file.endswith(".py") and not file.endswith(".rs"):
            return "Error: Invalid file type. Only .py and .rs files are allowed."

        file_path = os.path.join(self.workspace_folder, file)

        if not os.path.isfile(file_path):
            return f"Error: File '{file}' does not exist."

        try:
            if file.endswith(".py"):
                return self.python_container(file)
            elif file.endswith(".rs"):
                return self.rust_container(file)
        except Exception as e:
            return f"Error: {str(e)}"

    def python_container(self, file):
        container = self.client.containers.run(
            "python:3.10",
            f"python {file}",
            volumes={
                os.path.abspath(self.workspace_folder): {
                    "bind": "/workspace",
                    "mode": "ro",
                }
            },
            working_dir="/workspace",
            stderr=True,
            stdout=True,
            detach=True,
        )

        return self.container_logs(container)

    def rust_container(self, file):
        rust_compile = f"rustc {file} -o /workspace/output"
        run_output = "./output"

        container = self.client.containers.run(
            "rust:latest",
            f'/bin/bash -c "{rust_compile} && {run_output}"',
            volumes={
                os.path.abspath(self.workspace_folder): {
                    "bind": "/workspace",
                    "mode": "rw",
                }
            },
            working_dir="/workspace",
            stderr=True,
            stdout=True,
            detach=True,
        )

        return self.container_logs(container)

    def container_logs(self, container):
        logs = container.logs().decode("utf-8")
        container.remove()
        return logs
