# MHRS MCP API

A Python-based API for interacting with the Turkish Ministry of Health's MHRS (Merkezi Hekim Randevu Sistemi) platform. This API provides automated appointment booking, checking, and management capabilities through Claude AI integration.

## Features

- Automatic authentication and session management
- Appointment booking with specific doctors
- Check available doctors, dates, and time slots
- Modify existing appointments
- Cancel appointments
- Revert appointment changes

## Prerequisites

- Python 3.8 or higher
- Firefox browser installed
- Geckodriver (Firefox WebDriver) installed and in your PATH

### Installing Geckodriver

#### macOS (using Homebrew)
```bash
brew install geckodriver
```

#### Linux
```bash
# Download the latest version
wget https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz

# Extract the archive
tar -xvzf geckodriver-v0.33.0-linux64.tar.gz

# Make it executable
chmod +x geckodriver

# Move to PATH
sudo mv geckodriver /usr/local/bin/
```

#### Windows
1. Download geckodriver from [Mozilla's GitHub releases](https://github.com/mozilla/geckodriver/releases)
2. Extract the executable
3. Add the directory containing geckodriver.exe to your system PATH

## Installation

1. Clone the repository:
```bash
git clone https://github.com/raccoon-42/mhrs-mcp.git
cd mhrs-mcp
```

2. Create and activate a virtual environment:
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Claude Desktop Configuration

To integrate with Claude Desktop, you need to configure the `claude_desktop_config.json` file. This file should be located at:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

Add the following configuration to your `claude_desktop_config.json`:

```json
{
    "mhrs": {
        "command": "uv",
        "args": [
            "--directory",
            "/path/to/your/mhrs-mcp/core/",
            "run",
            "api.py"
        ],
        "env": {
            "MHRS_USERNAME": "your_username",
            "MHRS_PASSWORD": "your_password"
        }
    }
}
```

Replace:
- `/path/to/your/mhrs-mcp/core/` with the actual path to your project's core directory
- `your_username` with your MHRS username
- `your_password` with your MHRS password

Note: Make sure to keep your credentials secure and never commit this file to version control.

## Usage with Claude AI

Once configured, you can interact with the MHRS system through Claude AI. Simply ask Claude to help you with:
- Finding available doctors
- Checking appointment dates
- Booking appointments
- Managing existing appointments
- Canceling appointments

Claude will handle the API calls and provide you with the results in a conversational manner.

## Development

The project uses a modular architecture:

- `core/clients/`: Contains client implementations (BrowserClient, AuthClient)
- `core/services/`: Contains business logic services
- `utils/`: Contains utility functions and status codes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 