from playwright.sync_api import sync_playwright
import time
import shutil
from pathlib import Path
import pygetwindow as gw
import pyautogui

with sync_playwright() as p:
    screen_width, screen_height = pyautogui.size()
    half_width = screen_width // 2
    half_height = screen_height // 2
    
    base_profile = Path("./playwright-profile")
    
    contexts = []
    pages = []

    profile_dir = f"./playwright-profile-1"
        
    if not Path(profile_dir).exists() and base_profile.exists():
        shutil.copytree(base_profile, profile_dir)
    
    context = p.chromium.launch_persistent_context(
        user_data_dir=profile_dir,
        headless=False,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-infobars',  # Disable the automation infobar
            '--disable-extensions',
            '--disable-popup-blocking'
        ]
    )
    
    page = context.pages[0]
    page.goto('https://calendar.google.com')
    time.sleep(30000)
        
