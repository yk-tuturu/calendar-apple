from playwright.sync_api import sync_playwright
import time
import shutil
from pathlib import Path
import pygetwindow as gw
import pyautogui
import os

def hide_all_calendars_except_one(page, calendar_name):
    """Hide all calendars except the specified one"""
    try:
        # Wait for and check if calendar list exists
        calendar_list = page.locator("div[aria-label='My calendars']")
        
        try:
            calendar_list.wait_for(state='visible', timeout=2000)
        except:
            # Calendar list not visible, open the drawer
            print("opening drawer")
            page.click('div[aria-label="Main drawer"]')
            calendar_list.wait_for(state='visible', timeout=5000)
        
        # Wait for calendar items to load
        page.locator("div[aria-label='My calendars'] li").first.wait_for(state='visible', timeout=5000)
        time.sleep(3)
        
        calendar_items = page.locator("div[aria-label='My calendars'] li").all()
        print(len(calendar_items))
        
        for item in calendar_items:
            checkbox = item.locator('input[type="checkbox"]')
            
            # Get the calendar name
            cal_name = item.first.inner_text()
            print(f"Found calendar: {cal_name}")
            
            # Check only the calendar we want, uncheck others
            is_checked = checkbox.is_checked()
            
            if cal_name == calendar_name and not is_checked:
                print(f"Checking {cal_name}")
                checkbox.click()
                time.sleep(0.2)
            elif cal_name != calendar_name and is_checked:
                print(f"Unchecking {cal_name}")
                checkbox.click()
                time.sleep(0.2)
        
        #Close drawer
        print("closing drawer")
        page.click('div[aria-label="Main drawer"]')

                
    except Exception as e:
        print(f"Error hiding calendars: {e}")
        import traceback
        traceback.print_exc()

with sync_playwright() as p: 
    print("Log in into Google")
    
    base_profile = Path("./playwright-profile")

    if not os.path.exists(base_profile):
        os.makedirs(base_profile)


    context = p.chromium.launch_persistent_context(
        user_data_dir=base_profile,
        headless=False,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-infobars',  # Disable the automation infobar
            '--disable-extensions',
            '--disable-popup-blocking',
            '--disable-dev-shm-usage',  # Overcome limited resource problems
            '--no-sandbox',  # For stability
        ]
    )

    page = context.pages[0]
    page.goto('https://calendar.google.com')

    text = ""

    while not text == "done":
        text = input("Enter 'done' in the terminal once you are finished")


with sync_playwright() as p:
    screen_width, screen_height = pyautogui.size()
    half_width = screen_width // 3
    half_height = screen_height // 2
    
    base_profile = Path("./playwright-profile")
    
    contexts = []
    pages = []
    
    for i in range(6):
        profile_dir = f"./playwright-profile-{i}"
        
        if not Path(profile_dir).exists() and base_profile.exists():
            shutil.copytree(base_profile, profile_dir)
        
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-infobars',  # Disable the automation infobar
                '--disable-extensions',
                '--disable-popup-blocking',
                '--disable-dev-shm-usage',  # Overcome limited resource problems
                '--no-sandbox',  # For stability
            ]
        )
        
        page = context.pages[0]
        page.set_viewport_size({"width": half_width - 125, "height": half_height - 200})
        page.goto('https://calendar.google.com')

        time.sleep(1)
        
        all_windows = gw.getAllWindows()
        chrome_windows = [w for w in all_windows if 'Google Calendar' in w.title]
        
        if chrome_windows:
            window = chrome_windows[0]
            print(f"Found window: {window.title}")
            
            x = (i % 3) * half_width
            y = (i // 3) * half_height
            
            window.moveTo(x, y)

            window.resizeTo(half_width, half_height)
            page.evaluate("window.dispatchEvent(new Event('resize'))")
            time.sleep(0.5)
            
            print(f"Resized window {i} to position ({x}, {y})")
        
        contexts.append(context)
        pages.append(page)
        
        time.sleep(0.7)

        hide_all_calendars_except_one(page, str(i))
    
    # Wait for all calendars to load
    next_buttons = []
    for page in pages:
        next_button = page.locator("button[aria-label='Next week']")
        next_button.wait_for(state='visible', timeout=30000)
        next_buttons.append(next_button)
        page.keyboard.press('Control+0')
        time.sleep(0.2)
        
        # Set zoom to 50%
        page.keyboard.press('Control+0')
        time.sleep(0.2)
        for _ in range(4):
            page.keyboard.press('Control+Minus')
            time.sleep(0.1)
    
    # # Click consecutively across all windows
    try:
        for i in range(1100):
            for i in range(6):
                next_buttons[i].click()
            time.sleep(3)
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        for context in contexts:
            context.close()

    time.sleep(30000)