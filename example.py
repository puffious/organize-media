#!/usr/bin/env python3
"""
Production Examples for AI-Powered Media Library Organizer

This script demonstrates production-ready usage patterns and best practices
for integrating the media organizer into enterprise workflows.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

from tree_generator import TreeGenerator
from ai_organizer import AIOrganizer
from file_operations import FileOperations


def example_scan_directory():
    """Example: Scan and analyze a directory structure."""
    print("=" * 60)
    print("EXAMPLE 1: Directory Scanning and Analysis")
    print("=" * 60)

    # Replace with your actual path
    media_path = "/path/to/your/media"  # Change this!

    if not Path(media_path).exists():
        print(f"⚠️  Path doesn't exist: {media_path}")
        print("Please update the media_path variable in this script")
        return

    try:
        # Create tree generator
        generator = TreeGenerator(media_path)

        # Generate tree structure
        print("Scanning directory structure...")
        tree = generator.generate_tree(max_depth=3)

        # Display tree
        print("\nDirectory Tree:")
        print("-" * 40)
        print(generator.tree_to_text(tree))

        # Analyze content
        print("\nMedia Analysis:")
        print("-" * 40)
        analysis = generator.analyze_media_content(tree)

        for key, value in analysis.items():
            if key in ['total_size', 'video_size']:
                size_mb = value / (1024 * 1024)
                print(f"{key.replace('_', ' ').title()}: {size_mb:.1f} MB")
            else:
                print(f"{key.replace('_', ' ').title()}: {value}")

        # List available folders
        print("\nAvailable Folders:")
        print("-" * 40)
        folders = generator.get_folder_list()
        for i, folder in enumerate(folders[:10], 1):
            print(f"{i:2d}. {folder}")

        if len(folders) > 10:
            print(f"    ... and {len(folders) - 10} more folders")

    except Exception as e:
        print(f"Error: {e}")


def example_tv_show_organization():
    """Production example: Organize a TV show using AI."""
    print("\n" + "=" * 60)
    print("PRODUCTION EXAMPLE: TV Show Organization")
    print("=" * 60)

    # Load environment variables
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        print("⚠️  GEMINI_API_KEY not found in environment")
        print("Please set up your .env file with your API key")
        return

    # Example show structure (replace with real path)
    show_path = "/path/to/tv/shows"  # Change this!
    show_name = "Silicon Valley"     # Change this!

    if not Path(show_path).exists():
        print(f"⚠️  Path doesn't exist: {show_path}")
        print("Please update the show_path variable in this script")
        return

    try:
        # Initialize components
        generator = TreeGenerator(show_path)
        organizer = AIOrganizer(api_key)
        file_ops = FileOperations(show_path, dry_run=True)  # Always dry run in example

        # Generate tree for specific show
        print(f"Analyzing show: {show_name}")
        show_tree = generator.generate_single_folder_tree(show_name)

        if not show_tree:
            print(f"❌ Show folder not found: {show_name}")
            return

        # Convert to text format
        tree_text = generator.tree_to_text(show_tree)
        print("\nCurrent Structure:")
        print("-" * 40)
        print(tree_text)

        # Get AI organization suggestions
        print("\nGetting AI suggestions...")
        plan = organizer.organize_tv_show(tree_text, show_name)

        # Display organization plan
        print("\nAI Organization Plan:")
        print("-" * 40)
        print(f"  Show: {plan.show_name}")
        if plan.year:
            print(f"  Year: {plan.year}")
        print(f"  Summary: {plan.summary}")
        print("  Note: Original filenames are preserved during organization")

        if plan.warnings:
            print("\nWarnings:")
            for warning in plan.warnings:
                print(f"  ⚠️  {warning}")

        print(f"\nSuggested Operations ({len(plan.suggestions)}):")
        for i, suggestion in enumerate(plan.suggestions, 1):
            print(f"{i:2d}. {suggestion.operation.upper()}")
            if suggestion.operation == 'create_directory':
                print(f"    Create: {suggestion.destination_path}")
            elif suggestion.operation == 'move':
                print(f"    Move: {suggestion.source_path}")
                print(f"      To: {suggestion.destination_path}")
                print(f"    Confidence: {suggestion.confidence:.1%}")
                print(f"    (Filename preserved: {Path(suggestion.source_path).name})")
            print(f"    Reason: {suggestion.reason}")

        # Preview execution (dry run)
        print("\nExecution Preview:")
        print("-" * 40)
        preview = file_ops.preview_plan(plan)
        print(preview)

        # Note about execution
        print("\n💡 This is a DRY RUN - no files were moved")
        print("To execute for real, set dry_run=False in FileOperations")

    except Exception as e:
        print(f"Error: {e}")


def example_movie_organization():
    """Production example: Organize movies using AI."""
    print("\n" + "=" * 60)
    print("PRODUCTION EXAMPLE: Movie Organization")
    print("=" * 60)

    # Load environment variables
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        print("⚠️  GEMINI_API_KEY not found in environment")
        print("Please set up your .env file with your API key")
        return

    # Example movie path (replace with real path)
    movies_path = "/path/to/movies"  # Change this!

    if not Path(movies_path).exists():
        print(f"⚠️  Path doesn't exist: {movies_path}")
        print("Please update the movies_path variable in this script")
        return

    try:
        # Initialize components
        generator = TreeGenerator(movies_path)
        organizer = AIOrganizer(api_key)
        file_ops = FileOperations(movies_path, dry_run=True)  # Always dry run in example

        # Generate tree for movies (limited depth for movies)
        print("Analyzing movie collection...")
        tree = generator.generate_tree(max_depth=2)

        # Convert to text format
        tree_text = generator.tree_to_text(tree)
        print("\nCurrent Structure:")
        print("-" * 40)
        print(tree_text[:2000] + "..." if len(tree_text) > 2000 else tree_text)

        # Get AI organization suggestions
        print("\nGetting AI suggestions...")
        plan = organizer.organize_movie_collection(tree_text, "Movies")

        # Display organization plan
        print("\nAI Organization Plan:")
        print("-" * 40)
        print(f"Collection: {plan.show_name}")
        print(f"Summary: {plan.summary}")

        if plan.warnings:
            print("\nWarnings:")
            for warning in plan.warnings:
                print(f"  ⚠️  {warning}")

        print(f"\nSuggested Operations ({len(plan.suggestions)}):")
        for i, suggestion in enumerate(plan.suggestions[:10], 1):  # Show first 10
            print(f"{i:2d}. {suggestion.operation.upper()}")
            if suggestion.operation == 'create_directory':
                print(f"    Create: {suggestion.destination_path}")
            elif suggestion.operation == 'move':
                print(f"    Move: {Path(suggestion.source_path).name}")
                print(f"      To: {suggestion.destination_path}")
                print(f"    Confidence: {suggestion.confidence:.1%}")

        if len(plan.suggestions) > 10:
            print(f"    ... and {len(plan.suggestions) - 10} more operations")

        # Note about execution
        print("\n💡 This is a DRY RUN - no files were moved")
        print("To execute for real, set dry_run=False in FileOperations")

    except Exception as e:
        print(f"Error: {e}")


def example_create_test_structure():
    """Example: Create a test directory structure for testing."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Create Test Structure")
    print("=" * 60)

    test_dir = Path("test_media")

    print(f"Creating test directory structure in: {test_dir}")

    # Create test TV show structure
    tv_shows = [
        "Silicon Valley/Season 1/Silicon.Valley.S01E01.1080p.mkv",
        "Silicon Valley/Season 1/Silicon.Valley.S01E02.1080p.mkv",
        "Silicon Valley/s02/episode1.mkv",
        "Silicon Valley/s02/episode2.mkv",
        "Breaking Bad/s01/Breaking.Bad.S01E01.720p.mkv",
        "Breaking Bad/Season 2/Breaking Bad S02E01.mkv",
        "The Office/Season 01/The.Office.S01E01.mkv",
        "The Office/Season 01/The.Office.S01E02.mkv",
    ]

    # Create test movie structure
    movies = [
        "Ant-Man.2015.1080p.BluRay/Ant-Man.2015.1080p.BluRay.mkv",
        "Arrival (2016)/Arrival.2016.mkv",
        "batman_begins.mkv",
        "Movies/Inception/Inception.2010.1080p.mkv",
        "random_movie_folder/some_movie.avi",
    ]

    try:
        # Create TV shows structure
        tv_dir = test_dir / "TV Shows"
        for show_file in tv_shows:
            file_path = tv_dir / show_file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()  # Create empty file

        # Create movies structure
        movies_dir = test_dir / "Movies"
        for movie_file in movies:
            file_path = movies_dir / movie_file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()  # Create empty file

        print("✅ Test structure created successfully!")
        print("\nCreated structure:")
        print(f"  📁 {tv_dir}")
        print(f"  📁 {movies_dir}")

        print("\nYou can now test the organizer with:")
        print(f"  python example.py")
        print(f"  # Update paths in script to point to {test_dir.absolute()}")

        # Show the created structure
        generator = TreeGenerator(str(test_dir))
        tree = generator.generate_tree(max_depth=4)
        print("\nGenerated Test Structure:")
        print("-" * 40)
        print(generator.tree_to_text(tree))

    except Exception as e:
        print(f"Error creating test structure: {e}")


