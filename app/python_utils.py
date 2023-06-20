import logging

from kubernetes import client, config
from kubernetes.stream import stream


logger = logging.getLogger(__name__)


def delete_config_file(
    config_name: str,
    cloud_namespace: str,
) -> None:
    """Deletes config file from some kubernetes pod

    Parameters
    ----------
    config_name
        config file name
    cloud_namespace
        Identifier depends on branch

    """
    config.load_incluster_config()
    api_instance = client.CoreV1Api()
    label_selector = "some_label"
    pods = api_instance.list_namespaced_pod(
        namespace="kube-services", label_selector=label_selector
    )
    for i in pods.items:
        pod = i.metadata.name
    exec_command = ["/bin/sh"]
    resp = stream(
        api_instance.connect_get_namespaced_pod_exec,
        pod,
        "kube-services",
        command=exec_command,
        stderr=True,
        stdin=True,
        stdout=True,
        tty=False,
        _preload_content=False,
    )
    destination_file = f"opt/{config_name}.py"
    commands = []
    commands.append("rm " + destination_file)
    while resp.is_open():
        resp.update(timeout=1)
        if resp.peek_stdout():
            logging.info("STDOUT: %s" % resp.read_stdout())
        if resp.peek_stderr():
            logging.error("STDERR: %s" % resp.read_stderr())
        if commands:
            c = commands.pop(0)
            resp.write_stdin(c)
        else:
            break

    resp.close()


def copy_config_file(
    config_name: str,
    config_file_content: str,
    cloud_namespace: str,
) -> None:
    """kubectl cp implementation for copy config file from stream to kubernetes pod

    Parameters
    ----------
    config_name
        config file name
    config_file_content
        Content of the config file to upload
    cloud_namespace
        Identifier depends on branch
    """
    config.load_incluster_config()
    api_instance = client.CoreV1Api()
    label_selector = "label"
    pods = api_instance.list_namespaced_pod(
        namespace="kube-services", label_selector=label_selector
    )
    for i in pods.items:
        pod = i.metadata.name
    exec_command = ["/bin/sh"]
    resp = stream(
        api_instance.connect_get_namespaced_pod_exec,
        pod,
        "kube-services",
        command=exec_command,
        stderr=True,
        stdin=True,
        stdout=True,
        tty=False,
        _preload_content=False,
    )

    destination_file = f"{config_name}.py"
    commands = []
    commands.append("cat <<'EOF' >" + destination_file + "\n")
    commands.append(config_file_content)
    while resp.is_open():
        resp.update(timeout=1)
        if resp.peek_stdout():
            logging.info("STDOUT: %s" % resp.read_stdout())
        if resp.peek_stderr():
            logging.error("STDERR: %s" % resp.read_stderr())
        if commands:
            c = commands.pop(0)
            resp.write_stdin(c)
        else:
            break

    resp.close()
