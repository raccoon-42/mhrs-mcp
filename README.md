# MHRS MCP API

A Python-based API for interacting with the Turkish Ministry of Health's MHRS (Merkezi Hekim Randevu Sistemi) platform. This API provides automated appointment booking, checking, and management capabilities.

## Features

- Automatic authentication and session management
- Appointment booking with specific doctors
- Check available doctors, dates, and time slots
- Modify existing appointments
- Cancel appointments
- Revert appointment changes

## Installation

1. Clone the repository:
```bash
git clone https://github.com/raccoon-42/mhrs-mcp.git
cd mhrs-mcp
```

2. Install dependencies:
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

## API Endpoints

### Appointment Management

#### Book an Appointment
```python
result = appointment_book_tool(
    city="İZMİR",
    district="URLA",
    specialty="CİLDİYE",
    hospital="URLA",
    doctor_name="eylem",
    date="09.05.2025",
    time="15:40"
)
```

#### Check Available Doctors
```python
result = appointment_check_doctor_tool(
    city="İZMİR",
    district="URLA",
    specialty="CİLDİYE",
    hospital="URLA"
)
```

#### Check Available Dates
```python
result = appointment_check_dates_tool(
    city="İZMİR",
    district="URLA",
    specialty="CİLDİYE",
    hospital="URLA",
    doctor_name="eylem"
)
```

#### Check Available Hours
```python
result = appointment_check_hours_tool(
    city="İZMİR",
    district="URLA",
    specialty="CİLDİYE",
    hospital="URLA",
    doctor_name="eylem",
    date="09.05.2025"
)
```

### Appointment Actions

#### Cancel an Appointment
```python
result = cancel_appointment_tool("eylem")
```

#### Revert an Appointment
```python
result = revert_appointment_tool("eylem")
```

#### Get Active Appointments
```python
appointments = get_active_appointments_tool()
```

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