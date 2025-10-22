#!/usr/bin/env python3
"""
Main CLI Application for AI-Powered Media Library Organizer

This is the main entry point for the media library organization tool that uses
Google Gemini AI to intelligently organize movies and TV shows.
"""

import os
import sys
import click
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from tree_generator import TreeGenerator
from ai_organizer import AIOrganizer
from file_operations import FileOperations


# Load environment variables
load_dotenv()

# Initialize Rich console
console = Console()


class MediaOrganizerCLI:
    """Main CLI application class."""

    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.movies_path = os.getenv('MOVIES_PATH')
        self.tv_shows_path = os.getenv('TV_SHOWS_PATH')
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
        self.backup_enabled = os.getenv('BACKUP_ENABLED', 'true').lower() == 'true'
        self.gemini_model = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')

    def validate_setup(self) -> bool:
        """Validate that all required configuration is present."""
        if not self.api_key:
            console.print("❌ GEMINI_API_KEY not found in environment variables", style="red")
            console.print("Please set your Gemini API key in .env file", style="yellow")
            return False

        return True

    def test_ai_connection(self) -> bool:
        """Test connection to Gemini AI."""
        try:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task("Testing AI connection...", total=None)

                organizer = AIOrganizer(self.api_key, self.gemini_model)
                result = organizer.test_connection()

                progress.update(task, completed=True)

            if result:
                console.print("✅ AI connection successful", style="green")
                return True
            else:
                console.print("❌ AI connection failed", style="red")
                return False

        except Exception as e:
            console.print(f"❌ AI connection error: {str(e)}", style="red")
            return False


@click.group()
@click.option('--dry-run/--no-dry-run', default=True, help='Simulate operations without making changes')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, dry_run, verbose):
    """AI-Powered Media Library Organizer

    Organize your movie and TV show collections using Google Gemini AI.
    The AI analyzes your directory structure and suggests optimal organization.
    """
    ctx.ensure_object(dict)
    ctx.obj['dry_run'] = dry_run
    ctx.obj['verbose'] = verbose

    app = MediaOrganizerCLI()
    ctx.obj['app'] = app


@cli.command()
@click.pass_context
def setup(ctx):
    """Set up the media organizer with API key and paths."""
    console.print(Panel("🚀 Media Organizer Setup", style="blue"))

    # Check for existing .env file
    env_file = Path('.env')
    if env_file.exists():
        console.print("Found existing .env file", style="green")
        if not Confirm.ask("Do you want to update the configuration?"):
            return

    # Get API key
    api_key = Prompt.ask("Enter your Google Gemini API key", password=True)

    # Get media paths
    movies_path = Prompt.ask("Enter path to your movies directory", default="")
    tv_shows_path = Prompt.ask("Enter path to your TV shows directory", default="")

    # Write .env file
    env_content = f"""# Google Gemini API Configuration
GEMINI_API_KEY={api_key}

# Media Library Paths
MOVIES_PATH={movies_path}
TV_SHOWS_PATH={tv_shows_path}

# Organization Settings
DRY_RUN=true
BACKUP_ENABLED=true
LOG_LEVEL=INFO

# AI Model Configuration
GEMINI_MODEL=gemini-1.5-flash-latest
MAX_TOKENS=8192
TEMPERATURE=0.1

# File Operation Settings
MOVE_FILES=true
CREATE_SYMLINKS=false
PRESERVE_ORIGINAL_STRUCTURE=false
"""

    with open('.env', 'w') as f:
        f.write(env_content)

    console.print("✅ Configuration saved to .env file", style="green")
    console.print("You can now use the organizer commands", style="blue")


@cli.command()
@click.pass_context
def test(ctx):
    """Test the AI connection and configuration."""
    app = ctx.obj['app']

    console.print(Panel("🧪 Testing Configuration", style="blue"))

    if not app.validate_setup():
        sys.exit(1)

    if not app.test_ai_connection():
        sys.exit(1)

    console.print("✅ All tests passed! Ready to organize media.", style="green")


