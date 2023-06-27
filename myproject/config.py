from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.environ.get("TOKEN")
DJANGO_SERVER_URL = os.environ.get("DJANGO_SERVER_URL")