import sys
import os
import re
import discord
import requests
import asyncio


CLIENT = discord.Client()
NEWS_CHANNELS = []
TOKEN = os.environ.get('DISCORD_TOKEN')


if not TOKEN:
    try:
        from Credentials import TOKEN
    except ModuleNotFoundError:
        if len(sys.argv) > 1:
            TOKEN = sys.argv[1]
        else:
            raise Exception('Specify discord token either with a credentials.py file or as an argument.')


def _purge_check(message):
    if message.author.id != CLIENT.user.id:
        return True
    return False


async def _find_log_message(channel, starting_string):
    async for message in CLIENT.logs_from(channel, limit=20):
        if message.author.id == CLIENT.user.id and message.content.startswith(starting_string):
            return True

async def my_background_task():
    await asyncio.sleep(10)
    await CLIENT.wait_until_login()
    while not CLIENT.is_closed:
        request = requests.get('https://playoverwatch.com/en-us/game/patch-notes/pc/')
        match = re.search('<a href="#([a-zA-Z\-0-9]*)"><h3 class="blog-sidebar-article-title">([a-zA-Z 0-9\.]*)</h3>', request.text)
        if match:
            channels_told = 0
            for channel in NEWS_CHANNELS:
                update_in_logs = await _find_log_message(channel, match.group(2))
                if not update_in_logs:
                    message = match.group(2) + ' now out! read the patch notes here:\nhttps://playoverwatch.com/en-us/game/patch-notes/pc/#' + match.group(1)
                    channels_told += 1
                    await CLIENT.send_message(channel, message)
            print('Told ' + str(channels_told) + ' channels.')
        else:
            print('Could not find update notes in HTML.')
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
                NEWS_CHANNELS.append(channel)


CLIENT.loop.create_task(my_background_task())
CLIENT.run(TOKEN)