@cli.command()
@click.argument('path')
@click.option('--max-depth', default=3, help='Maximum directory depth to scan')
@click.pass_context
def scan(ctx, path, max_depth):
    """Scan and display directory structure for a given path."""
    console.print(f"📁 Scanning directory: {path}")

    try:
        generator = TreeGenerator(path)
        tree = generator.generate_tree(max_depth=max_depth)

        console.print("\n" + "="*60)
        console.print(generator.tree_to_text(tree))
        console.print("="*60)

        # Show analysis
        analysis = generator.analyze_media_content(tree)

        table = Table(title="Media Analysis")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        for key, value in analysis.items():
            if key == 'total_size' or key == 'video_size':
                value_mb = value / (1024 * 1024)
                value = f"{value_mb:.1f} MB"
            table.add_row(key.replace('_', ' ').title(), str(value))

        console.print(table)

    except Exception as e:
        console.print(f"❌ Error scanning directory: {str(e)}", style="red")
        sys.exit(1)


@cli.command()
@click.argument('path')
@click.option('--show-name', help='Specific show folder to organize')
@click.pass_context
def organize_show(ctx, path, show_name):
    """Organize a TV show directory using AI suggestions."""
    app = ctx.obj['app']
    dry_run = ctx.obj['dry_run']

    if not app.validate_setup():
        sys.exit(1)

    console.print(f"📺 Organizing TV show{'s' if not show_name else f': {show_name}'}")

    try:
        generator = TreeGenerator(path)

        if show_name:
            # Organize specific show
            shows_to_process = [show_name]
        else:
            # List all shows and let user choose
            folders = generator.get_folder_list()
            if not folders:
                console.print("No folders found in the specified path", style="yellow")
                return

            table = Table(title="Available TV Shows")
            table.add_column("#", style="cyan")
            table.add_column("Show Name", style="green")

            for i, folder in enumerate(folders[:20], 1):  # Show first 20
                table.add_row(str(i), folder)

            console.print(table)

            if len(folders) > 20:
                console.print(f"... and {len(folders) - 20} more shows")

            choice = Prompt.ask("Enter show number to organize (or 'all' for batch processing)")

            if choice.lower() == 'all':
                if not Confirm.ask("This will process all shows. Continue?"):
                    return
                shows_to_process = folders
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(folders):
                        shows_to_process = [folders[idx]]
                    else:
                        console.print("Invalid selection", style="red")
                        return
                except ValueError:
                    console.print("Invalid input", style="red")
                    return

        # Process selected shows
        organizer = AIOrganizer(app.api_key, app.gemini_model)
        file_ops = FileOperations(path, dry_run=dry_run, backup_enabled=app.backup_enabled)

        for show in shows_to_process:
            console.print(f"\n🎬 Processing: {show}")

            # Generate tree for this show
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task("Generating directory tree...", total=None)
                show_tree = generator.generate_single_folder_tree(show)
                progress.update(task, completed=True)

            if not show_tree:
                console.print(f"❌ Could not access folder: {show}", style="red")
                continue

            tree_text = generator.tree_to_text(show_tree)

            # Get AI suggestions
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task("Getting AI organization suggestions...", total=None)
                plan = organizer.organize_tv_show(tree_text, show)
                progress.update(task, completed=True)

            # Show preview
            console.print(Panel(file_ops.preview_plan(plan), title=f"Organization Plan: {show}"))

            if plan.warnings:
                console.print("⚠️  Warnings detected:", style="yellow")
                for warning in plan.warnings:
                    console.print(f"  • {warning}", style="yellow")

            # Ask for confirmation
            if not dry_run:
                if not Confirm.ask(f"Execute organization plan for {show}?"):
                    console.print("Skipped", style="yellow")
                    continue

            # Execute plan
            report = file_ops.execute_plan(plan, f"TV Show: {show}")

            # Show results
            console.print(f"\n📊 Results for {show}:")
            console.print(f"  ✅ Successful operations: {report.successful_operations}")
            console.print(f"  ❌ Failed operations: {report.failed_operations}")
            if report.total_bytes_moved > 0:
                mb_moved = report.total_bytes_moved / (1024 * 1024)
                console.print(f"  📦 Data moved: {mb_moved:.1f} MB")

    except Exception as e:
        console.print(f"❌ Error organizing shows: {str(e)}", style="red")
        sys.exit(1)


