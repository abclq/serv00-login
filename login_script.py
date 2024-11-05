async def main():
    global message
    message = 'serv00&ct8自动化脚本运行\n'

    successful_accounts = []  # 用于存储所有成功登录的账号

    try:
        async with aiofiles.open('accounts.json', mode='r', encoding='utf-8') as f:
            accounts_json = await f.read()
        accounts = json.loads(accounts_json)
    except Exception as e:
        print(f'读取 accounts.json 文件时出错: {e}')
        return

    for account in accounts:
        username = account['username']
        password = account['password']
        panel = account['panel']

        serviceName = 'ct8' if 'ct8' in panel else 'serv00'
        is_logged_in = await login(username, password, panel)

        if is_logged_in:
            now_utc = format_to_iso(datetime.utcnow())
            now_beijing = format_to_iso(datetime.utcnow() + timedelta(hours=8))
            successful_accounts.append(username)
            print(f'{serviceName}账号 {username} 于北京时间 {now_beijing} 登录成功！')
        else:
            message += f'{serviceName}账号 {username} 登录失败，请检查{serviceName}账号和密码是否正确。\n'
            print(f'{serviceName}账号 {username} 登录失败，请检查{serviceName}账号和密码是否正确。')

        delay = random.randint(1000, 8000)
        await delay_time(delay)

    if successful_accounts:
        accounts_list = ' ， '.join(successful_accounts)
        message += f'{serviceName}账号: {accounts_list} 于北京时间 {now_beijing} 登录成功！\n'
        message += '所有serv00账号登录完成！'
        print(f'{serviceName}账号: {accounts_list} 于北京时间 {now_beijing} 登录成功！')
        print('所有serv00账号登录完成！')
        await send_telegram_message(message)
    else:
        print('没有账号登录成功，请检查日志中的错误信息。')

    # 关闭浏览器实例
    if browser:
        await browser.close()
