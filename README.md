# Kubectl Wizard

Kubectl Wizard is a Python-based interactive CLI tool designed to simplify common kubectl operations. It provides a user-friendly interface for executing kubectl commands, making it easier for interact with Kubernetes clusters.

## Features

- Interactive menu for selecting kubectl actions
- Support for switching between Kubernetes contexts
- Simplified execution of `kubectl run`, `kubectl debug`, and `kubectl exec` commands
- Namespace selection for all operations
- Pod selection for debug and exec operations
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
3. `kubectl debug`: Debug an existing pod by creating a new debug container.
4. `kubectl exec`: Execute a command (default: bash shell) in an existing pod.

## Workflow

1. Select an action from the main menu.
2. If switching context, select the desired context from the list.
3. For other actions, select the namespace and (if applicable) the target pod.
4. Review and confirm the command before execution.
5. View the execution results.
6. Return to the main menu to perform another action or exit.

## License

This project is licensed under the MIT License - see the [LICENSE](https://opensource.org/license/mit) for details.
