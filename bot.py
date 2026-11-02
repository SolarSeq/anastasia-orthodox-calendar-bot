import os
from datetime import datetime, time
from zoneinfo import ZoneInfo

import aiohttp
import discord
from discord.ext import tasks
from dotenv import load_dotenv


load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# Post only to these two approved #calendar channels.
CHANNEL_IDS = (
    1235781438276763689,  # St Anne's
    1235794513281290320,  # ANDROIDS
)

EASTERN = ZoneInfo("America/New_York")
POST_TIME = time(hour=3, minute=0, tzinfo=EASTERN)

OCA_URL = "https://orthocal.info/api/oca/"

# Set SEND_ON_START=true temporarily in .env when testing.
SEND_ON_START = os.getenv("SEND_ON_START", "false").lower() == "true"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

startup_test_sent = False


def log(message: str) -> None:
    print(message, flush=True)


async def fetch_oca_json() -> dict:
    timeout = aiohttp.ClientTimeout(total=30)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(OCA_URL) as response:
            response.raise_for_status()
            return await response.json()


def build_message(data: dict) -> str:
    titles = data.get("titles") or []
    saints = data.get("saints") or []
    feasts = data.get("feasts") or []

    title_text = (
        ", ".join(titles)
        if titles
        else data.get("summary_title") or "an unknown feast day"
    )

    message = f"Good morning! Today is the {title_text}.\n"

    if saints:
        message += f"We commemorate: {', '.join(saints)}.\n"

    if feasts:
        message += f"It is the feast of: {', '.join(feasts)}.\n"

    if (data.get("fast_level") or 0) > 0:
        fast_description = data.get("fast_level_desc") or "fasting day"
        message += f"> Today is a fasting day: {fast_description}.\n"

        if (data.get("fast_exception") or 0) > 0:
            exception_description = data.get("fast_exception_desc")

            if exception_description:
                message += f"> *Note: {exception_description}*\n"

    # Discord messages are limited in length.
    if len(message) > 1900:
        message = message[:1897] + "..."

    return message


async def send_daily_message() -> None:
    now = datetime.now(EASTERN)

    log(
        "Starting daily post at "
        f"{now.strftime('%Y-%m-%d %I:%M:%S %p %Z')}"
    )

    try:
        data = await fetch_oca_json()
        message = build_message(data)
        log("Orthocal data retrieved successfully.")
    except Exception as error:
        log(f"Orthocal request failed: {type(error).__name__}: {error}")
        return

    for channel_id in CHANNEL_IDS:
        try:
            channel = client.get_channel(channel_id)

            if channel is None:
                channel = await client.fetch_channel(channel_id)

            guild_name = (
                channel.guild.name
                if getattr(channel, "guild", None)
                else "unknown server"
            )

            await channel.send(message)

            log(
                f"Message sent to #{channel.name} "
                f"in {guild_name} ({channel_id})."
            )

        except discord.Forbidden:
            log(f"Permission denied in channel {channel_id}.")

        except discord.NotFound:
            log(f"Channel {channel_id} was not found.")

        except Exception as error:
            log(
                f"Failed to send to channel {channel_id}: "
                f"{type(error).__name__}: {error}"
            )


@tasks.loop(time=POST_TIME, reconnect=True)
async def daily_post_loop() -> None:
    await send_daily_message()


@daily_post_loop.before_loop
async def before_daily_post_loop() -> None:
    await client.wait_until_ready()
    log("Daily scheduler is ready.")


@daily_post_loop.error
async def daily_post_error(error: Exception) -> None:
    log(f"Daily scheduler failed: {type(error).__name__}: {error}")


@client.event
async def on_ready() -> None:
    global startup_test_sent

    now = datetime.now(EASTERN)

    log(f"Logged in as {client.user} ({client.user.id}).")
    log(f"Current Eastern time: {now.strftime('%Y-%m-%d %I:%M:%S %p %Z')}")
    log("Daily posting time: 3:00 AM America/New_York.")
    log(f"Configured channel IDs: {CHANNEL_IDS}")

    if not daily_post_loop.is_running():
        daily_post_loop.start()

    if SEND_ON_START and not startup_test_sent:
        startup_test_sent = True
        log("SEND_ON_START is enabled; running one immediate test.")
        await send_daily_message()


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError(
            "DISCORD_TOKEN is missing. "
            "Put it in .env as DISCORD_TOKEN=..."
        )

    client.run(TOKEN)