def example_ai_connection_test():
    """Production example: Test AI connection and capabilities."""
    print("\n" + "=" * 60)
    print("PRODUCTION EXAMPLE: AI Connection Test")
    print("=" * 60)

    # Load environment variables
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        print("⚠️  GEMINI_API_KEY not found in environment")
        print("Please set up your .env file with your API key")
        return

    try:
        # Test AI connection
        organizer = AIOrganizer(api_key)

        print("Testing AI connection...")
        if organizer.test_connection():
            print("✅ AI connection successful!")
        else:
            print("❌ AI connection failed")
            return

        # Test with sample data
        sample_tree = """
Silicon Valley/
├── Season 1/
│   ├── Silicon.Valley.S01E01.Minimum.Viable.Product.1080p.mkv
│   └── Silicon.Valley.S01E02.The.Cap.Table.1080p.mkv
├── s02/
│   ├── episode1.mkv
│   └── episode2.mkv
└── Season Three/
    ├── s3e1.avi
    └── s3e2.avi
"""

        print("\nTesting AI with sample TV show structure...")
        print("Sample input:")
        print(sample_tree)

        tree_text = sample_tree.strip()
        plan = organizer.organize_tv_show(tree_text, "Silicon Valley")

        print("\nAI Response:")
        print(f"  Show Name: {plan.show_name}")
        print(f"  Year: {plan.year}")
        print(f"  Summary: {plan.summary}")
        print(f"  Operations: {len(plan.suggestions)}")

        if plan.suggestions:
            print("\nFirst few suggestions:")
            for i, suggestion in enumerate(plan.suggestions[:3], 1):
                print(f"  {i}. {suggestion.operation}: {suggestion.reason}")
                if suggestion.operation == 'move':
                    print(f"     (Original filename preserved: {Path(suggestion.source_path).name})")

        print("\n✅ AI test completed successfully!")

    except Exception as e:
        print(f"Error testing AI: {e}")


