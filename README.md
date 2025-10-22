# AI-Powered Media Library Organizer

A production-ready, intelligent media library organizer that uses Google Gemini AI to automatically organize your movie and TV show collections. The AI analyzes your directory structure and suggests optimal organization plans, which can then be applied to your filesystem.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

## Features

- 🤖 **AI-Powered Organization**: Uses Google Gemini AI via google-genai to intelligently analyze and organize media files
- 📺 **TV Show Support**: Handles complex TV show structures with seasons and episodes
- 🎬 **Movie Organization**: Organizes movie collections with proper naming conventions
- 🔍 **Directory Analysis**: Scans and analyzes directory trees to understand current structure
- 🚀 **Dry Run Mode**: Preview changes before applying them
- 📊 **Detailed Reporting**: Complete execution reports and operation logs
- 🔙 **Undo Support**: Ability to undo recent organization operations
- 🧹 **Cleanup Tools**: Remove empty directories after organization
- 🛡️ **Safe Operations**: Backup information, conflict resolution, and filename preservation

## Quick Start

### Method 1: Quick Setup (Recommended)

```bash
# Quick production setup
make quick-setup

# Or manually:
pip install -r requirements.txt
python3 quickstart.py
```

### Method 2: Docker (Isolated & Secure)

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or manually:
docker build -t ai-media-organizer .
docker run -it -v /path/to/media:/media -v ./config:/app/config ai-media-organizer setup
```

### Method 3: Package Installation

```bash
# Install as Python package
pip install -e .

# Use globally installed command
media-organizer --help
```

## Installation & Deployment

### Production Installation

#### Option 1: Makefile (Recommended)
```bash
# Quick production setup
make quick-setup

# Development environment
make dev-setup

# See all options
make help
```

#### Option 2: Docker Deployment
```bash
# Using Docker Compose (recommended)
docker-compose up -d
docker-compose exec media-organizer setup

# Using Docker directly
docker build -t ai-media-organizer .
docker run -it \
  -v /host/media:/media \
  -v /host/config:/app/config \
  ai-media-organizer setup
```

#### Option 3: Python Package
```bash
# Install as editable package
pip install -e .

