import asyncio
from pyppeteer import launch
from datetime import datetime, timedelta
import random
import requests

# Telegram 配置
TELEGRAM_TOKEN = "7056296159:AAGDFwNTx8OA0dzv1S0WN0CDh3iinBipeXs"
TELEGRAM_CHAT_ID = 685294921

def format_to_iso(date):
    """格式化时间为 ISO 格式"""
    return date.strftime('%Y-%m-%d %H:%M:%S')

async def delay_time(ms):
    """以毫秒为单位的随机延迟"""
    await asyncio.sleep(ms / 1000)

# 全局浏览器实例
browser = None

async def login(username, password, panel):
    """尝试登录并返回是否成功"""
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
    """发送 Telegram 消息"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
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
    """主程序入口"""
    success_accounts = []
    failed_accounts = []

    # 登录信息
    accounts = [
        {"username": "MichaelCarter", "password": "dmW9ao1K34wH0Qbs)lDL", "panel": "panel14.serv00.com"},
        {"username": "MorefieldPaul", "password": "jpvg37Z!Ur^oy(S*nic!", "panel": "panel15.serv00.com"},
        {"username": "Subbillson", "password": "Gu@y77S94M6!kbJ(wQYb", "panel": "panel15.serv00.com"},
        {"username": "Abrount", "password": "&E@m)P4e*^7(QuczNoGC", "panel": "panel15.serv00.com"},
        {"username": "TheresaFught", "password": "@kL^0E#sA^6%OhC3xnmI", "panel": "panel15.serv00.com"},
        {"username": "Thkeresa", "password": "9IpOtvMe43bXyK6DRKp4", "panel": "panel14.serv00.com"}
    ]

    # 当前北京时间
    now_beijing = format_to_iso(datetime.utcnow() + timedelta(hours=8))

    for account in accounts:
        username = account["username"]
        password = account["password"]
        panel = account["panel"]

        # 加入随机延迟
        random_delay = random.randint(2000, 5000)  # 2到5秒随机延迟
        print(f'随机延迟 {random_delay} ms...')
        await delay_time(random_delay)

        # 登录尝试
        is_logged_in = await login(username, password, panel)

        if is_logged_in:
            success_accounts.append({"username": username, "time": now_beijing})
            print(f'{username} 于北京时间 {now_beijing} 登录成功！')
        else:
            failed_accounts.append(username)
            print(f'{username} 登录失败，请检查账号和密码是否正确。')

    # 构建消息
    message = "✅ *serv00&ct8自动化脚本运行完成！*\n\n"
    if success_accounts:
        message += "✔️ *登录成功：*\n"
        for i, account in enumerate(success_accounts, 1):
            message += f"{i}. {account['username']} — 登录时间: {account['time']}\n"
        message += "\n"

    if failed_accounts:
        message += "❌ *登录失败：*\n"
        for account in failed_accounts:
            message += f"- {account}\n"
        message += "\n"

    message += f"📌 *总结：{len(success_accounts)} 个账号登录成功，{len(failed_accounts)} 个账号登录失败。*"

    # 发送 Telegram 消息
    await send_telegram_message(message)

    # 关闭浏览器
    if browser:
        await browser.close()

# 启动主程序
if __name__ == "__main__":
    asyncio.run(main())
