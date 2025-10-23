<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/requests-2.31.0-3776AB?style=flat-square&logo=python&logoColor=white" alt="requests">
  <img src="https://img.shields.io/badge/httpx-0.25.0-00B4AB?style=flat-square&logo=python&logoColor=white" alt="httpx">
  <img src="https://img.shields.io/badge/uvicorn-0.23.0-6E00F7?style=flat-square&logo=python&logoColor=white" alt="uvicorn">
  <img src="https://img.shields.io/badge/FastAPI-0.103.0-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/openai->=0.1.0-412991?style=flat-square&logo=openai&logoColor=white" alt="openai">
  <img src="https://img.shields.io/badge/playwright-1.39.0-FF6B00?style=flat-square&logo=playwright&logoColor=white" alt="playwright">
  <img src="https://img.shields.io/badge/websockets-11.0.0-FF4D4D?style=flat-square&logo=websocket&logoColor=white" alt="websockets">
</p> 

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