def main():
    """Run production examples."""
    print("🎬 AI-Powered Media Library Organizer - Production Examples")
    print("=" * 65)

    print("\n📝 PRODUCTION SETUP:")
    print("1. Production setup: make quick-setup")
    print("2. Docker deployment: docker-compose up -d")
    print("3. Package installation: pip install -e .")
    print("4. Update paths in this script to match your environment")

    # Check if .env exists
    if not Path('.env').exists():
        print("\n⚠️  No .env file found!")
        print("Please copy .env.example to .env and configure your settings")

        if input("\nCreate test structure? (y/N): ").lower() == 'y':
            example_create_test_structure()
        return

    # Load environment to check setup
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        print("\n⚠️  GEMINI_API_KEY not configured in .env file")
        print("Run 'make setup' or 'python3 quickstart.py' to configure")
        return

    # Run production examples
    print("\n🚀 Running Production Examples...")

    # Test AI connection first
    example_ai_connection_test()

    print("\n📋 Available Examples:")
    print("  - Uncomment example functions below to run specific examples")
    print("  - Update media paths to match your environment")

    # Uncomment and update paths as needed:
    # example_scan_directory()
    # example_tv_show_organization()
    # example_movie_organization()

    print("\n✅ Production examples ready!")
    print("\n🏭 Production Tips:")
    print("  - Use 'make' commands for production operations")
    print("  - Deploy with Docker for isolation and security")
    print("  - Original filenames are always preserved")
    print("  - Monitor execution reports in .organize_reports/")
    print("  - Use dry-run mode to preview changes")
    print("  - See README.md for complete production guide")


if __name__ == "__main__":
    main()
