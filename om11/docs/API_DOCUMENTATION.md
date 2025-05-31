# Overview
This documentation describes the API endpoints provided by the `APIHandler` class in the open-manus-agent project. The API allows for browser management and command execution through a FastAPI application.

## Base URL
All API endpoints are prefixed with `/api/`.

## Authentication
The API currently does not implement authentication. User identification is handled via `user_uuid` parameters.

## Endpoints

### 1. Check Agent Status
**Endpoint:** `GET /api/check-agent-status/`

**Description:**  
Checks if a browser instance is active for the specified user.

**Query Parameters:**
- `user_uuid` (string, required): Unique identifier for the user

**Response:**
```json
{
  "active": boolean
}
```

**Status Codes:**
- 200: Success
- 400: Missing required parameters

### 2. Start Browser
**Endpoint:** `POST /api/start-browser/`

**Description:**  
Initializes and connects a browser instance for the specified user.

**Query Parameters:**
- `ws_url` (string, required): WebSocket URL for running the user's browser
- `user_uuid` (string, required): Unique identifier for the user

**Response:**
```json
{
  "success": "Browser connected"
}
```
or
```json
{
  "error": "Browser is not connected, please check data and try again"
}
```

**Status Codes:**
- 200: Browser successfully connected
- 400: Missing required parameters
- 500: Error connecting browser

### 3. Execute Command
**Endpoint:** `POST /api/execute-command/`

**Description:**  
Executes a command using the user's browser instance.

**Query Parameters:**
- `message` (string, required): Command to execute
- `user_uuid` (string, required): Unique identifier for the user

**Response:**
Array of strings representing command results or error messages.

**Status Codes:**
- 200: Command executed successfully
- 400: Missing parameters or browser not connected
- 500: Error executing command

### 4. Close Browser
**Endpoint:** `POST /api/close-browser/`

**Description:**  
Closes the browser instance associated with the specified user.

**Query Parameters:**
- `user_uuid` (string, required): Unique identifier for the user

**Response:**
```json
{
  "status": "Browser closed"
}
```
or
```json
{
  "status": "No browser found for user"
}
```

## Data Structures

### BrowserManager
Manages browser instances with the following capabilities:
- Connecting to a browser via WebSocket
- Closing browser instances
- Maintaining browser state

### Tasks
Handles task execution with dependencies:
- `browser_manager`: BrowserManager instance
- `captcha_service`: Service for handling CAPTCHAs

### DBManager
Manages database operations with configuration directory:
- `config_dir`: Path to user configurations

### CaptchaService
Handles CAPTCHA-related operations with:
- `db_manager`: DBManager instance
- `config`: CaptchaConfig settings

## Error Handling
The API returns appropriate HTTP status codes and JSON error messages when operations fail. Common error responses include:
- Missing parameters (400)
- Browser not connected (400)
- Internal server errors (500)

## Logging
The API logs important events and errors using the provided logger instance.

## Dependencies
The API relies on:
- FastAPI for the web framework
- Custom modules for browser management, task handling, and user management

## Example Usage

### Starting a Browser
```bash
curl -X POST "http://localhost:8000/api/start-browser/?ws_url=ws://example.com&user_uuid=12345"
```

### Executing a Command
```bash
curl -X POST "http://localhost:8000/api/execute-command/?message=open+google.com&user_uuid=12345"
```

### Checking Browser Status
```bash
curl "http://localhost:8000/api/check-agent-status/?user_uuid=12345"
```

### Closing a Browser
```bash
curl -X POST "http://localhost:8000/api/close-browser/?user_uuid=12345"
```