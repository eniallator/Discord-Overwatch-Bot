import sys
import os.path
import re
import discord
import requests
import asyncio

CLIENT = discord.Client()
NEWS_CHANNEL = []
VERSION_FILE = 'latest_version.txt'
TOKEN = None

try:
    from Credentials import TOKEN
except ModuleNotFoundError:
    if len(sys.argv) > 1:
        TOKEN = sys.argv[1]
    else:
        raise Exception('Specify discord token either with a credentials.py file or as an argument.')


def _update_version_file(new_contents):
    with open(VERSION_FILE, 'w') as ver_file:
        ver_file.write(new_contents)

async def my_background_task():
    await asyncio.sleep(20)
    await CLIENT.wait_until_login()
    while not CLIENT.is_closed:
        request = requests.get('https://playoverwatch.com/en-us/game/patch-notes/pc/')
        match = re.search('<a href="#([a-zA-Z\-0-9]*)"><h3 class="blog-sidebar-article-title">([a-zA-Z 0-9\.]*)</h3>', request.text)
        loc_version = ''
        if os.path.isfile(VERSION_FILE):
            with open(VERSION_FILE, 'r') as ver_file:
                loc_version = ver_file.read()
        if not loc_version or loc_version != match.group(2):
            _update_version_file(match.group(2))
            message = match.group(2) + ' now out! read the patch notes here:\nhttps://playoverwatch.com/en-us/game/patch-notes/pc/#' + match.group(1)
            print(message)
            if NEWS_CHANNEL:
                await CLIENT.send_message(NEWS_CHANNEL[0], message)
        else:
            print('No new version.')
        await asyncio.sleep(60)


@CLIENT.event
async def on_ready():
    print('Logged in as')
    print(CLIENT.user.name)
    print(CLIENT.user.id)
    print('------')
    for server in CLIENT.servers:
        for channel in server.channels:
            if str(channel) == 'overwatch-news':
                NEWS_CHANNEL.append(channel)

CLIENT.loop.create_task(my_background_task())
CLIENT.run(TOKEN)
