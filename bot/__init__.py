import logging
import os
import sys
from os import environ
import toml

from pyrogram import Client
from .helper.validator import validate_config
from jsonschema import ValidationError

# Setup logging
log_level = environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    format="[%(levelname)s]\t%(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=log_level,
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

# Load config
config = None
if os.path.exists("config.toml"):
    config = toml.load("config.toml")
    logging.info("Loaded config.toml")
elif os.environ.get("CONFIG"):
    config = toml.loads(environ["CONFIG"])
    logging.info("Loaded config from environment variable")
else:
    logging.error("File config.toml and CONFIG env variable not found. Exiting...")
    sys.exit(1)

# Validate config
try:
    validate_config(config)
except ValidationError as error:
    logging.error(f"Invalid config: {error.message}")
    logging.info("Please read the documentation carefully and configure the bot properly.")
    sys.exit(1)

logging.info("Initializing bot client...")

# Create the Pyrogram client (not started here)
if config["pyrogram"].get("bot_token"):
    app = Client(
        "bot",
        api_id=config["pyrogram"]["api_id"],
        api_hash=config["pyrogram"]["api_hash"],
        bot_token=config["pyrogram"]["bot_token"],
    )
else:
    app = Client(
        "bot",
        api_id=config["pyrogram"]["api_id"],
        api_hash=config["pyrogram"]["api_hash"],
        session_string=config["pyrogram"]["session_string"],
    )

# Load sudo users
sudo_users = config["pyrogram"].get("sudo_users", [])
