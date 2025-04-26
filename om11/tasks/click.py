from browser_manager import click as browser_click
import asyncio

def click(selector):
    asyncio.run(browser_click(selector))
    return f"Кликнул по элементу {selector}"