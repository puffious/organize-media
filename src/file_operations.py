"""
File System Operations Module for Media Library Organization

This module handles all file system operations including moving files,
creating directories, and applying organization plans safely.
Original filenames are always preserved - only directory structure changes.
"""

import os
import shutil
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from ai_organizer import OrganizationPlan, OrganizationSuggestion


@dataclass
class OperationResult:
    """Result of a file system operation."""
    success: bool
    operation: str
    source_path: str
    destination_path: str
    error_message: Optional[str] = None
    bytes_moved: Optional[int] = None


@dataclass
class ExecutionReport:
    """Complete report of organization execution."""
    plan_name: str
    start_time: datetime
    end_time: Optional[datetime]
    total_operations: int
    successful_operations: int
    failed_operations: int
    results: List[OperationResult]
    total_bytes_moved: int
    dry_run: bool


class FileOperations:
    """Handles safe file system operations for media organization."""

    def __init__(self, base_path: str, dry_run: bool = True, backup_enabled: bool = True):
        """
        Initialize file operations handler.

        Args:
            base_path: Base path for all operations
            dry_run: If True, only simulate operations without actual changes
            backup_enabled: If True, create backup information before moves
        """
        self.base_path = Path(base_path)
        self.dry_run = dry_run
        self.backup_enabled = backup_enabled

        if not self.base_path.exists():
            raise ValueError(f"Base path does not exist: {base_path}")

    def execute_plan(self, plan: OrganizationPlan, plan_name: str = "") -> ExecutionReport:
        """
        Execute a complete organization plan.

        Note: Original filenames are preserved - only moves files to correct folders.

        Args:
            plan: The organization plan to execute
            plan_name: Name/description for the plan

        Returns:
            ExecutionReport with results of all operations
        """
        report = ExecutionReport(
            plan_name=plan_name or f"Organization of {plan.show_name}",
            start_time=datetime.now(),
            end_time=None,
            total_operations=len(plan.suggestions),
            successful_operations=0,
            failed_operations=0,
            results=[],
            total_bytes_moved=0,
            dry_run=self.dry_run
        )

        print(f"{'[DRY RUN] ' if self.dry_run else ''}Executing plan: {report.plan_name}")
        print(f"Total operations: {report.total_operations}")

        # Sort operations to do directory creation first
        sorted_suggestions = sorted(
            plan.suggestions,
            key=lambda x: (0 if x.operation == 'create_directory' else 1, x.destination_path)
        )

        for i, suggestion in enumerate(sorted_suggestions, 1):
            print(f"Operation {i}/{report.total_operations}: {suggestion.operation}")

            if suggestion.operation == 'create_directory':
                result = self._create_directory(suggestion)
            elif suggestion.operation == 'move':
                result = self._move_file(suggestion)
            else:
                result = OperationResult(
                    success=False,
                    operation=suggestion.operation,
                    source_path=suggestion.source_path,
                    destination_path=suggestion.destination_path,
                    error_message=f"Unknown operation: {suggestion.operation}"
                )

            report.results.append(result)

            if result.success:
                report.successful_operations += 1
                if result.bytes_moved:
                    report.total_bytes_moved += result.bytes_moved
            else:
                report.failed_operations += 1
                print(f"  ❌ Failed: {result.error_message}")

        report.end_time = datetime.now()
        self._save_execution_report(report)

        return report

    def _create_directory(self, suggestion: OrganizationSuggestion) -> OperationResult:
        """Create a directory."""
        dest_path = self.base_path / suggestion.destination_path

        if self.dry_run:
            print(f"  [DRY RUN] Would create directory: {dest_path}")
            return OperationResult(
                success=True,
                operation='create_directory',
                source_path="",
                destination_path=str(dest_path)
            )

        try:
            if dest_path.exists():
                print(f"  ℹ️  Directory already exists: {dest_path}")
                return OperationResult(
                    success=True,
                    operation='create_directory',
                    source_path="",
                    destination_path=str(dest_path)
                )

            dest_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Created directory: {dest_path}")

            return OperationResult(
                success=True,
                operation='create_directory',
                source_path="",
                destination_path=str(dest_path)
            )

        except Exception as e:
            return OperationResult(
                success=False,
                operation='create_directory',
                source_path="",
                destination_path=str(dest_path),
                error_message=str(e)
            )

    def _move_file(self, suggestion: OrganizationSuggestion) -> OperationResult:
        """Move a file from source to destination while preserving original filename."""
        source_path = self.base_path / suggestion.source_path
        dest_path = self.base_path / suggestion.destination_path

        # Validate source exists
        if not source_path.exists():
            return OperationResult(
                success=False,
                operation='move',
                source_path=str(source_path),
                destination_path=str(dest_path),
                error_message=f"Source file not found: {source_path}"
            )

        # Get file size for reporting
        file_size = source_path.stat().st_size if source_path.is_file() else 0

        if self.dry_run:
            print(f"  [DRY RUN] Would move: {source_path} -> {dest_path}")
            return OperationResult(
                success=True,
                operation='move',
                source_path=str(source_path),
                destination_path=str(dest_path),
                bytes_moved=file_size
            )

        try:
            # Create backup info if enabled
            if self.backup_enabled:
                self._create_backup_info(source_path, dest_path)

            # Ensure destination directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Check if destination exists
            if dest_path.exists():
                if self._should_overwrite(source_path, dest_path):
                    print(f"  ⚠️  Overwriting existing file: {dest_path}")
                    dest_path.unlink()
                else:
                    # Create unique name
                    dest_path = self._get_unique_destination(dest_path)
                    print(f"  ℹ️  Using alternative name: {dest_path}")

            # Perform the move
            shutil.move(str(source_path), str(dest_path))
            print(f"  ✅ Moved: {source_path.name} -> {dest_path}")

            return OperationResult(
                success=True,
                operation='move',
                source_path=str(source_path),
                destination_path=str(dest_path),
                bytes_moved=file_size
            )

        except Exception as e:
            return OperationResult(
                success=False,
                operation='move',
                source_path=str(source_path),
                destination_path=str(dest_path),
                error_message=str(e)
            )

    def _should_overwrite(self, source_path: Path, dest_path: Path) -> bool:
        """Determine if destination file should be overwritten."""
        if not dest_path.exists():
            return False

        # Compare file sizes - keep larger file
        source_size = source_path.stat().st_size
        dest_size = dest_path.stat().st_size

        if source_size > dest_size:
            return True

        # If same size, keep newer file
        if source_size == dest_size:
            source_mtime = source_path.stat().st_mtime
            dest_mtime = dest_path.stat().st_mtime
            return source_mtime > dest_mtime

        return False

    def _get_unique_destination(self, dest_path: Path) -> Path:
        """Generate a unique destination path if file already exists."""
        counter = 1
        base_name = dest_path.stem
        extension = dest_path.suffix
        parent = dest_path.parent

        while True:
            new_name = f"{base_name}.{counter:02d}{extension}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1

    def _create_backup_info(self, source_path: Path, dest_path: Path):
        """Create backup information for file operations."""
        backup_dir = self.base_path / ".organize_backup"
        backup_dir.mkdir(exist_ok=True)

        backup_info = {
            "timestamp": datetime.now().isoformat(),
            "operation": "move",
            "source": str(source_path),
            "destination": str(dest_path),
            "source_size": source_path.stat().st_size if source_path.exists() else 0
        }

        backup_file = backup_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_file, 'w') as f:
            json.dump(backup_info, f, indent=2)

    def _save_execution_report(self, report: ExecutionReport):
        """Save execution report to file."""
        reports_dir = self.base_path / ".organize_reports"
        reports_dir.mkdir(exist_ok=True)

        timestamp = report.start_time.strftime('%Y%m%d_%H%M%S')
        report_file = reports_dir / f"execution_report_{timestamp}.json"

        # Convert report to dict for JSON serialization
        report_dict = {
            "plan_name": report.plan_name,
            "start_time": report.start_time.isoformat(),
            "end_time": report.end_time.isoformat() if report.end_time else None,
            "total_operations": report.total_operations,
            "successful_operations": report.successful_operations,
            "failed_operations": report.failed_operations,
            "total_bytes_moved": report.total_bytes_moved,
            "dry_run": report.dry_run,
            "results": [
                {
                    "success": r.success,
                    "operation": r.operation,
                    "source_path": r.source_path,
                    "destination_path": r.destination_path,
                    "error_message": r.error_message,
                    "bytes_moved": r.bytes_moved
                }
                for r in report.results
            ]
        }

        with open(report_file, 'w') as f:
            json.dump(report_dict, f, indent=2)

        print(f"\nExecution report saved: {report_file}")

    def undo_last_operation(self) -> bool:
        """
        Undo the last organization operation using backup information.

        Returns:
            True if undo was successful, False otherwise
        """
        backup_dir = self.base_path / ".organize_backup"
        if not backup_dir.exists():
            print("No backup information found")
            return False

        # Find the most recent backup file
        backup_files = sorted(backup_dir.glob("backup_*.json"), reverse=True)
        if not backup_files:
            print("No backup files found")
            return False

        latest_backup = backup_files[0]

        try:
            with open(latest_backup, 'r') as f:
                backup_info = json.load(f)

            source = Path(backup_info['source'])
            destination = Path(backup_info['destination'])

            if backup_info['operation'] == 'move' and destination.exists():
                # Move the file back
                shutil.move(str(destination), str(source))
                print(f"Undone: {destination} -> {source}")

                # Remove the backup file
                latest_backup.unlink()
                return True

        except Exception as e:
            print(f"Failed to undo operation: {e}")
            return False

        return False

    def cleanup_empty_directories(self, path: Optional[Path] = None) -> int:
        """
        Remove empty directories recursively.

        Args:
            path: Path to clean up (defaults to base_path)

        Returns:
            Number of directories removed
        """
        if path is None:
            path = self.base_path

        removed_count = 0

        try:
            for item in path.iterdir():
                if item.is_dir():
                    # Recursively clean subdirectories first
                    removed_count += self.cleanup_empty_directories(item)

                    # Try to remove this directory if it's empty
                    try:
                        if not any(item.iterdir()):  # Directory is empty
                            if not self.dry_run:
                                item.rmdir()
                                print(f"  🗑️  Removed empty directory: {item}")
                            else:
                                print(f"  [DRY RUN] Would remove empty directory: {item}")
                            removed_count += 1
                    except OSError:
                        pass  # Directory not empty or permission denied

        except PermissionError:
            pass

        return removed_count

    def get_disk_usage(self, path: Optional[Path] = None) -> Dict[str, int]:
        """
        Get disk usage information for a path.

        Args:
            path: Path to analyze (defaults to base_path)

        Returns:
            Dictionary with total_size, file_count, directory_count
        """
        if path is None:
            path = self.base_path

        total_size = 0
        file_count = 0
        directory_count = 0

        for item in path.rglob('*'):
            if item.is_file():
                total_size += item.stat().st_size
                file_count += 1
            elif item.is_dir():
                directory_count += 1

        return {
            "total_size": total_size,
            "file_count": file_count,
            "directory_count": directory_count
        }

    def preview_plan(self, plan: OrganizationPlan) -> str:
        """
        Generate a text preview of what the organization plan would do.

        Note: All moves preserve original filenames.

        Args:
            plan: Organization plan to preview

        Returns:
            String with formatted preview
        """
        preview = f"Organization Plan Preview: {plan.show_name}\n"
        preview += "=" * 50 + "\n\n"

        if plan.summary:
            preview += f"Summary: {plan.summary}\n\n"

        if plan.warnings:
            preview += "⚠️  Warnings:\n"
            for warning in plan.warnings:
                preview += f"  - {warning}\n"
            preview += "\n"

        preview += f"Operations ({len(plan.suggestions)}):\n"

        create_ops = [s for s in plan.suggestions if s.operation == 'create_directory']
        move_ops = [s for s in plan.suggestions if s.operation == 'move']

        if create_ops:
            preview += f"\n📁 Directory Creation ({len(create_ops)}):\n"
            for op in create_ops:
                preview += f"  + Create: {op.destination_path}\n"

        if move_ops:
            preview += f"\n📦 File Moves ({len(move_ops)}) - Original filenames preserved:\n"
            for op in move_ops:
                confidence_indicator = "🟢" if op.confidence > 0.8 else "🟡" if op.confidence > 0.6 else "🔴"
                preview += f"  {confidence_indicator} {op.source_path} -> {op.destination_path}\n"
                preview += f"     Reason: {op.reason} (confidence: {op.confidence:.1%})\n"

        total_moves = len([s for s in plan.suggestions if s.operation == 'move'])
        preview += f"\nTotal files to be moved: {total_moves}\n"

        return preview
