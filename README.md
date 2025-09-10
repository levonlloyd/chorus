# Chorus

A script to manage multiple copies of multiple repos being edited by coding agents in parallel.

## Installation

(TODO)

## Usage

Chorus provides a command-line interface for managing repositories and workspaces.

### List Repositories

To list all repositories that have at least one workspace checked out, run:

```bash
chorus list-repos
```

### List Workspaces

To list all workspaces for a given repository, run:

```bash
chorus list-workspaces <repo_name>
```

## For Coding Agents

For information on how to write a coding agent that can use Chorus, see `AGENTS.md`.
