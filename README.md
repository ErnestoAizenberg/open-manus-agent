[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=FFD43B)](https://www.python.org/)
![FastAPI](https://img.shields.io/badge/FastAPI-0.103.0-000000?style=for-the-badge&logo=fastapi)
[![Playwright](https://img.shields.io/badge/Playwright-000000?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev)

# Open Manus Agent

A microservices-based agent for managing browsers via AI, featuring a macOS web UI and Telegram chat interface. Built on FastAPI for asynchronous operation.

## Quick Start

1. Clone the repository and install dependencies:
   ```shell
   git clone https://github.com/ErnestoAizenberg/open-manus-agent.git
   cd open-manus-agent
   pip install -r requirements.txt
   cp .env.example .env
   python run.py
   ```

## Components

- **Main Web UI**: [OM11MACOS](https://github.com/ErnestoAizenberg/OM11MACOS)
- **Telegram Integration**: [OM11TG](https://github.com/ErnestoAizenberg/OM11TG)
