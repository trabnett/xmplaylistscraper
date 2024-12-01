import os
from dotenv import load_dotenv
from pathlib import Path

from scraper import XMPlaylistScraper

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

scraper_mod = XMPlaylistScraper(refresh_token=os.environ.get("REFRESH_TOKEN"))

scraper_mod.scrape()

print('COMPLETE!')