@cli.command()
@click.argument('path')
@click.pass_context
def organize_movies(ctx, path):
    """Organize movie directory using AI suggestions."""
    app = ctx.obj['app']
    dry_run = ctx.obj['dry_run']

    if not app.validate_setup():
        sys.exit(1)

    console.print(f"🎬 Organizing movies in: {path}")

    try:
        generator = TreeGenerator(path)

        # Generate tree for movies
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Scanning movie directory...", total=None)
            tree = generator.generate_tree(max_depth=2)
            progress.update(task, completed=True)

        tree_text = generator.tree_to_text(tree)

        # Get AI suggestions
        organizer = AIOrganizer(app.api_key, app.gemini_model)

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Getting AI organization suggestions...", total=None)
            plan = organizer.organize_movie_collection(tree_text, "Movies")
            progress.update(task, completed=True)

        # Show preview
        file_ops = FileOperations(path, dry_run=dry_run, backup_enabled=app.backup_enabled)
        console.print(Panel(file_ops.preview_plan(plan), title="Movie Organization Plan"))

        if plan.warnings:
            console.print("⚠️  Warnings detected:", style="yellow")
            for warning in plan.warnings:
                console.print(f"  • {warning}", style="yellow")

        # Ask for confirmation
        if not dry_run:
            if not Confirm.ask("Execute movie organization plan?"):
                console.print("Operation cancelled", style="yellow")
                return

        # Execute plan
        report = file_ops.execute_plan(plan, "Movie Collection")

        # Show results
        console.print(f"\n📊 Organization Results:")
        console.print(f"  ✅ Successful operations: {report.successful_operations}")
        console.print(f"  ❌ Failed operations: {report.failed_operations}")
        if report.total_bytes_moved > 0:
            mb_moved = report.total_bytes_moved / (1024 * 1024)
            console.print(f"  📦 Data moved: {mb_moved:.1f} MB")

    except Exception as e:
        console.print(f"❌ Error organizing movies: {str(e)}", style="red")
        sys.exit(1)


@cli.command()
@click.argument('path')
@click.pass_context
def cleanup(ctx, path):
    """Clean up empty directories after organization."""
    dry_run = ctx.obj['dry_run']

    console.print(f"🧹 Cleaning up empty directories in: {path}")

    try:
        file_ops = FileOperations(path, dry_run=dry_run)
        removed_count = file_ops.cleanup_empty_directories()

        if removed_count > 0:
            console.print(f"✅ Removed {removed_count} empty directories", style="green")
        else:
            console.print("No empty directories found", style="blue")

    except Exception as e:
        console.print(f"❌ Error during cleanup: {str(e)}", style="red")
        sys.exit(1)


@cli.command()
@click.argument('path')
@click.pass_context
def undo(ctx, path):
    """Undo the last organization operation."""
    console.print(f"↩️  Attempting to undo last operation in: {path}")

    try:
        file_ops = FileOperations(path, dry_run=False)
        success = file_ops.undo_last_operation()

        if success:
            console.print("✅ Successfully undone last operation", style="green")
        else:
            console.print("❌ Could not undo last operation", style="red")

    except Exception as e:
        console.print(f"❌ Error during undo: {str(e)}", style="red")
        sys.exit(1)


@cli.command()
@click.argument('path')
@click.pass_context
def status(ctx, path):
    """Show status and statistics for media directory."""
    console.print(f"📊 Analyzing: {path}")

    try:
        file_ops = FileOperations(path)
        usage = file_ops.get_disk_usage()

        table = Table(title="Directory Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        size_gb = usage['total_size'] / (1024**3)
        table.add_row("Total Size", f"{size_gb:.2f} GB")
        table.add_row("File Count", str(usage['file_count']))
        table.add_row("Directory Count", str(usage['directory_count']))

        console.print(table)

        # Check for backup and report files
        backup_dir = Path(path) / ".organize_backup"
        reports_dir = Path(path) / ".organize_reports"

        if backup_dir.exists():
            backup_files = list(backup_dir.glob("backup_*.json"))
            console.print(f"📁 Backup files: {len(backup_files)}")

        if reports_dir.exists():
            report_files = list(reports_dir.glob("execution_report_*.json"))
            console.print(f"📋 Execution reports: {len(report_files)}")

    except Exception as e:
        console.print(f"❌ Error getting status: {str(e)}", style="red")
        sys.exit(1)


if __name__ == '__main__':
    cli()
