# utils.py
import re

async def parse_chats(app, chats):
    monitored_chats = set()
    chats_map = {}

    for chat in chats:
        from_chats = chat["from"]
        to_chats = chat["to"]
        replace = chat.get("replace")

        if not isinstance(from_chats, list):
            from_chats = [from_chats]

        if not isinstance(to_chats, list):
            to_chats = [to_chats]

        # Resolve from_chats usernames to IDs
        resolved_from_chats = []
        for chat_id_or_username in from_chats:
            if isinstance(chat_id_or_username, int):
                resolved_from_chats.append(chat_id_or_username)
            else:
                # resolve username to ID
                chat_obj = await app.get_chat(chat_id_or_username)
                resolved_from_chats.append(chat_obj.id)

        # Resolve to_chats usernames to IDs
        resolved_to_chats = []
        for chat_id_or_username in to_chats:
            if isinstance(chat_id_or_username, int):
                resolved_to_chats.append(chat_id_or_username)
            else:
                chat_obj = await app.get_chat(chat_id_or_username)
                resolved_to_chats.append(chat_obj.id)

        # Build mapping
        for from_chat in resolved_from_chats:
            if from_chat not in chats_map:
                chats_map[from_chat] = {"to": set(), "replace": replace}

            for to_chat in resolved_to_chats:
                chats_map[from_chat]["to"].add(to_chat)

            monitored_chats.add(from_chat)

    return list(monitored_chats), chats_map

from pyrogram.types import Message, MessageEntity

def extract_token_address(message: Message) -> str | None:
    text = message.text or message.caption

	# # Try to match solscan or mevx URLs
    # url_match = re.search(r"(?:solscan\.io/token/|mevx\.io/solana/)([A-Za-z0-9]{32,50})", text)
    # if url_match:
    #     return url_match.group(1)
    
    entities = message.entities or []
    for entity in entities:
        if entity.type == "text_link":
            url = entity.url
            match = re.search(r"(?:solscan\.io/token/|mevx\.io/solana/)([A-Za-z0-9]{32,50})", url)
            if match:
                return match.group(1)
            
    # Fallback: generic token-like pattern
    generic_match = re.search(r"([A-Za-z0-9]{32,50})", text)
    if generic_match:
        return generic_match.group(1)

    return None