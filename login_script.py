import json
import asyncio
from pyppeteer import launch
from datetime import datetime, timedelta
import aiofiles
import random
import requests
import os

# 从环境变量中获取 Telegram Bot Token 和 Chat ID
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def format_to_iso(date):
    return date.strftime('%Y-%m-%d %H:%M:%S')

async def delay_time(ms):
    await asyncio.sleep(ms / 1000)

# 全局浏览器实例
browser = None

# telegram消息
message = 'serv00&ct8自动化脚本运行\n'

async def login(username, password, panel):
    global browser

    page = None  # 确保 page 在任何情况下都被定义
    serviceName = 'ct8' if 'ct8' in panel else 'serv00'
    try:
        if not browser:
            browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])

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
            raise Exception('无法找到登录按钮')

        await page.waitForNavigation()

        is_logged_in = await page.evaluate('''() => {
            const logoutButton = document.querySelector('a[href="/logout/"]');
            return logoutButton !== null;
        }''')

        return is_logged_in

    except Exception as e:
        print(f'{serviceName}账号 {username} 登录时出现错误: {e}')
        return False

    finally:
        if page:
            await page.close()

async def main():
    global message
    message = 'serv00&ct8自动化脚本运行\n'

    try:
        async with aiofiles.open('accounts.json', mode='r', encoding='utf-8') as f:
            accounts_json = await f.read()
        accounts = json.loads(accounts_json)
    except Exception as e:
        print(f'读取 accounts.json 文件时出错: {e}')
        return

    successful_accounts = []  # 用于记录成功登录的账号
    all_logins_successful = True  # 用于标记是否所有账号登录成功

    for account in accounts:
        username = account['username']
        password = account['password']
        panel = account['panel']

        is_logged_in = await login(username, password, panel)

        if is_logged_in:
            now_beijing = format_to_iso(datetime.utcnow() + timedelta(hours=8))
            successful_accounts.append(username)
            print(f'{username} 于北京时间 {now_beijing} 登录成功！')
        else:
            all_logins_successful = False
            print(f'{username} 登录失败，请检查账号和密码是否正确。')

        delay = random.randint(1000, 8000)
        await delay_time(delay)

    if all_logins_successful:
        message += f'serv00账号: {", ".join(successful_accounts)}\n'
        message += f'于北京时间 {now_beijing} 登录成功！\n'
        message += '所有serv00账号登录完成！'
        print('所有serv00账号登录完成！')
        await send_telegram_message(message)
    else:
        print('有账号登录失败，请检查日志中的错误信息。')

    # 关闭浏览器实例
    if browser:
        await browser.close()

async def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown',  # 如果您希望使用Markdown格式
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"发送消息失败，状态码: {response.status_code}, 响应内容: {response.text}")
    except Exception as e:
        print(f"发送消息时出现错误: {e}")

if __name__ == '__main__':
    asyncio.run(main())
