# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Chorus is a Python CLI tool that manages multiple copies of multiple repositories being edited by coding agents in parallel. It provides workspace management for coding agents to work on different copies of the same repository simultaneously.

## Architecture

- **Package structure**: Single Python package at `src/chorus/` with CLI module at `src/chorus/cli.py`
- **CLI entry point**: Configured in `pyproject.toml` as `chorus = "chorus.cli:main"`
- **Configuration**: Uses YAML config at `~/.config/chorus.yaml` with defaults in `cli.py:DEFAULT_CONFIG`
- **Storage**: Manages repositories and workspaces in `~/.chorus/` directory by default
- **Agent integration**: Works with Zellij terminal multiplexer using layout at `zellij/layout.kdl`

## Development Commands

This project uses `uv` for dependency management:

- **Run commands**: `uv run <command>` - Execute commands in the project environment
- **Install dependencies**: `uv add <package>` - Add new dependencies
- **Remove dependencies**: `uv remove <package>` - Remove dependencies
- **Run the CLI**: `uv run chorus <command>` - Run chorus CLI commands locally

## CLI Commands

- `chorus list-repos` - List all repositories with workspaces
- `chorus list-workspaces <repo_name>` - List workspaces for a repo  
- `chorus add-repo <git_url>` - Add a new repository to chorus
- `chorus add-workspace <repo_name> <workspace_name>` - Create new workspace and clone repo
- `chorus connect` - Interactive workspace connection via Zellij
- `chorus config` - Show current configuration
- `chorus add-agent <agent_name>` - Add agent to configuration

## Key Implementation Details

- Configuration merges user config with `DEFAULT_CONFIG` in `cli.py:27`
- Workspace creation clones repos into `~/.chorus/<repo_name>/<workspace_name>/`
- Each repo directory contains a `chorus.yaml` with the git URL
- Agent commands are passed to Zellij via `CHORUS_COMMAND` environment variable
- The `connect` command uses Zellij layout from `zellij/layout.kdl:3` for multi-pane development

## Known Issues

- Line 132 in `cli.py` has a typo: `clone_.command` should be `clone_command`