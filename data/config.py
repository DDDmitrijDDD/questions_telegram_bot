import os
from dotenv import load_dotenv

load_dotenv()

# токен бота
BOT_TOKEN = str(os.getenv("TOKEN"))

#url bitrix24
webhook_url = str(os.getenv("webhook_url"))

# flood-time
rate = 1

# id админов
admins_id = [int(os.getenv("admins_id"))]