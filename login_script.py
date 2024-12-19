import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import random
import requests

# Telegram 配置
TELEGRAM_TOKEN = "7056296159:AAGDFwNTx8OA0dzv1S0WN0CDh3iinBipeXs"
TELEGRAM_CHAT_ID = 685294921

def format_to_iso(date):
    """Format datetime to ISO format."""
    return date.strftime('%Y-%m-%d %H:%M:%S')

async def delay_time(ms):
    """Delay for a random duration in milliseconds."""
    await asyncio.sleep(ms / 1000)

async def login(playwright, username, password, panel):
    """Attempt login and return success status."""
    browser = await playwright.chromium.launch(headless=True, args=['--no-sandbox'])
    context = await browser.new_context()
    page = await context.new_page()

    try:
        url = f'https://{panel}/login/?next=/'
        await page.goto(url)

        # Fill username and password
        await page.fill('#id_username', username)
        await page.fill('#id_password', password)

        # Click login button
        await page.click('#submit')
        await page.wait_for_timeout(3000)

        # Check if login was successful
        is_logged_in = await page.locator('a[href="/logout/"]').count() > 0
        return is_logged_in
    except Exception as e:
        print(f'Error logging in with account {username}: {e}')
        return False
    finally:
        await context.close()
        await browser.close()

async def send_telegram_message(message):
    """Send a Telegram message."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown',
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Telegram message sent successfully!")
        else:
            print(f"Failed to send Telegram message: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

async def main():
    """Main entry point."""
    success_accounts = []
    failed_accounts = []

    # Account login information
    accounts = [
        {"username": "MichaelCarter", "password": "dmW9ao1K34wH0Qbs)lDL", "panel": "panel14.serv00.com"},
        {"username": "MorefieldPaul", "password": "jpvg37Z!Ur^oy(S*nic!", "panel": "panel15.serv00.com"},
        {"username": "Subbillson", "password": "Gu@y77S94M6!kbJ(wQYb", "panel": "panel15.serv00.com"},
        {"username": "Abrount", "password": "&E@m)P4e*^7(QuczNoGC", "panel": "panel15.serv00.com"},
        {"username": "TheresaFught", "password": "@kL^0E#sA^6%OhC3xnmI", "panel": "panel15.serv00.com"},
        {"username": "Thkeresa", "password": "9IpOtvMe43bXyK6DRKp4", "panel": "panel14.serv00.com"},
        {"username": "Laint19628200", "password": "DL1HSufZ4GjL3HhlOMgl", "panel": "panel15.serv00.com"},
        {"username": "Makined4864", "password": "zDM0iroI2uzw5D1l6Trv", "panel": "panel15.serv00.com"}
    ]

    # Current Beijing time
    now_beijing = format_to_iso(datetime.utcnow() + timedelta(hours=8))

    async with async_playwright() as playwright:
        for account in accounts:
            username = account["username"]
            password = account["password"]
            panel = account["panel"]

            # Add random delay
            random_delay = random.randint(2000, 5000)  # 2 to 5 seconds
            print(f'Random delay {random_delay} ms...')
            await delay_time(random_delay)

            # Attempt login
            is_logged_in = await login(playwright, username, password, panel)

            if is_logged_in:
                success_accounts.append({"username": username, "time": now_beijing})
                print(f'{username} logged in successfully at Beijing time {now_beijing}!')
            else:
                failed_accounts.append(username)
                print(f'{username} login failed. Please check username and password.')

        # Construct message
        message = "\u2705 *serv00&ct8 automation script completed!*\n\n"
        if success_accounts:
            message += "\u2714\ufe0f *Successful logins:*\n"
            for i, account in enumerate(success_accounts, 1):
                message += f"{i}. {account['username']} - Login time: {account['time']}\n"
            message += "\n"

        if failed_accounts:
            message += "\u274c *Failed logins:*\n"
            for account in failed_accounts:
                message += f"- {account}\n"
            message += "\n"

        message += f"\ud83d\udccc *Summary: {len(success_accounts)} accounts logged in successfully, {len(failed_accounts)} accounts failed to login.*"

        # Send Telegram message
        await send_telegram_message(message)

# Run main program
if __name__ == "__main__":
    asyncio.run(main())
