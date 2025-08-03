# Weather Dashboard Installation Guide

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Quick Installation](#quick-installation)
3. [Detailed Installation Steps](#detailed-installation-steps)
4. [Configuration Setup](#configuration-setup)
5. [API Key Setup](#api-key-setup)
6. [Troubleshooting](#troubleshooting)
7. [Platform-Specific Instructions](#platform-specific-instructions)
8. [Advanced Installation](#advanced-installation)

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **Memory**: 4GB RAM
- **Storage**: 500MB available disk space
- **Internet**: Broadband connection for API access

### Recommended Requirements
- **Operating System**: Latest stable version
- **Python**: 3.9 or higher
- **Memory**: 8GB RAM
- **Storage**: 1GB available disk space
- **Internet**: High-speed connection for optimal performance

### Python Dependencies
The application requires the following Python packages:
- `ttkbootstrap>=1.14.0` - Modern GUI framework
- `numpy` - Numerical computing
- `pandas` - Data manipulation
- `matplotlib` - Data visualization
- `requests` - HTTP client
- `python-dotenv` - Environment variable management

## Quick Installation

### For Users (Simplified Setup)

1. **Download the Application**
   ```bash
   git clone https://github.com/yourusername/weather-dashboard.git
   cd weather-dashboard
   ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up API Key**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenWeatherMap API key
   ```

4. **Run the Application**
   ```bash
   python main.py
   ```

### For Developers (Full Setup)

1. **Clone and Set Up Environment**
   ```bash
   git clone https://github.com/yourusername/weather-dashboard.git
   cd weather-dashboard
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run Tests**
   ```bash
   pytest test/
   ```

5. **Start Development Server**
   ```bash
   python main.py
   ```

## Detailed Installation Steps

### Step 1: Python Installation

#### Windows
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer with "Add Python to PATH" checked
3. Verify installation:
   ```bash
   python --version
   pip --version
   ```

#### macOS
1. Install using Homebrew:
   ```bash
   brew install python
   ```
2. Or download from [python.org](https://www.python.org/downloads/)
3. Verify installation:
   ```bash
   python3 --version
   pip3 --version
   ```

#### Linux (Ubuntu/Debian)
1. Update package list:
   ```bash
   sudo apt update
   ```
2. Install Python:
   ```bash
   sudo apt install python3 python3-pip python3-venv
   ```
3. Verify installation:
   ```bash
   python3 --version
   pip3 --version
   ```

### Step 2: Git Installation

#### Windows
1. Download Git from [git-scm.com](https://git-scm.com/download/win)
2. Run the installer with default settings
3. Verify installation:
   ```bash
   git --version
   ```

#### macOS
1. Install using Homebrew:
   ```bash
   brew install git
   ```
2. Or download from [git-scm.com](https://git-scm.com/download/mac)
3. Verify installation:
   ```bash
   git --version
   ```

#### Linux
1. Install Git:
   ```bash
   sudo apt install git
   ```
2. Verify installation:
   ```bash
   git --version
   ```

### Step 3: Clone Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/weather-dashboard.git

# Navigate to project directory
cd weather-dashboard

# Verify project structure
ls -la
```

### Step 4: Create Virtual Environment

#### Windows
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation (should show venv path)
where python
```

#### macOS/Linux
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (should show venv path)
which python
```

### Step 5: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

### Step 6: Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit environment file
# On Windows: notepad .env
# On macOS/Linux: nano .env or vim .env
```

## Configuration Setup

### Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Required: OpenWeatherMap API Key
API_KEY=your_32_character_api_key_here

# Optional: API Configuration
BASE_URL=https://api.openweathermap.org/data/2.5/weather
FORECAST_URL=https://api.openweathermap.org/data/2.5/forecast
UNITS=imperial

# Optional: Database Configuration
DATABASE_PATH=data/weather.db

# Optional: Performance Settings
REQUEST_TIMEOUT=10
MAX_RETRIES=3
MIN_REQUEST_INTERVAL=1.0

# Optional: Logging
LOG_LEVEL=INFO
```

### Configuration Options

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `API_KEY` | OpenWeatherMap API key | - | Yes |
| `BASE_URL` | Weather API base URL | OpenWeatherMap URL | No |
| `UNITS` | Temperature units | `imperial` | No |
| `DATABASE_PATH` | SQLite database location | `data/weather.db` | No |
| `REQUEST_TIMEOUT` | API timeout in seconds | `10` | No |
| `MAX_RETRIES` | Maximum retry attempts | `3` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |

### Database Setup

The application automatically creates the SQLite database on first run:

```bash
# Database will be created at:
data/weather.db

# Database contains:
# - User settings and preferences
# - Saved locations
# - Cached weather data
# - Application logs
```

## API Key Setup

### Getting an OpenWeatherMap API Key

1. **Create Account**
   - Visit [OpenWeatherMap](https://openweathermap.org/)
   - Click "Sign Up" and create a free account

2. **Get API Key**
   - Log in to your account
   - Navigate to "My API Keys"
   - Copy your API key (32 characters)

3. **Configure API Key**
   ```bash
   # Edit .env file
   API_KEY=your_actual_api_key_here
   ```

### API Key Verification

Test your API key:

```bash
# Run the application
python main.py

# Check logs for API connection status
tail -f data/weather_dashboard.log
```

### API Key Troubleshooting

**Common Issues:**
- **Invalid API Key**: Ensure the key is exactly 32 characters
- **API Key Not Set**: Check that `.env` file exists and contains `API_KEY=`
- **Rate Limit Exceeded**: Free tier allows 60 calls/minute
- **Account Not Activated**: New accounts may take 2 hours to activate

## Troubleshooting

### Common Installation Issues

#### Python Not Found
**Problem**: `python` or `python3` command not found
**Solutions**:
```bash
# Windows: Add Python to PATH
# macOS/Linux: Install Python
sudo apt install python3  # Ubuntu/Debian
brew install python       # macOS

# Verify installation
python --version
python3 --version
```

#### pip Not Found
**Problem**: `pip` command not found
**Solutions**:
```bash
# Install pip
python -m ensurepip --upgrade

# Or install separately
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

#### Virtual Environment Issues
**Problem**: Virtual environment not activating
**Solutions**:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Verify activation
which python  # Should show venv path
```

#### Dependency Installation Failures
**Problem**: `pip install` fails
**Solutions**:
```bash
# Upgrade pip
pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v

# Install system dependencies (Linux)
sudo apt install python3-dev build-essential
```

### Runtime Issues

#### Import Errors
**Problem**: Module not found errors
**Solutions**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

#### GUI Issues
**Problem**: Application window doesn't appear
**Solutions**:
```bash
# Check tkinter installation
python -c "import tkinter; tkinter._test()"

# Install tkinter (Linux)
sudo apt install python3-tk

# Check display settings (Linux)
echo $DISPLAY
```

#### Database Issues
**Problem**: Database errors or corruption
**Solutions**:
```bash
# Remove database and restart
rm data/weather.db
python main.py

# Check file permissions
ls -la data/

# Fix permissions
chmod 755 data/
chmod 644 data/weather.db
```

### Network Issues

#### API Connection Failures
**Problem**: Cannot connect to weather APIs
**Solutions**:
```bash
# Test internet connection
ping api.openweathermap.org

# Check firewall settings
# Windows: Allow Python through firewall
# macOS: System Preferences > Security & Privacy
# Linux: Check iptables rules

# Test API directly
curl "https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_API_KEY"
```

#### Proxy Issues
**Problem**: Behind corporate firewall/proxy
**Solutions**:
```bash
# Set proxy environment variables
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080

# Or configure in Python
import os
os.environ['HTTP_PROXY'] = 'http://proxy.company.com:8080'
```

### Performance Issues

#### Slow Application Startup
**Problem**: Application takes too long to start
**Solutions**:
```bash
# Check system resources
top
htop

# Disable unnecessary startup features
# Edit config.py to disable auto-updates

# Profile startup time
python -m cProfile -o startup.prof main.py
```

#### Memory Issues
**Problem**: High memory usage
**Solutions**:
```bash
# Monitor memory usage
ps aux | grep python

# Reduce cache size in config.py
CACHE_DURATION = 1800  # 30 minutes instead of 1 hour

# Clear cache manually
rm -rf data/cache/
```

## Platform-Specific Instructions

### Windows Installation

#### Prerequisites
1. **Windows 10 or later**
2. **Python 3.8+** from [python.org](https://www.python.org/downloads/)
3. **Git** from [git-scm.com](https://git-scm.com/download/win)

#### Installation Steps
```cmd
# Open Command Prompt as Administrator
# Clone repository
git clone https://github.com/yourusername/weather-dashboard.git
cd weather-dashboard

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
notepad .env

# Run application
python main.py
```

#### Windows-Specific Issues
- **PATH Issues**: Ensure Python is added to PATH during installation
- **Firewall**: Allow Python through Windows Firewall
- **Antivirus**: Add application directory to antivirus exclusions
- **Permissions**: Run Command Prompt as Administrator if needed

### macOS Installation

#### Prerequisites
1. **macOS 10.14 or later**
2. **Homebrew** (recommended) or Python from [python.org](https://www.python.org/downloads/)
3. **Git** (included with Xcode Command Line Tools)

#### Installation Steps
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and Git
brew install python git

# Clone repository
git clone https://github.com/yourusername/weather-dashboard.git
cd weather-dashboard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env

# Run application
python main.py
```

#### macOS-Specific Issues
- **Gatekeeper**: Allow application in System Preferences > Security & Privacy
- **Permissions**: Grant accessibility permissions if needed
- **Homebrew**: Update Homebrew regularly with `brew update`

### Linux Installation

#### Ubuntu/Debian
```bash
# Update system
sudo apt update && sudo apt upgrade

# Install dependencies
sudo apt install python3 python3-pip python3-venv git

# Clone repository
git clone https://github.com/yourusername/weather-dashboard.git
cd weather-dashboard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env

# Run application
python main.py
```

#### CentOS/RHEL/Fedora
```bash
# Install dependencies
sudo dnf install python3 python3-pip git  # Fedora
sudo yum install python3 python3-pip git  # CentOS/RHEL

# Follow same steps as Ubuntu
```

#### Linux-Specific Issues
- **Display Issues**: Set `export DISPLAY=:0` if needed
- **Permissions**: Use `chmod` to set correct file permissions
- **Dependencies**: Install system packages for GUI support
- **Desktop Integration**: Create desktop shortcut if desired

## Advanced Installation

### Docker Installation

#### Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tk \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p data

# Expose port (if needed)
EXPOSE 8000

# Run application
CMD ["python", "main.py"]
```

#### Build and Run Docker Container
```bash
# Build image
docker build -t weather-dashboard .

# Run container
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  weather-dashboard
```

### System Service Installation

#### Create Systemd Service
```ini
# /etc/systemd/system/weather-dashboard.service
[Unit]
Description=Weather Dashboard
After=network.target

[Service]
Type=simple
User=weather
WorkingDirectory=/opt/weather-dashboard
ExecStart=/opt/weather-dashboard/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Install as Service
```bash
# Create user
sudo useradd -r -s /bin/false weather

# Copy application
sudo cp -r weather-dashboard /opt/
sudo chown -R weather:weather /opt/weather-dashboard

# Enable and start service
sudo systemctl enable weather-dashboard
sudo systemctl start weather-dashboard

# Check status
sudo systemctl status weather-dashboard
```

### Development Installation

#### Install Development Dependencies
```bash
# Install additional development tools
pip install -r requirements-dev.txt

# Install code quality tools
pip install black isort pylint pytest pytest-cov

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

#### Development Environment Setup
```bash
# Configure Git hooks
git config core.hooksPath .githooks

# Set up development environment
python -c "import weather_dashboard; print('Setup complete')"

# Run tests
pytest test/ -v --cov=core --cov=gui
```

### Production Installation

#### Production Checklist
- [ ] Use production API key
- [ ] Set appropriate log levels
- [ ] Configure database backup
- [ ] Set up monitoring
- [ ] Configure firewall rules
- [ ] Set up SSL certificates (if web interface)
- [ ] Configure automated updates
- [ ] Set up error reporting

#### Production Configuration
```bash
# Production .env file
API_KEY=your_production_api_key
LOG_LEVEL=WARNING
DATABASE_PATH=/var/weather/data/weather.db
REQUEST_TIMEOUT=15
MAX_RETRIES=5
BACKUP_ENABLED=true
MONITORING_ENABLED=true
```

---

*This installation guide covers all major installation scenarios. For additional help, refer to the troubleshooting section or create an issue on the project repository.*