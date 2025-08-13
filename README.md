# 2FA Integration with Attendance System

## Team
- Samip Regmi
- Nayan Nembang
- Raju Behtwal 2025

## Algorithm for Frequency Generation

```python
datetime.utcnow().replace(second=0, microsecond=0).isoformat()+'Z'
```

Current time format: `'2025-07-16T12:06:00Z'`

We will use this time format string with user secret stored within `user.json`:

```python
combo = '2025-07-16T12:06:00Z-{user['secret']}'
```

This combo is encoded using SHA256 encoding:

```python
hashlib.sha256('2025-07-16T12:06:00Z-samipregmi'.encode()).hexdigest()
```

Encoded string in hex format:

```
c25ccc408ab329ac636533dd3e62ed3ac4ae7a07a65e450d44c8784f3460daaf
```

Take the last 4 parts by slicing (you can take any part, here we randomly take the last 4 parts):

```
daaf
```

Convert this hex data to integer:

```python
int('daaf', 16)
```

This gives a large number, but we want the range to be `0 <= int('daaf', 16) < 20`, so we apply modulus 20:

```python
sha_bias = int('daaf', 16) % 20
```

This is our first bias.

Use `now.minute` as the second bias.

The generated frequency will be:

```python
base_frequency + sha_bias + now.minute
```

## Introduction & Manual

### Code Running Instructions

1. Start SQL:
   ```bash
   startsql
   sql
   use 2fa;
   ```

2. Start server.py:
   ```bash
   python3 server.py
   ```

3. Start ngrok:
   ```bash
   ngrok tcp 12000
   ```

4. Change TCP URL in `loginmanager.py` and run:
   ```bash
   python3 loginmanager.py
   cloudflared --url http://localhost:5800
   ```

5. Change the URL in `index.html`:
   ```html
   href = "<cloudflared url>"
   ```

### Python Files Overview

- **app.py**
  - Removed redirect clutters and minified the user interface [Recently Added]
  - Flask backend
  - Renders `templates/index.html`
  - Includes Face Detection + Frequency Detection

- **loginmanager.py** [Recently Added]
  - Flask backend
  - Renders pages through `templates/`
  - Session-based login
  - Role-based session: 'admin' and normal user through `user.json`

- **ReportWrite.py**
  - Writes PNG image for users who have completed attendance using `server.py` [Recently Added]
  - Writes to `2fa.csv`
  - Writes to `{Date}.csv`
  - Saves CSV attendance data to Remote save
  - Saves image data to Remote save
  - Saves attendance data to MySQL

- **graph.py (DEPRECATED)**
  - Uses `2fa.csv` and generates `plot.png`

- **API.py (DEPRECATED)**
  - Flask backend
  - Handles POST requests on `/create`
  - Registers new users with USERNAME, SECRET CODE, and IMAGE
  - Appends to `user.json`

- **Socket.py (RENAMED TO server.py)**
  - Can be accessed with any POSIX-compliant terminal:
    - `telnet <tcp address> <tcp port>`
  - Authentication Added:
    - Requires username and secret code to login user
  - Commands:
    - `help`: Triggers help section
    - `<file>`: Available 2FA or `<date>`
    - `ask`: Calls Gemini API with access to `2fa.csv` and `user.json`, and answers related queries
    - `mark`: Marks attendance for specified user using `user['email']` and sends an OTP code
    - `check` : Checks if you are present today or not
    - `msee` : Lists recent messages on Server
    - `msend` : Sends Admin messages to Server

---

&copy; 2FA 2025