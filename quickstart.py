#!/usr/bin/env python3
"""
Quick Start Script for AI-Powered Media Library Organizer

This script helps you get started quickly with the media organizer.
It will guide you through setup and test your configuration.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_step(step_num, text):
    """Print a formatted step."""
    print(f"\n🚀 Step {step_num}: {text}")
    print("-" * 40)

def check_python():
    """Check Python version."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_requirements():
    """Install required packages."""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        return False

def setup_environment():
    """Set up environment file."""
    env_file = Path(".env")
    env_example = Path(".env.example")

    if env_file.exists():
        print("✅ .env file already exists")
        return True

    if env_example.exists():
        print("Creating .env file from template...")
        try:
            with open(env_example, 'r') as f:
                content = f.read()

            with open(env_file, 'w') as f:
                f.write(content)

            print("✅ .env file created")
            print("📝 Please edit .env file and add your Gemini API key")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("❌ .env.example not found")
        return False

def test_cli():
    """Test if CLI is working."""
    try:
        result = subprocess.run([sys.executable, "src/main.py", "--help"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ CLI is working correctly")
            return True
        else:
            print("❌ CLI test failed")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ CLI test error: {e}")
        return False

def verify_paths():
    """Verify that media paths exist if provided."""
    from dotenv import load_dotenv
    load_dotenv()

    movies_path = os.getenv('MOVIES_PATH')
    tv_shows_path = os.getenv('TV_SHOWS_PATH')

    issues = []

    if movies_path and not Path(movies_path).exists():
        issues.append(f"Movies path does not exist: {movies_path}")

    if tv_shows_path and not Path(tv_shows_path).exists():
        issues.append(f"TV shows path does not exist: {tv_shows_path}")

    if issues:
        print("⚠️  Path Issues Found:")
        for issue in issues:
            print(f"   {issue}")
        print("   Please update paths in .env file or create the directories")
        return False
    else:
        print("✅ Media paths verified")
        return True

def show_next_steps():
    """Show next steps to user."""
    print_header("🎉 Setup Complete!")

    print("\n📋 Next Steps:")
    print("1. Get your Google Gemini API key:")
    print("   - Visit: https://makersuite.google.com/app/apikey")
    print("   - Create a new API key")
    print("   - Add it to your .env file")

    print("\n2. Test your setup:")
    print("   python3 src/main.py test")

    print("\n3. Scan your media directories:")
    print("   python3 src/main.py scan /path/to/your/tv/shows")
    print("   python3 src/main.py scan /path/to/your/movies")

    print("\n4. Organize your media (starts in dry-run mode):")
    print("   python3 src/main.py organize-show /path/to/your/tv/shows")
    print("   python3 src/main.py organize-movies /path/to/your/movies")

    print("\n5. When satisfied, apply changes:")
    print("   python3 src/main.py --no-dry-run organize-show /path/to/your/tv/shows")

    print("\n6. Read the documentation:")
    print("   - README.md for detailed instructions")
    print("   - example.py for programmatic usage")

    print("\n💡 Production Tips:")
    print("   - Always start with dry-run mode (default)")
    print("   - Original filenames are preserved")
    print("   - Check execution reports in .organize_reports/")
    print("   - Use 'python3 src/main.py --help' for all commands")

def main():
    """Main quickstart function."""
    print_header("🎬 AI-Powered Media Library Organizer - Quick Start")

    print("This script will help you set up the media organizer quickly.")
    print("It will check requirements, install dependencies, and create test data.")

    # Step 1: Check Python version
    print_step(1, "Checking Python Version")
    if not check_python():
        print("\n❌ Setup failed. Please upgrade Python and try again.")
        sys.exit(1)

    # Step 2: Install requirements
    print_step(2, "Installing Requirements")
    if not install_requirements():
        print("\n❌ Setup failed. Please check your Python/pip installation.")
        sys.exit(1)

    # Step 3: Set up environment
    print_step(3, "Setting Up Environment")
    if not setup_environment():
        print("\n❌ Setup failed. Please create .env file manually.")
        sys.exit(1)

    # Step 4: Test CLI
    print_step(4, "Testing CLI")
    if not test_cli():
        print("\n❌ CLI test failed. Check the error messages above.")
        sys.exit(1)

    # Step 5: Verify paths (optional)
    print_step(5, "Verifying Media Paths")
    verify_paths()

    # Show next steps
    show_next_steps()

    print("\n🎊 Quickstart completed successfully!")
    print("You're ready to organize your media library with AI!")

if __name__ == "__main__":
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
