"""CLI interface for Chorus."""

import os

import click
import questionary
import yaml
from rich.console import Console

from .config import add_agent, get_chorus_directory, load_config


@click.group()
@click.pass_context
def main(ctx):
    """Chorus - Manage multiple copies of multiple repos being edited by coding agents in parallel."""
    ctx.obj = load_config()


@main.command(name="list-repos")
@click.pass_context
def list_repos(ctx):
    """Lists all repos that have at least one workspace checked out."""
    config = ctx.obj
    chorus_dir = get_chorus_directory(config)
    if not os.path.exists(chorus_dir):
        click.echo(f"Chorus storage directory ({chorus_dir}) does not exist.")
        return
    repos = [
        d for d in os.listdir(chorus_dir) if os.path.isdir(os.path.join(chorus_dir, d))
    ]
    if not repos:
        click.echo(f"No repos found in {chorus_dir}.")
        return
    for repo in repos:
        click.echo(repo)


@main.command(name="list-workspaces")
@click.pass_context
@click.argument("repo_name")
def list_workspaces(ctx, repo_name):
    """Lists all workspaces for a given repo."""
    config = ctx.obj
    chorus_dir = get_chorus_directory(config)
    repo_dir = os.path.join(chorus_dir, repo_name)
    if not os.path.exists(repo_dir):
        click.echo(f"Repo '{repo_name}' not found in {chorus_dir}.")
        return
    workspaces = [
        d for d in os.listdir(repo_dir) if os.path.isdir(os.path.join(repo_dir, d))
    ]
    if not workspaces:
        click.echo(f"No workspaces found for repo '{repo_name}'.")
        return
    for workspace in workspaces:
        click.echo(workspace)


@main.command(name="add-repo")
@click.pass_context
@click.argument("git_url")
def add_repo(ctx, git_url):
    """Adds a new repo to chorus."""
    config = ctx.obj
    chorus_dir = get_chorus_directory(config)
    repo_name = git_url.split("/")[-1].replace(".git", "")
    repo_dir = os.path.join(chorus_dir, repo_name)

    if not os.path.exists(chorus_dir):
        os.makedirs(chorus_dir)

    if os.path.exists(repo_dir):
        click.echo(f"Repo '{repo_name}' already exists.")
        return

    os.makedirs(repo_dir)
    with open(os.path.join(repo_dir, "chorus.yaml"), "w") as f:
        f.write(f"url: {git_url}\n")

    click.echo(f"Repo '{repo_name}' added successfully.")


@main.command(name="add-workspace")
@click.pass_context
@click.argument("repo_name")
@click.argument("workspace_name")
def add_workspace(ctx, repo_name, workspace_name):
    """Creates a new workspace for a repo and clones the repo into it."""
    config = ctx.obj
    chorus_dir = get_chorus_directory(config)
    repo_dir = os.path.join(chorus_dir, repo_name)
    workspace_dir = os.path.join(repo_dir, workspace_name)

    if not os.path.exists(repo_dir):
        click.echo(f"Repo '{repo_name}' not found.")
        return

    if os.path.exists(workspace_dir):
        click.echo(
            f"Workspace '{workspace_name}' already exists for repo '{repo_name}'."
        )
        return

    with open(os.path.join(repo_dir, "chorus.yaml"), "r") as f:
        repo_config = yaml.safe_load(f)
        git_url = repo_config.get("url")

    if not git_url:
        click.echo("Git URL not found in chorus.yaml.")
        return

    os.makedirs(workspace_dir)

    clone_command = f"git clone {git_url} {os.path.join(workspace_dir, repo_name)}"
    os.system(clone_command)

    click.echo(
        f"Workspace '{workspace_name}' created for repo '{repo_name}' and repo cloned successfully."
    )


@main.command()
@click.pass_context
def connect(ctx):
    """Connect to a workspace."""
    config = ctx.obj
    chorus_dir = get_chorus_directory(config)
    console = Console()
    console.print("[bold magenta]Connect to a Chorus Workspace[/bold magenta]")

    if not os.path.exists(chorus_dir):
        console.print(f"[red]Chorus storage directory ({chorus_dir}) does not exist.[/red]")
        return

    repos = [
        d for d in os.listdir(chorus_dir) if os.path.isdir(os.path.join(chorus_dir, d))
    ]
    if not repos:
        console.print(f"[yellow]No repos found in {chorus_dir}.[/yellow]")
        return

    repo_name = questionary.select("Please choose a repo:", choices=repos).ask()

    if not repo_name:
        return

    repo_dir = os.path.join(chorus_dir, repo_name)
    workspaces = [
        d for d in os.listdir(repo_dir) if os.path.isdir(os.path.join(repo_dir, d))
    ]
    if not workspaces:
        console.print(f"[yellow]No workspaces found for repo '{repo_name}'.[/yellow]")
        return

    workspace_name = questionary.select(
        "Please choose a workspace:", choices=workspaces
    ).ask()

    if not workspace_name:
        return

    agents = config.get("agents", [])
    if not agents:
        console.print("[yellow]No agents configured. Please add an agent using 'chorus add-agent'.[/yellow]")
        return

    agent_name = questionary.select("Please choose an agent:", choices=agents).ask()

    if not agent_name:
        return

    workspace_path = os.path.join(repo_dir, workspace_name)
    git_repo_root = os.path.join(workspace_path, repo_name)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    layout_path = os.path.join(project_root, "zellij", "layout.kdl")

    console.print(f"Connecting to [cyan]{repo_name}/{workspace_name}[/cyan]...")

    os.chdir(workspace_path)
    
    # Create a temporary layout file with the git repo root substituted
    import tempfile
    with open(layout_path, 'r') as f:
        layout_content = f.read()
    
    layout_content = layout_content.replace('{git_repo_root}', git_repo_root)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.kdl', delete=False) as temp_layout:
        temp_layout.write(layout_content)
        temp_layout_path = temp_layout.name
    
    try:
        os.system(f"CHORUS_COMMAND='{agent_name}' zellij --layout {temp_layout_path}")
    finally:
        os.unlink(temp_layout_path)


@main.command(name="config")
@click.pass_context
def show_config(ctx):
    """Shows the loaded configuration."""
    config = ctx.obj
    click.echo(yaml.dump(config))


@main.command(name="add-agent")
@click.argument("agent_name")
@click.pass_context
def add_agent_command(ctx, agent_name):
    """Adds a new agent to the chorus configuration."""
    if add_agent(agent_name):
        click.echo(f"Agent '{agent_name}' added successfully.")
    else:
        click.echo(f"Agent '{agent_name}' already exists.")


if __name__ == "__main__":
    main()
