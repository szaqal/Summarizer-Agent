import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL     = os.environ["DATABASE_URL"]
MISTRAL_API_KEY  = os.environ["MISTRAL_API_KEY"]
SIGNAL_RECIPIENT = os.environ["SIGNAL_RECIPIENT"]
SIGNAL_SENDER    = os.environ["SIGNAL_SENDER"]
