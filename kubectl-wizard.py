#!/usr/bin/env python3

import json
import subprocess
import sys
import shutil


def check_kubectl():
    if shutil.which("kubectl") is None:
        print(
            "Error: kubectl command not found. Please install kubectl and ensure it's in your PATH.",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        subprocess.run(
            ["kubectl", "version", "--client"], check=True, capture_output=True
        )
    except subprocess.CalledProcessError:
        print(
            "Error: kubectl command found, but failed to execute. Please check your kubectl installation.",
            file=sys.stderr,
        )
        sys.exit(1)


def get_contexts():
    try:
        result = subprocess.run(
            ["kubectl", "config", "get-contexts", "-o", "name"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip().split("\n")
    except subprocess.CalledProcessError as e:
        print(f"Error getting contexts: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def get_namespaces():
    try:
        result = subprocess.run(
            [
                "kubectl",
                "get",
                "namespaces",
                "-o",
                "jsonpath={.items[*].metadata.name}",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.split()
    except subprocess.CalledProcessError as e:
        print(f"Error getting namespaces: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def get_pods(namespace):
    try:
        result = subprocess.run(
            [
                "kubectl",
                "get",
                "pods",
                "-n",
                namespace,
                "-o",
                "jsonpath={.items[*].metadata.name}",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.split()
    except subprocess.CalledProcessError as e:
        print(f"Error getting pods: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def get_containers(namespace, pod):
    try:
        result = subprocess.run(
            [
                "kubectl",
                "get",
                "pod",
                pod,
                "-n",
                namespace,
                "-o",
                "jsonpath={.spec.containers[*].name}",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.split()
    except subprocess.CalledProcessError as e:
        print(f"Error getting containers: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def get_services(namespace):
    try:
        result = subprocess.run(
            ["kubectl", "get", "svc", "-n", namespace, "-o", "json"],
            check=True,
            capture_output=True,
            text=True,
        )
        data = json.loads(result.stdout)
        services = []
        for item in data.get("items", []):
            ports = [p["port"] for p in item["spec"].get("ports", [])]
            services.append(
                {
                    "name": item["metadata"]["name"],
                    "ports": ports,
                }
            )
        return services
    except subprocess.CalledProcessError as e:
        print(f"Error getting services: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def select_option(options, prompt, default=None):
    while True:
        print(prompt)
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        if default:
            choice = input(
                f"Enter your choice (number, default is {default}): "
            ).strip() or str(default)
        else:
            choice = input("Enter your choice (number): ")
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print("Invalid selection. Please try again.")


def select_service(services):
    print("* service:")
    for i, svc in enumerate(services, 1):
        ports_str = " , ".join(str(p) for p in svc["ports"])
        print(f"  {i}. {svc['name']} ( port {ports_str} )")

    while True:
        choice = input("Enter the number: ")
        if choice.isdigit() and 1 <= int(choice) <= len(services):
            return services[int(choice) - 1]
        print("Invalid selection. Please try again.")


def select_ports(service):
    ports = service["ports"]

    if len(ports) == 1:
        return ports

    print(f"* {service['name']}:")
    for i, port in enumerate(ports, 1):
        print(f"  {i}. {port}")

    while True:
        choice = input(
            "Enter the numbers (comma-separated) or 'all' for all ports: "
        ).strip()
        if choice == "all":
            return ports

        selected = []
        valid = True
        for s in choice.split(","):
            s = s.strip()
            if s.isdigit() and 1 <= int(s) <= len(ports):
                selected.append(ports[int(s) - 1])
            else:
                print(f"Invalid selection: {s}")
                valid = False
                break

        if valid and selected:
            return selected
        print("Please try again.")


def build_use_context(_namespace):
    contexts = get_contexts()
    selected_context = select_option(contexts, "Select a Kubernetes context:")
    try:
        subprocess.run(
            ["kubectl", "config", "use-context", selected_context], check=True
        )
        print(f"Successfully switched to context: {selected_context}")
    except subprocess.CalledProcessError as e:
        print(f"Error switching context: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    return None


def build_run(namespace):
    container_name = (
        input("Enter a container name (default: debian-container): ").strip()
        or "debian-container"
    )
    return [
        "kubectl",
        "run",
        container_name,
        "--image=debian:trixie",
        "--restart=Never",
        "-n",
        namespace,
        "--",
        "sleep",
        "infinity",
    ]


def build_debug(namespace):
    pods = get_pods(namespace)
    pod = select_option(pods, "Select a Pod:")
    containers = get_containers(namespace, pod)
    container = select_option(containers, "Select a container:", default=1)
    return [
        "kubectl",
        "debug",
        pod,
        "-it",
        "-n",
        namespace,
        "--image=debian:bookworm",
        "--container",
        container,
        "--",
        "/bin/bash",
    ]


def build_exec(namespace):
    pods = get_pods(namespace)
    pod = select_option(pods, "Select a Pod:")
    containers = get_containers(namespace, pod)
    container = select_option(containers, "Select a container:", default=1)
    default_command = "/bin/bash"
    user_command = (
        input(f"Enter the command to execute (default: {default_command}): ").strip()
        or default_command
    )
    return [
        "kubectl",
        "exec",
        "-it",
        "-n",
        namespace,
        pod,
        "-c",
        container,
        "--",
    ] + user_command.split()


def build_port_forward(namespace):
    services = get_services(namespace)
    if not services:
        print(f"No services found in namespace {namespace}")
        return None

    service = select_service(services)
    selected_ports = select_ports(service)
    port_args = [f"{p}:{p}" for p in selected_ports]
    return [
        "kubectl",
        "port-forward",
        f"service/{service['name']}",
        "-n",
        namespace,
    ] + port_args


ACTIONS = {
    "kubectl config use-context": {
        "needs_namespace": False,
        "build": build_use_context,
    },
    "kubectl run": {"needs_namespace": True, "build": build_run},
    "kubectl debug": {"needs_namespace": True, "build": build_debug},
    "kubectl exec": {"needs_namespace": True, "build": build_exec},
    "kubectl port-forward": {"needs_namespace": True, "build": build_port_forward},
}


def confirm_and_execute(command):
    print("Command to execute:")
    print(" ".join(command))

    confirm = input("Do you want to execute this command? (y/n): ")
    if confirm.lower() != "y":
        print("Command execution cancelled.")
        return

    try:
        result = subprocess.run(command)
        if result.returncode == 0:
            print("Command executed successfully.")
        else:
            print(f"Command exited with return code {result.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the command: {e}", file=sys.stderr)


def main():
    check_kubectl()

    action_names = list(ACTIONS.keys()) + ["Exit"]

    while True:
        action = select_option(action_names, "Select an action:")

        if action == "Exit":
            print("Exiting the wizard. Goodbye!")
            break

        entry = ACTIONS[action]
        namespace = None
        if entry["needs_namespace"]:
            namespaces = get_namespaces()
            namespace = select_option(namespaces, "Select a Kubernetes namespace:")

        command = entry["build"](namespace)

        if command is not None:
            confirm_and_execute(command)


if __name__ == "__main__":
    main()
