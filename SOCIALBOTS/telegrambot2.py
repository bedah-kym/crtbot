import os
import json
import asyncio
import logging
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.errors.rpcerrorlist import UserAlreadyParticipantError
from telethon.tl.functions.channels import JoinChannelRequest
from aiohttp import ClientSession
import aiosqlite

# Load environment variables
load_dotenv()

# Telegram API credentials
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
SESSION_NAME = os.getenv('SESSION_NAME', 'userbot_session')

# Notification bot credentials
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Database path
DB_PATH = os.getenv('DB_PATH', 'telegram_messages.db')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define group configuration directly
config = {
    'groups': [
        {
            'username': 'crtjob2',  # Replace with actual group usernames
            'keywords': ['dump', 'pump']
        },
        {
            'username':'mizanicrt',
            'keywords':['crypto','pump']
        }
        # Add more groups as needed
    ]
}

# Database setup
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER,
                group_name TEXT,
                sender_id INTEGER,
                message TEXT,
                date TEXT
            )
        ''')
        await db.commit()


async def save_message(group_id, group_name, sender_id, message, date):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO messages (group_id, group_name, sender_id, message, date) VALUES (?, ?, ?, ?, ?)",
            (group_id, group_name, sender_id, message, date)
        )
        await db.commit()
        logger.debug(f"Message saved to database from group {group_name}.")

# Asynchronous notification system
async def send_notification(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    async with ClientSession() as session:
        async with session.post(url, data=payload) as response:
            if response.status != 200:
                logger.error(f"Failed to send notification: {response.status}")
            else:
                logger.info("Notification sent.")

async def join_groups(client, group_keywords):
    logger.info("Starting to join groups...")
    for group in config['groups']:
        group_username = group['username']
        logger.info(f"Attempting to join group: {group_username}")
        keywords = group.get('keywords', [])
        try:
            # Get the group entity
            group_entity = await client.get_entity(group_username)
            logger.debug(f"Retrieved entity for {group_username}: {group_entity}")
            # Attempt to join the group
            try:
                await client(JoinChannelRequest(group_entity))
                logger.info(f"Joined group: {group_entity.title}")
            except UserAlreadyParticipantError:
                logger.info(f"Already a participant of group: {group_entity.title}")
            group_id = group_entity.id
            group_name = group_entity.title
            group_keywords[group_id] = {
                'keywords': keywords,
                'username': getattr(group_entity, 'username', None),
                'title': group_name
            }
            logger.info(f"Added group '{group_name}' to monitoring list.")
        except Exception as e:
            logger.error(f"Error joining group '{group_username}': {e}")

async def process_history(client, group_id, group_info, limit=100):
    logger.info(f"Processing history for group: {group_info['title']}")
    async for message in client.iter_messages(group_id, limit=limit):
        if message.text:
            message_text = message.text
            sender_id = message.sender_id
            date = message.date
            # Check if message contains any of the keywords
            keywords = group_info['keywords']
            for keyword in keywords:
                if keyword.lower() in message_text.lower():
                    await save_message(group_id, group_info['title'], sender_id, message_text, date.isoformat())
                    notification_text = f"Keyword '{keyword}' found in {group_info['title']}:\n{message_text}"
                    await send_notification(notification_text)
                    logger.info(notification_text)
                    break
                
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

async def main():
    # Initialize database
    await init_db()
    logger.info("Database initialized.")

    # Start client
    logger.info("Starting Telegram client...")
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()
    logger.info("Telegram client started.")

    # Build a mapping of chat_id to keywords and group info
    group_keywords = {}

    # Join groups
    logger.info("Joining groups...")
    await join_groups(client, group_keywords)
    logger.info("Groups joined.")

    # Process history
    logger.info("Processing message history...")
    for group_id, group_info in group_keywords.items():
        await process_history(client, group_id, group_info, limit=100)
    logger.info("Message history processed.")

    # Register event handler
    @client.on(events.NewMessage)
    async def new_message_handler(event):
        group_id = event.chat_id
        if group_id in group_keywords:
            message_text = event.raw_text
            sender_id = event.sender_id
            date = event.date
            group_info = group_keywords[group_id]
            group_name = group_info['title']
            # Check if message contains any of the keywords
            keywords = group_info['keywords']
            for keyword in keywords:
                if keyword.lower() in message_text.lower():
                    await save_message(group_id, group_name, sender_id, message_text, date.isoformat())
                    notification_text = f"Keyword '{keyword}' found in {group_name}:\n{message_text}"
                    await send_notification(notification_text)
                    logger.info(notification_text)
                    break  # Process the first matching keyword

    # Start listening for new messages
    logger.info("Userbot is running...")
    await client.run_until_disconnected()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("User interrupted the script. Shutting down...")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
