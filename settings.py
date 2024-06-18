from dotenv import load_dotenv
import os
import core.db as db

load_dotenv()

DB_URL = os.getenv('DB_URL', 'postgresql:///sesame')
SENTRY_DSN = os.environ.get('SENTRY_DSN', None)

db.connect(DB_URL)
