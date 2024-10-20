import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
ADMINS = list(map(int, os.getenv('ADMINS').split(',')))

#print(f"API_TOKEN: {API_TOKEN}")
#print(f"ADMINS: {ADMINS}")