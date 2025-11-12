# External IP Checker

## What is it?

External IP Checker monitors your external IP address and alerts you via Pushover when:
- Your external IP doesn't match DNS A-records (DNS mode)
- Your external IP changes from a previously saved value (Change detection mode)

This is useful for monitoring dynamic DNS setups or detecting unexpected IP changes.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Y8Y078U1V)

## Features

- **Two monitoring modes:**
  - `check_ip_based_on_dns.py` - Compares current external IP with DNS A-records
  - `check_ip_based_on_previous_value.py` - Alerts when IP changes from last known value
- **Pushover notifications** - Get instant alerts on your phone/device
- **Robust error handling** - Graceful handling of network and DNS failures
- **Logging** - Detailed logs for debugging and auditing
- **Type hints** - Modern Python code for better IDE support
- **Timeout protection** - API requests have configurable timeouts

## Installation

### Requirements
- Python 3.6+
- `dnspython` - for DNS resolution (DNS mode only)
- `requests` - for HTTP requests
- `chump` - for Pushover notifications

Install dependencies:
```bash
pip install dnspython requests chump
```

## Configuration

### Setup Pushover

1. Create a [Pushover](https://pushover.net/) account
2. Create an application at https://pushover.net/apps/build
3. Get your User Key from your Pushover account

### Configure the Scripts

Configuration files go in `/config/` directory.

#### DNS Mode: `check_ip_based_on_dns.ini`

```ini
[COMMON]
URL = domain.org

[PUSHOVER]
USER_KEY = your_pushover_user_key
TOKEN_API = your_pushover_app_token
SOUND = pushover
```

#### Change Detection Mode: `check_ip_based_on_previous_value.ini`

```ini
[PUSHOVER]
USER_KEY = your_pushover_user_key
TOKEN_API = your_pushover_app_token
SOUND = pushover
```

A file `/config/saved_ip.txt` will be created automatically to track the previous IP.

## Usage

### DNS Mode
```bash
python check_ip_based_on_dns.py
```
Monitors if your external IP matches the DNS A-records for the configured domain.

### Change Detection Mode
```bash
python check_ip_based_on_previous_value.py
```
Alerts when your external IP changes from the last known value.

## Running Periodically

### Using Cron
Add to your crontab to run every 5 minutes:
```bash
*/5 * * * * cd /path/to/app && python check_ip_based_on_dns.py
```

### Using Docker
The scripts are designed to run in containers with `/config` volume mounted for persistent configuration.

## Code Enhancements (v2024.11.12)

- ✅ Added type hints for better code clarity
- ✅ Added docstrings for all classes and methods
- ✅ Improved error handling with specific exception types
- ✅ Fixed incorrect `except IOError or FileNotFoundError` syntax
- ✅ Added timeout protection to API requests
- ✅ Proper logging with module logger instead of logging module directly
- ✅ Refactored file I/O to use context managers consistently
- ✅ Better separation of concerns with private methods
- ✅ More informative error messages
- ✅ Removed unused variables
- ✅ Improved code readability with better variable naming

## License

MIT License - See LICENSE file

---

**Last Updated:** 2024-11-12
