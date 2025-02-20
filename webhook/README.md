# UltraDNS Webhook Functions

This directory contains functions for handling UltraDNS push notifications and forwarding them to collaboration tools like Slack and Microsoft Teams.

## Overview

UltraDNS push notifications provide real-time telemetry events when changes occur. These functions act as intermediaries, processing the event data and reformatting it for the respective webhook endpoints.

## Functions

* `lambda-teams.py` – Formats telemetry events into an Adaptive Card and sends them to a Microsoft Teams webhook.
* `lambda-slack.py` – Converts telemetry events into Slack blocks and posts them to a Slack webhook.

## Requirements

* An UltraDNS account with push notifications enabled.
* A configured Slack or Teams webhook URL.
* AWS Lambda with appropriate permissions to execute web requests.

## Setup

1. Deploy the function to AWS Lambda.
2. Set the `WEBHOOK_URL` environment variable (Teams) or modify the `slack_webhook_url` in the script.
3. _(Optional)_ Use `WHITELISTED_IPS` to restrict incoming requests.
4. Configure UltraDNS to send push notifications to the Lambda endpoint.