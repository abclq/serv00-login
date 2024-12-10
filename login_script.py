import asyncio
from pyppeteer import launch
from datetime import datetime, timedelta
import random
import requests
import os

# Telegram 配置
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '你的默认Token')  # 如果需要，替换为实际的Token
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '你的默认Chat ID')  # 如果需要，替换为实际的Chat ID

def format_to_iso(date):
    return date.strftime('%Y-%m-%d %H:%M:%S')

async def delay_time(ms):
    await asyncio.sleep(ms / 1000)

# 全局浏览器实例
browser = None

# Telegram 消息
message = 'serv00&ct8自动化脚本运行\n'

async def login(username, password, panel):
    global browser

    page = None
    try:
        if not browser:
            browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])

        page = await browser.newPage()
        url = f'https://{panel}/login/?next=/'
        await page.goto(url)

        # 输入用户名和密码
        username_input = await page.querySelector('#id_username')
        if username_input:
            await page.evaluate('''(input) => input.value = ""''', username_input)
        await page.type('#id_username', username)
        await page.type('#id_password', password)

        # 点击登录按钮
        login_button = await page.querySelector('#submit')
        if login_button:
            await login_button.click()
        else:
            raise Exception('无法找到登录按钮')

        await page.waitForNavigation()

        # 检查是否登录成功
        is_logged_in = await page.evaluate('''() => {
            const logoutButton = document.querySelector('a[href="/logout/"]');
            return logoutButton !== null;
        }''')

        return is_logged_in

    except Exception as e:
        print(f'账号 {username} 登录时出现错误: {e}')
        return False

    finally:
        if page:
            await page.close()

async def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown',
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Telegram 消息发送成功！")
        else:
            print(f"Telegram 消息发送失败，错误代码: {response.status_code}, 错误信息: {response.text}")
    except Exception as e:
        print(f"发送 Telegram 消息时发生错误: {e}")

async def main():
    global message
    message = 'serv00&ct8自动化脚本运行\n'

    # 登录信息
    username = "MichaelCarter"
    password = "dmW9ao1K34wH0Qbs)lDL"
    panel = "panel14.serv00.com"

    # 当前北京时间
    now_beijing = format_to_iso(datetime.utcnow() + timedelta(hours=8))

    # 登录尝试
    is_logged_in = await login(username, password, panel)

    if is_logged_in:
        message += f'serv00账号: {username}\n'
        message += f'于北京时间 {now_beijing} 登录成功！\n'
        message += '所有serv00账号登录完成！'
        print(f'{username} 于北京时间 {now_beijing} 登录成功！')
    else:
        message += f'{username} 登录失败，请检查账号和密码是否正确。'
        print(f'{username} 登录失败，请检查账号和密码是否正确。')

    # 发送 Telegram 消息
    await send_telegram_message(message)

    # 关闭浏览器
    if browser:
        await browser.close()

# 启动主程序
if __name__ == "__main__":
    asyncio.run(main())
