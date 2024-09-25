#!/usr/bin/env python3

import subprocess
import sys
import shutil

def check_kubectl():
    if shutil.which('kubectl') is None:
        print("Error: kubectl command not found. Please install kubectl and ensure it's in your PATH.", file=sys.stderr)
        sys.exit(1)
    try:
        subprocess.run(['kubectl', 'version', '--client'], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Error: kubectl command found, but failed to execute. Please check your kubectl installation.", file=sys.stderr)
        sys.exit(1)

def get_contexts():
    try:
        result = subprocess.run(['kubectl', 'config', 'get-contexts', '-o', 'name'],
                                check=True, capture_output=True, text=True)
        return result.stdout.strip().split('\n')
    except subprocess.CalledProcessError as e:
        print(f"Error getting contexts: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def use_context(context):
    try:
        subprocess.run(['kubectl', 'config', 'use-context', context], check=True)
        print(f"Successfully switched to context: {context}")
    except subprocess.CalledProcessError as e:
        print(f"Error switching context: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def get_namespaces():
    try:
        result = subprocess.run(['kubectl', 'get', 'namespaces', '-o', 'jsonpath={.items[*].metadata.name}'],
                                check=True, capture_output=True, text=True)
        return result.stdout.split()
    except subprocess.CalledProcessError as e:
        print(f"Error getting namespaces: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def get_pods(namespace):
    try:
        result = subprocess.run(['kubectl', 'get', 'pods', '-n', namespace, '-o', 'jsonpath={.items[*].metadata.name}'],
                                check=True, capture_output=True, text=True)
        return result.stdout.split()
    except subprocess.CalledProcessError as e:
        print(f"Error getting pods: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def get_containers(namespace, pod):
    try:
        result = subprocess.run(['kubectl', 'get', 'pod', pod, '-n', namespace, '-o', 'jsonpath={.spec.containers[*].name}'],
                                check=True, capture_output=True, text=True)
        return result.stdout.split()
    except subprocess.CalledProcessError as e:
        print(f"Error getting containers: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def select_option(options, prompt, default=None):
    while True:
        print(prompt)
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        if default:
            choice = input(f"Enter your choice (number, default is {default}): ").strip() or str(default)
        else:
            choice = input("Enter your choice (number): ")
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print("Invalid selection. Please try again.")

def main():
    check_kubectl()

    while True:
        action = select_option(['kubectl config use-context', 'kubectl run', 'kubectl debug', 'kubectl exec', 'Exit'],
                               "Select an action:")

        if action == 'Exit':
            print("Exiting the wizard. Goodbye!")
            break

        if action == 'kubectl config use-context':
            contexts = get_contexts()
            selected_context = select_option(contexts, "Select a Kubernetes context:")
            use_context(selected_context)
            continue

        # Select k8s namespace
        namespaces = get_namespaces()
        namespace = select_option(namespaces, "Select a Kubernetes namespace:")

        if action == 'kubectl run':
            container_name = input("Enter a container name (default: debian-container): ").strip() or 'debian-container'
            command = [
                'kubectl', 'run', container_name,
                '--image=debian:bookworm', '--restart=Never',
                '-n', namespace,
                '--', 'sleep', 'infinity'
            ]
        elif action == 'kubectl debug' or action == 'kubectl exec':
            pods = get_pods(namespace)
            pod = select_option(pods, "Select a Pod:")
            containers = get_containers(namespace, pod)
            container = select_option(containers, "Select a container:", default=1)

            if action == 'kubectl debug':
                command = [
                    'kubectl', 'debug', pod,
                    '-it',
                    '-n', namespace,
                    '--image=debian:bookworm',
                    '--container', container,
                    '--', '/bin/bash'
                ]
            else:  # kubectl exec
                command = [
                    'kubectl', 'exec', '-it',
                    '-n', namespace,
                    pod,
                    '-c', container,
                    '--', '/bin/bash'
                ]
        else:
            print(f"Unsupported action: {action}", file=sys.stderr)
            continue

        print("Command to execute:")
        print(' '.join(command))

        confirm = input("Do you want to execute this command? (y/n): ")

        if confirm.lower() == 'y':
            try:
                result = subprocess.run(command)
                if result.returncode == 0:
                    print("Command executed successfully.")
                else:
                    print(f"Command exited with return code {result.returncode}")
            except subprocess.CalledProcessError as e:
                print(f"An error occurred while executing the command: {e}", file=sys.stderr)
        else:
            print("Command execution cancelled.")

if __name__ == "__main__":
    main()
