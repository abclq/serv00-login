import json
import asyncio
from pyppeteer import launch
from datetime import datetime, timedelta
import aiofiles
import random
import requests
import os

# Load environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("Telegram bot token and chat ID must be set in the environment variables.")

def format_to_iso(date):
    return date.strftime('%Y-%m-%d %H:%M:%S')

async def delay_time(ms):
    await asyncio.sleep(ms / 1000)

# Login function
async def login(username, password, panel, browser):
    page = None
    serviceName = 'ct8' if 'ct8' in panel else 'serv00'
    try:
        page = await browser.newPage()
        url = f'https://{panel}/login/?next=/'
        await page.goto(url)

        username_input = await page.querySelector('#id_username')
        if username_input:
            await page.evaluate('''(input) => input.value = ""''', username_input)

        await page.type('#id_username', username)
        await page.type('#id_password', password)

        login_button = await page.querySelector('#submit')
        if login_button:
            await login_button.click()
        else:
            raise Exception('Login button not found.')

        await page.waitForNavigation()

        is_logged_in = await page.evaluate('''() => {
            const logoutButton = document.querySelector('a[href="/logout/"]');
            return logoutButton !== null;
        }''')

        return is_logged_in

    except Exception as e:
        print(f'{serviceName} account {username} encountered an error during login: {e}')
        return False

    finally:
        if page:
            await page.close()

async def main():
    message = 'serv00&ct8 Automation Script Run\n'

    try:
        # Load account data from JSON file
        async with aiofiles.open('accounts.json', mode='r', encoding='utf-8') as f:
            accounts_json = await f.read()
        accounts = json.loads(accounts_json)
    except Exception as e:
        print(f'Error reading accounts.json: {e}')
        return

    # Launch browser
    browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
    try:
        for account in accounts:
            username = account['username']
            password = account['password']
            panel = account['panel']
            serviceName = 'ct8' if 'ct8' in panel else 'serv00'

            # Attempt login for each account
            is_logged_in = await login(username, password, panel, browser)
            now_utc = format_to_iso(datetime.utcnow())
            now_beijing = format_to_iso(datetime.utcnow() + timedelta(hours=8))

            if is_logged_in:
                success_message = f'{serviceName} account {username} successfully logged in at Beijing Time {now_beijing} (UTC {now_utc})!'
                message += success_message + '\n'
                print(success_message)
            else:
                failure_message = f'{serviceName} account {username} login failed. Check username and password.'
                message += failure_message + '\n'
                print(failure_message)

            # Introduce a random delay between logins to avoid blocking
            delay = random.randint(1000, 8000)
            await delay_time(delay)

        # Send summary message to Telegram
        message += f'All {serviceName} account logins completed!'
        await send_telegram_message(message)
        print(f'All {serviceName} account logins completed!')

    finally:
        # Ensure the browser is closed
        await browser.close()

# Send Telegram message
async def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'reply_markup': {
            'inline_keyboard': [
                [
                    {
                        'text': 'Issue Feedback❓',
                        'url': 'https://t.me/yxjsjl'
                    }
                ]
            ]
        }
    }
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"Failed to send message to Telegram: {response.text}")
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")

if __name__ == '__main__':
    asyncio.run(main())
