import logging

from pyrogram import filters, idle
from pyrogram.types import Message

from bot import app, config, sudo_users
from bot.helper.utils import parse_chats, extract_token_address

# Optional: define keywords to filter messages
KEYWORDS = config.get("keywords", [])  # e.g., ["urgent", "alert", "breaking"]

async def main():
    async with app:
        logging.info("Bot started.")
        
        # Resolve usernames and parse chat mapping
        monitored_chats, chats_map = await parse_chats(app, config["chats"])
        
        # Log monitoring info
        logging.info(f"Monitoring chats: {monitored_chats}")

        @app.on_message(filters.chat(monitored_chats) & filters.incoming)
        async def forward_handler(_, message: Message):
            if message.chat.id not in monitored_chats:
                return # do nothing for unmonitored chats
            
            text = message.text or message.caption or ""
            
            # If keywords are defined, filter messages
            if KEYWORDS and not any(kw.lower() in text.lower() for kw in KEYWORDS):
                return  # Skip message if it doesn't contain any keyword

            token = extract_token_address(message)
            if not token:
                return # Skip if no token address found

            from_chat_id = message.chat.id
            destinations = chats_map.get(from_chat_id, {}).get("to", [])

            # Forward or copy message
            for to_chat_id in destinations:
                try:
                    await app.send_message(to_chat_id, token)
                except Exception as e:
                    logging.error(f"Failed to forward to {to_chat_id}: {e}")

        # Keep bot running
        await idle()

if __name__ == "__main__":
    app.run(main())

