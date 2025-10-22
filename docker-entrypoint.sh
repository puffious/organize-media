#!/bin/bash
# AI-Powered Media Library Organizer - Docker Entrypoint Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$(id -u)" = "0" ]; then
    print_error "Do not run as root for security reasons"
    exit 1
fi

# Initialize configuration
init_config() {
    print_status "Initializing configuration..."

    # Check if config directory exists
    if [ ! -d "/app/config" ]; then
        mkdir -p /app/config
    fi

    # Check if .env file exists in config directory
    if [ ! -f "/app/config/.env" ]; then
        if [ -f "/app/.env.example" ]; then
            print_status "Creating .env file from example..."
            cp /app/.env.example /app/config/.env
            print_warning "Please edit /app/config/.env with your API key and paths"
        else
            print_error ".env.example not found"
            exit 1
        fi
    fi

    # Create symlink to config .env if it doesn't exist
    if [ ! -f "/app/.env" ]; then
        ln -s /app/config/.env /app/.env
    fi

    print_success "Configuration initialized"
}

# Validate environment
validate_env() {
    print_status "Validating environment..."

    if [ ! -f "/app/config/.env" ]; then
        print_error "Configuration file not found at /app/config/.env"
        exit 1
    fi

    # Check if GEMINI_API_KEY is set
    if ! grep -q "GEMINI_API_KEY=" /app/config/.env || grep -q "GEMINI_API_KEY=your_gemini_api_key_here" /app/config/.env; then
        print_error "GEMINI_API_KEY not configured in /app/config/.env"
        print_status "Please edit /app/config/.env and set your Google Gemini API key"
        exit 1
    fi

    print_success "Environment validated"
}

# Check media volume mounts
check_media_mounts() {
    print_status "Checking media volume mounts..."

    if [ ! -d "/media" ]; then
        print_warning "No /media volume mounted"
        print_status "Mount your media directories with: -v /host/path:/media"
    else
        print_success "Media volume mounted"
    fi
}

# Show usage information
show_usage() {
    cat << EOF

${BLUE}AI-Powered Media Library Organizer - Docker Container${NC}

${GREEN}Usage:${NC}
  docker run -v /host/media:/media -v /host/config:/app/config ai-media-organizer [COMMAND] [OPTIONS]

${GREEN}Examples:${NC}
  # Setup (interactive)
  docker run -it -v /host/config:/app/config ai-media-organizer setup

  # Test configuration
  docker run -v /host/config:/app/config ai-media-organizer test

  # Scan media directory
  docker run -v /host/media:/media -v /host/config:/app/config ai-media-organizer scan /media/shows

  # Organize TV shows (dry run)
  docker run -v /host/media:/media -v /host/config:/app/config ai-media-organizer organize-show /media/shows

  # Organize movies (execute changes)
  docker run -v /host/media:/media -v /host/config:/app/config ai-media-organizer --no-dry-run organize-movies /media/movies

  # Show status
  docker run -v /host/media:/media -v /host/config:/app/config ai-media-organizer status /media

  # Clean up empty directories
  docker run -v /host/media:/media -v /host/config:/app/config ai-media-organizer cleanup /media

${GREEN}Volume Mounts:${NC}
  /media         - Your media files (movies, TV shows)
  /app/config    - Configuration files (.env)
  /app/logs      - Application logs and reports

${GREEN}Environment Setup:${NC}
  1. Create config directory: mkdir -p /host/config
  2. Run setup: docker run -it -v /host/config:/app/config ai-media-organizer setup
  3. Edit /host/config/.env with your Gemini API key
  4. Test: docker run -v /host/config:/app/config ai-media-organizer test

${GREEN}Security:${NC}
  - Container runs as non-root user 'organizer'
  - Configuration files stored in mounted volume
  - No sensitive data in container image

EOF
}

# Main execution
main() {
    print_status "Starting AI-Powered Media Library Organizer..."

    # Initialize configuration
    init_config

    # Check media mounts
    check_media_mounts

    # If no arguments provided, show usage
    if [ $# -eq 0 ]; then
        show_usage
        exit 0
    fi

    # Handle special commands
    case "$1" in
        "setup")
            print_status "Running interactive setup..."
            python3 /app/quickstart.py
            ;;
        "help"|"--help"|"-h")
            show_usage
            ;;
        "bash"|"sh")
            print_status "Starting shell..."
            exec /bin/bash
            ;;
        *)
            # Validate environment for all other commands
            validate_env

            # Execute the media organizer
            print_status "Executing: python3 /app/src/main.py $*"
            exec python3 /app/src/main.py "$@"
            ;;
    esac
}

# Execute main function with all arguments
main "$@"
