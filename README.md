# kubectl-wizard

`kubectl-wizard` is a Python-based interactive CLI tool designed to simplify common kubectl operations. It provides a user-friendly interface for executing kubectl commands, making it easier to interact with Kubernetes clusters.

## Features

- Interactive menu for selecting kubectl actions
- Support for switching between Kubernetes contexts
- Simplified execution of `kubectl run`, `kubectl debug`, `kubectl exec`, and `kubectl port-forward` commands
- Namespace selection for all operations
- Pod selection for debug and exec operations
- Container selection for debug and exec operations
- Service and port selection for port-forward operations
- Confirmation prompts before executing commands

## Requirements

- Python 3.6+
- kubectl installed and configured on your system

## Usage

Run the script from the command line:

```
$ ./kubectl-wizard.py
```

Follow the interactive prompts to select and execute kubectl commands.

## Supported Commands

1. `kubectl config use-context`: Switch between available Kubernetes contexts.
2. `kubectl run`: Create and run a new pod with a Debian container.
3. `kubectl debug`: Debug an existing pod by creating a new debug container or attaching to an existing container.
4. `kubectl exec`: Execute a command in an existing container within a pod. The default command is `/bin/bash`, but users can specify any command.
5. `kubectl port-forward`: Forward local ports to a Kubernetes service. Services and ports are listed interactively. If the service has a single port, it is selected automatically. For services with multiple ports, select ports by number (comma-separated) or enter `all`.

## Workflow

1. Select an action from the main menu.
2. If switching context, select the desired context from the list.
3. For other actions:
   - Select the namespace
   - Select the target pod (for debug and exec operations)
   - Select the target container (for debug and exec operations)
   - Select the target service and ports (for port-forward operations)
   - For exec operations, optionally specify a command to run (default is `/bin/bash`)
4. Review and confirm the command before execution.
5. View the execution results.
6. Return to the main menu to perform another action or exit.

## License

This project is licensed under the [MIT License](./LICENSE).
