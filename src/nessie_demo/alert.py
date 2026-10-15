"""Dead-simple alerting for the demo. Prints a loud panel; optionally POSTs to a Slack webhook."""

from __future__ import annotations

import os

import requests
from rich.panel import Panel

from .display import console


def alert(title: str, message: str) -> None:
    console.print(Panel(message, title=f"🚨 {title}", title_align="left", border_style="bold red", padding=(1, 2), expand=False))

    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if webhook:
        try:
            requests.post(webhook, json={"text": f"*{title}*\n{message}"}, timeout=5)
        except Exception as e:  # alerting must never crash the pipeline
            console.print(f"(slack notify failed: {e})")
