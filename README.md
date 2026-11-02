# Anastasia — Orthodox Calendar Discord Bot

Anastasia is a Python Discord bot that retrieves Eastern Orthodox calendar information and automatically posts a daily summary to configured Discord channels.

The bot is deployed as an always-on Docker Compose service and currently posts at 3:00 AM America/New_York.

## Features

- Retrieves daily calendar data from the OrthoCal API
- Posts feast, saint, and fasting information to Discord
- Supports multiple configured Discord channels
- Uses timezone-aware scheduling
- Handles API and Discord errors
- Uses environment variables to keep credentials out of source code
- Runs continuously with Docker Compose and automatic restart

## Technology

- Python 3.11
- discord.py
- aiohttp
- Docker and Docker Compose
- Ubuntu Linux
- OrthoCal API

## Configuration

Copy .env.example to .env and provide your own Discord bot token. The real .env file is excluded from Git and Docker image builds.

## Current Deployment

Anastasia is a functioning production service running continuously on an Ubuntu server.

## Roadmap

- Multi-server Discord installation
- Per-server channel configuration
- /setup command for Discord administrators
- Persistent server settings
- Public Discord invite flow

## Project Background

Anastasia evolved from an earlier personal modification of an existing Orthodox Discord calendar bot. The current implementation was rebuilt in Python with asynchronous API access, timezone-aware scheduling, Docker deployment, and environment-based configuration.

This project was developed with AI-assisted coding. Requirements, integration decisions, testing, deployment, server administration, and production troubleshooting were performed as part of the project development process.
