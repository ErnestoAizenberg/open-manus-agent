![Python](https://img.shields.io/badge/Python-3.7-a2d2ff) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115.1-ffafcc) ![SQLAlchemy](https://img.shields.io/badge/Flask--SQLAlchemy-3.1.1-bde0fe) ![redis](https://img.shields.io/badge/redis-latest-cddaaf)

# Open Manus Agent

A microservices-based agent for managing browsers via AI, featuring a macOS web UI and Telegram chat interface. Built on FastAPI for asynchronous operation.

## Quick Start

1. Clone the repository and install dependencies:
   ```shell
   git clone https://github.com/ErnestoAizenberg/open-manus-agent.git
   cd open-manus-agent
   pip install -r requirements.txt
   python run.py
   ```

2. Configure ports and settings during runtime (press Enter for defaults)

3. Access the application at: http://localhost:5000/

## Components

- **Main Web UI**: [OM11MACOS](https://github.com/ErnestoAizenberg/OM11MACOS)
- **Telegram Integration**: [OM11TG](https://github.com/ErnestoAizenberg/OM11TG)
