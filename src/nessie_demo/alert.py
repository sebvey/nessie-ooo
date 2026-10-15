"""Dead-simple alerting for the demo. Prints a loud banner; optionally POSTs to a Slack webhook."""

from __future__ import annotations

import os

import requests


def alert(title: str, message: str) -> None:
    banner = "!" * 60
    print(f"\n{banner}\n🚨  {title}\n{message}\n{banner}\n")

    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if webhook:
        try:
            requests.post(webhook, json={"text": f"*{title}*\n{message}"}, timeout=5)
        except Exception as e:  # alerting must never crash the pipeline
            print(f"(slack notify failed: {e})")