# Or build and install wheel
make package
pip install dist/*.whl
```

### Prerequisites

- **Python**: 3.8 or higher
- **API Key**: Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- **Permissions**: Read/write access to your media directories
- **Storage**: Adequate disk space for file operations
- **Memory**: 512MB+ RAM recommended

### Production Configuration

1. **Environment Setup**:
   ```bash
   # Copy configuration template
   cp .env.example .env
   
   # Edit with your settings
   nano .env
   ```

2. **Security Configuration**:
   ```bash
   # Set restrictive permissions on config
   chmod 600 .env
   
   # Ensure media directories have proper ownership
   chown -R user:group /path/to/media
   ```

3. **Validation**:
   ```bash
   # Test configuration
   make test-connection
   # or
   python3 src/main.py test
   ```

## Production Usage

### Command Line Interface

```bash
# Production commands
python3 src/main.py --help                    # Show all options
python3 src/main.py scan /path/to/media       # Analyze structure
python3 src/main.py organize-show /path/to/shows
python3 src/main.py organize-movies /path/to/movies
python3 src/main.py status /path/to/media     # Statistics
python3 src/main.py cleanup /path/to/media    # Remove empty dirs
python3 src/main.py undo /path/to/media       # Undo last operation
```

### Makefile Commands (Production)

```bash
# Media operations
make scan MEDIA_PATH=/path/to/media
make organize-shows SHOWS_PATH=/path/to/shows
make organize-movies MOVIES_PATH=/path/to/movies
make status MEDIA_PATH=/path/to/media
make cleanup-dirs MEDIA_PATH=/path/to/media

# Maintenance
make validate-env                             # Check configuration
make clean                                    # Clean temp files
```

### Docker Commands

```bash
# Docker operations
docker-compose exec media-organizer scan /media/shows
docker-compose exec media-organizer organize-show /media/shows
docker-compose exec media-organizer organize-movies /media/movies
docker-compose exec media-organizer status /media

# Interactive mode
docker-compose exec media-organizer bash
```

### Package Commands (if installed)

```bash
# Global commands (if installed as package)
media-organizer scan /path/to/media
organize-media organize-show /path/to/shows
```

### Organization Formats

#### TV Shows
The organizer creates this structure:
```
Show Name (Year)/
├── Season 01/
│   ├── [original-filename].mkv
│   ├── [original-filename].mkv
│   └── ...
├── Season 02/
│   ├── [original-filename].mkv
│   └── ...
└── Season 03/
    └── ...
```

#### Movies
The organizer creates this structure:
```
Movies/
├── Movie Name (Year)/
│   ├── [original-filename].mkv
│   ├── [original-filename].srt (subtitles)
│   └── poster.jpg (if exists)
├── Another Movie (Year)/
│   └── [original-filename].mkv
└── ...
```

### Advanced Usage

#### Dry Run Mode (Default)
By default, all operations run in dry-run mode, showing you what would happen without making changes:

```bash
python src/main.py organize-show /path/to/shows
```

#### Execute Real Changes
To apply changes to your filesystem:

```bash
python src/main.py --no-dry-run organize-show /path/to/shows
```

#### Batch Processing
Process all shows in a directory:

```bash
python src/main.py organize-show /path/to/shows
# When prompted, choose 'all' to process all shows
```

#### Verbose Output
Get detailed information during operations:

```bash
python src/main.py -v organize-show /path/to/shows
```

## Configuration Options

The `.env` file supports these options:

```bash
# Required
GEMINI_API_KEY=your_api_key_here

# Media Paths
MOVIES_PATH=/path/to/movies
TV_SHOWS_PATH=/path/to/tv/shows

# Operation Settings
DRY_RUN=true                    # Default to dry-run mode
BACKUP_ENABLED=true             # Create backup information
LOG_LEVEL=INFO                  # Logging level

# AI Configuration
GEMINI_MODEL=gemini-1.5-flash
MAX_TOKENS=8192
TEMPERATURE=0.1

# File Operations
MOVE_FILES=true                 # Move files vs copy
CREATE_SYMLINKS=false           # Create symlinks instead of moving
PRESERVE_ORIGINAL_STRUCTURE=false
```

## Production Architecture

### System Overview
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Media Files   │───▶│  AI Organizer    │───▶│ Organized Media │
│                 │    │                  │    │                 │
│ Chaotic         │    │ 1. Scan & Analyze│    │ Structured      │
│ Structure       │    │ 2. AI Processing │    │ Folders         │
│                 │    │ 3. Safe Execution│    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                       ┌──────▼──────┐
                       │   Reports   │
                       │   Backups   │
                       │   Logs      │
                       └─────────────┘
```

### Processing Pipeline

1. **Directory Scanning**: Recursive analysis of media structure
2. **Content Analysis**: File type detection and metadata extraction
3. **AI Processing**: Google Gemini analyzes patterns and suggests organization
4. **Plan Validation**: Safety checks and conflict resolution
5. **Safe Execution**: Atomic operations with rollback capability
6. **Reporting**: Detailed logs and execution reports

### Safety Mechanisms

- **Atomic Operations**: All-or-nothing file moves
- **Backup System**: Complete operation history
- **Dry-Run Mode**: Preview changes before execution
- **Rollback Support**: Undo recent operations
- **Conflict Resolution**: Intelligent duplicate handling
- **Permission Validation**: Pre-flight security checks

## Examples

### Organizing a Complex TV Show

**Before:**
```
Silicon Valley/
├── Silicon.Valley.S01E01.1080p.BluRay.x264-DEMAND.mkv
├── Silicon.Valley.S01E02.1080p.BluRay.x264-DEMAND.mkv
├── Season 2/
│   ├── Silicon Valley S02E01 HDTV x264-KILLERS.mkv
│   └── Silicon Valley S02E02 HDTV x264-KILLERS.mkv
└── s03/
    ├── episode1.mkv
    └── episode2.mkv
```

**After AI Organization:**
```
Silicon Valley (2014)/
├── Season 01/
│   ├── Silicon.Valley.S01E01.1080p.BluRay.x264-DEMAND.mkv
│   └── Silicon.Valley.S01E02.1080p.BluRay.x264-DEMAND.mkv
├── Season 02/
│   ├── Silicon Valley S02E01 HDTV x264-KILLERS.mkv
│   └── Silicon Valley S02E02 HDTV x264-KILLERS.mkv
└── Season 03/
    ├── episode1.mkv
    └── episode2.mkv
```

### Organizing Movies

**Before:**
```
Movies/
├── Ant-Man.2015.IMAX.1080p.BluRay.OPUS.7.1.AV1-KIMJI/
│   └── Ant-Man.2015.IMAX.1080p.BluRay.OPUS.7.1.AV1-KIMJI.mkv
├── Arrival (2016) Open Matte (1080p WEBRip x265 Silence)/
│   └── Arrival (2016) Open Matte (1080p WEBRip x265 Silence).mkv
└── movie_files/
    ├── batman_begins_2005.mkv
    └── batman_begins_subs.srt
```

**After AI Organization:**
```
Movies/
├── Ant-Man (2015)/
│   └── Ant-Man.2015.IMAX.1080p.BluRay.OPUS.7.1.AV1-KIMJI.mkv
├── Arrival (2016)/
│   └── Arrival (2016) Open Matte (1080p WEBRip x265 Silence).mkv
└── Batman Begins (2005)/
    ├── batman_begins_2005.mkv
    └── batman_begins_subs.srt
```

## Safety Features

### Backup System
- Creates JSON backup files before operations
- Stores original file locations
- Enables undo functionality
- Tracks operation history

### Conflict Resolution
- Keeps highest quality versions when duplicates exist
- Creates unique filenames for conflicts
- Preserves original files when unsure
- Provides detailed conflict warnings

### Validation
- Validates file existence before operations
- Checks destination paths
- Confirms directory permissions
- Preserves original filenames
- Reports potential issues

## Production Operations

### Monitoring & Logging

```bash
# Check application status
make status MEDIA_PATH=/path/to/media

# View recent operations
tail -f logs/organizer.log

# Monitor execution reports
ls -la .organize_reports/
```

### Troubleshooting

#### Common Production Issues

**Configuration Issues:**
```bash
# Validate environment
make validate-env

# Test AI connection
make test-connection

# Reset configuration
rm .env && make setup
```

**Performance Issues:**
```bash
# For large libraries (10,000+ files)
# Process in smaller batches
python3 src/main.py organize-show /media/shows/specific-show

# Monitor resource usage
docker stats media-organizer  # if using Docker
htop  # system monitoring
```

**Permission/Security Issues:**
```bash
# Check file permissions
ls -la /path/to/media

# Fix ownership (if needed)
sudo chown -R $USER:$USER /path/to/media

# Docker permission issues
docker-compose exec media-organizer ls -la /media
```

**Recovery Operations:**
```bash
# Undo last operation
make undo MEDIA_PATH=/path/to/media

# View operation history
cat .organize_reports/execution_report_*.json

# Manual recovery from backups
cat .organize_backup/backup_*.json
```

### Production Monitoring

#### Health Checks
```bash
# Application health
python3 src/main.py test

# Docker health (if using Docker)
docker-compose ps
docker-compose logs media-organizer
```

#### Performance Metrics
- **Processing Speed**: ~100-500 files per minute
- **Memory Usage**: 256MB-1GB depending on library size
- **Disk I/O**: Sequential reads, minimal writes
- **API Calls**: ~1 call per show/movie collection

#### Maintenance Schedule
- **Daily**: Check execution reports
- **Weekly**: Validate configuration and test API connection
- **Monthly**: Review and clean up old backup files
- **Quarterly**: Update dependencies and review security

## Production Deployment

### Docker Production Setup

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  media-organizer:
    image: ai-media-organizer:latest
    volumes:
      - /host/media:/media:rw
      - /host/config:/app/config:ro
      - /host/logs:/app/logs:rw
    environment:
      - ENV_FILE=/app/config/.env
    restart: unless-stopped
    user: "1000:1000"
```

### Automated Processing

```bash
# Cron job for regular organization
# Add to crontab -e:
0 2 * * * /usr/bin/docker-compose -f /path/to/docker-compose.yml exec -T media-organizer organize-show /media/new-shows >> /var/log/media-organizer.log 2>&1
```

### Scaling for Large Libraries

- **Parallel Processing**: Organize shows individually for better performance
- **Batch Processing**: Use `make` commands for automated workflows
- **Resource Management**: Monitor memory usage for large collections
- **Network Storage**: Works with NFS, SMB, and other network storage

## Contributing

This is a production-ready project. Contributions welcome:

### Development Setup
```bash
make dev-setup                 # Complete development environment
make check                     # Run all quality checks
make format                    # Format code
```

### Contribution Guidelines
- Follow existing code style
- Add tests for new features
- Update documentation
- Use conventional commit messages

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Production Support

### Documentation
- [README.md](README.md) - Complete user guide
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Technical architecture
- [Makefile](Makefile) - Available commands and examples

### Monitoring
- Execution reports in `.organize_reports/`
- Backup information in `.organize_backup/`
- Application logs in `logs/` (Docker) or local directory

### Security
- Runs as non-root user in Docker
- No hardcoded credentials
- Secure API key handling
- File permission validation

---

## ⚠️ Production Guidelines

- **🔒 Security**: Always run with minimal required permissions
- **🧪 Testing**: Test with dry-run mode before production execution
- **📁 Backups**: Original filenames preserved, operation history maintained
- **📊 Monitoring**: Review execution reports and monitor resource usage
- **🔄 Recovery**: Full undo support with detailed backup information
- **📈 Scaling**: Processes 100-500 files per minute, scales with hardware