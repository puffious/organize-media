"""
Directory Tree Generator for Media Library Organization

This module provides utilities to generate directory trees for media files
and folders, which can then be sent to AI for organization suggestions.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class MediaFile:
    """Represents a media file with metadata."""
    name: str
    path: str
    size: int
    extension: str
    is_video: bool = False
    is_subtitle: bool = False
    is_extra: bool = False


@dataclass
class DirectoryNode:
    """Represents a directory node in the tree structure."""
    name: str
    path: str
    type: str  # 'file' or 'directory'
    size: Optional[int] = None
    children: Optional[List['DirectoryNode']] = None
    media_file: Optional[MediaFile] = None


class TreeGenerator:
    """Generates directory trees for media organization."""

    VIDEO_EXTENSIONS = {'.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
    SUBTITLE_EXTENSIONS = {'.srt', '.sub', '.idx', '.ass', '.ssa', '.vtt'}
    EXTRA_EXTENSIONS = {'.nfo', '.jpg', '.jpeg', '.png', '.gif', '.txt', '.md'}

    def __init__(self, root_path: Union[str, Path]):
        """Initialize with root directory path."""
        self.root_path = Path(root_path)
        if not self.root_path.exists():
            raise ValueError(f"Path does not exist: {root_path}")

    def generate_tree(self, max_depth: int = 5, include_hidden: bool = False) -> DirectoryNode:
        """
        Generate a complete directory tree structure.

        Args:
            max_depth: Maximum depth to traverse
            include_hidden: Whether to include hidden files/directories

        Returns:
            DirectoryNode representing the root of the tree
        """
        return self._build_tree_node(self.root_path, 0, max_depth, include_hidden)

    def generate_single_folder_tree(self, folder_name: str, max_depth: int = 3) -> Optional[DirectoryNode]:
        """
        Generate tree for a single folder within the root path.

        Args:
            folder_name: Name of the folder to analyze
            max_depth: Maximum depth to traverse

        Returns:
            DirectoryNode for the specified folder or None if not found
        """
        folder_path = self.root_path / folder_name
        if not folder_path.exists() or not folder_path.is_dir():
            return None

        return self._build_tree_node(folder_path, 0, max_depth, False)

    def _build_tree_node(self, path: Path, current_depth: int, max_depth: int, include_hidden: bool) -> DirectoryNode:
        """Build a tree node recursively."""
        if current_depth > max_depth:
            return None

        # Skip hidden files/directories if not included
        if not include_hidden and path.name.startswith('.'):
            return None

        node = DirectoryNode(
            name=path.name,
            path=str(path),
            type='directory' if path.is_dir() else 'file'
        )

        if path.is_file():
            # Handle file
            node.size = path.stat().st_size
            node.media_file = self._create_media_file(path)
            return node

        # Handle directory
        try:
            children = []
            for child_path in sorted(path.iterdir()):
                child_node = self._build_tree_node(child_path, current_depth + 1, max_depth, include_hidden)
                if child_node:
                    children.append(child_node)

            node.children = children
            return node

        except PermissionError:
            # Skip directories we can't read
            return None

    def _create_media_file(self, path: Path) -> MediaFile:
        """Create a MediaFile object from a file path."""
        extension = path.suffix.lower()

        return MediaFile(
            name=path.name,
            path=str(path),
            size=path.stat().st_size,
            extension=extension,
            is_video=extension in self.VIDEO_EXTENSIONS,
            is_subtitle=extension in self.SUBTITLE_EXTENSIONS,
            is_extra=extension in self.EXTRA_EXTENSIONS
        )

    def tree_to_text(self, node: DirectoryNode, prefix: str = "", is_last: bool = True) -> str:
        """
        Convert tree structure to text representation similar to `tree` command.

        Args:
            node: The root node to convert
            prefix: Current line prefix for formatting
            is_last: Whether this is the last child at current level

        Returns:
            String representation of the tree
        """
        if not node:
            return ""

        # Current node line
        current_prefix = "└── " if is_last else "├── "
        result = f"{prefix}{current_prefix}{node.name}"

        # Add file size for files
        if node.type == 'file' and node.size:
            size_mb = node.size / (1024 * 1024)
            result += f" ({size_mb:.1f} MB)"

        result += "\n"

        # Process children
        if node.children:
            next_prefix = prefix + ("    " if is_last else "│   ")
            for i, child in enumerate(node.children):
                is_child_last = (i == len(node.children) - 1)
                result += self.tree_to_text(child, next_prefix, is_child_last)

        return result

    def tree_to_json(self, node: DirectoryNode) -> Dict:
        """Convert tree structure to JSON format."""
        if not node:
            return {}

        result = {
            "name": node.name,
            "path": node.path,
            "type": node.type
        }

        if node.size:
            result["size"] = node.size

        if node.media_file:
            result["media_info"] = {
                "extension": node.media_file.extension,
                "is_video": node.media_file.is_video,
                "is_subtitle": node.media_file.is_subtitle,
                "is_extra": node.media_file.is_extra
            }

        if node.children:
            result["children"] = [self.tree_to_json(child) for child in node.children]

        return result

    def get_folder_list(self) -> List[str]:
        """Get list of all folders in the root directory."""
        folders = []
        try:
            for item in self.root_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    folders.append(item.name)
        except PermissionError:
            pass

        return sorted(folders)

    def analyze_media_content(self, node: DirectoryNode) -> Dict:
        """
        Analyze media content in a directory tree.

        Returns:
            Dictionary with analysis results including file counts, sizes, etc.
        """
        analysis = {
            "total_files": 0,
            "video_files": 0,
            "subtitle_files": 0,
            "extra_files": 0,
            "total_size": 0,
            "video_size": 0,
            "seasons_detected": set(),
            "episodes_detected": [],
            "quality_formats": set()
        }

        self._analyze_node_recursive(node, analysis)

        # Convert sets to lists for JSON serialization
        analysis["seasons_detected"] = sorted(list(analysis["seasons_detected"]))
        analysis["quality_formats"] = sorted(list(analysis["quality_formats"]))

        return analysis

    def _analyze_node_recursive(self, node: DirectoryNode, analysis: Dict):
        """Recursively analyze a node and update analysis dictionary."""
        if not node:
            return

        if node.type == 'file' and node.media_file:
            analysis["total_files"] += 1
            analysis["total_size"] += node.size or 0

            if node.media_file.is_video:
                analysis["video_files"] += 1
                analysis["video_size"] += node.size or 0

                # Detect season/episode patterns
                filename = node.media_file.name.lower()
                if 's01' in filename or 'season 01' in filename or 'season.01' in filename:
                    analysis["seasons_detected"].add("Season 01")
                if 's02' in filename or 'season 02' in filename or 'season.02' in filename:
                    analysis["seasons_detected"].add("Season 02")
                if 's03' in filename or 'season 03' in filename or 'season.03' in filename:
                    analysis["seasons_detected"].add("Season 03")

                # Detect quality formats
                if '1080p' in filename:
                    analysis["quality_formats"].add("1080p")
                if '2160p' in filename or '4k' in filename:
                    analysis["quality_formats"].add("2160p/4K")
                if '720p' in filename:
                    analysis["quality_formats"].add("720p")

            elif node.media_file.is_subtitle:
                analysis["subtitle_files"] += 1
            elif node.media_file.is_extra:
                analysis["extra_files"] += 1

        # Process children
        if node.children:
            for child in node.children:
                self._analyze_node_recursive(child, analysis)


def main():
    """Example usage of TreeGenerator."""
    import sys

    if len(sys.argv) != 2:
        print("Usage: python tree_generator.py <directory_path>")
        sys.exit(1)

    directory_path = sys.argv[1]

    try:
        generator = TreeGenerator(directory_path)

        # Generate tree for entire directory
        print("Generating directory tree...")
        tree = generator.generate_tree(max_depth=3)

        # Print text representation
        print("\nDirectory Tree:")
        print(generator.tree_to_text(tree))

        # Print analysis
        print("\nMedia Analysis:")
        analysis = generator.analyze_media_content(tree)
        for key, value in analysis.items():
            print(f"  {key}: {value}")

        # List all folders
        print("\nAvailable folders:")
        folders = generator.get_folder_list()
        for i, folder in enumerate(folders[:10], 1):  # Show first 10
            print(f"  {i}. {folder}")

        if len(folders) > 10:
            print(f"  ... and {len(folders) - 10} more folders")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
