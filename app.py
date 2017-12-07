import sys
import os
import re
import discord
import requests
import asyncio


CLIENT = discord.Client()
TOKEN = os.environ.get('DISCORD_TOKEN')


if not TOKEN:
    try:
        from Credentials import TOKEN
    except ModuleNotFoundError:
        if len(sys.argv) > 1:
            TOKEN = sys.argv[1]
        else:
            raise Exception('Specify discord token either with a credentials.py file or as an argument.')


async def _find_log_message(channel, starting_string):
    async for message in CLIENT.logs_from(channel, limit=20):
        if message.author.id == CLIENT.user.id and message.content.startswith(starting_string):
            return True

def _find_channels_to_tell(server_list):
    channel_list = []
    for server in server_list:
        for channel in server.channels:
            if str(channel) == 'overwatch-news':
                channel_list.append(channel)
    return channel_list

async def overwatch_news_timer():
    await asyncio.sleep(10)
    await CLIENT.wait_until_login()
    while not CLIENT.is_closed:
        request = requests.get('https://playoverwatch.com/en-us/game/patch-notes/pc/')
        match = re.search('<a href="#([a-zA-Z\-0-9]*)"><h3 class="blog-sidebar-article-title">([a-zA-Z 0-9\.]*)</h3>', request.text)
        if match:
            channel_list = _find_channels_to_tell(CLIENT.servers)
            channels_told = []
            for channel in channel_list:
                update_in_logs = await _find_log_message(channel, match.group(2))
                if not update_in_logs:
                    message = match.group(2) + ' now out! read the patch notes here:\nhttps://playoverwatch.com/en-us/game/patch-notes/pc/#' + match.group(1)
                    channels_told.append(str(channel.server))
                    await CLIENT.send_message(channel, message)
            
            if channels_told:
                print('Told the following servers: ' + ', '.join(channels_told))
            else:
                print('Told no servers.')
        else:
            print('Could not find update notes in HTML.')
        await asyncio.sleep(60)


@CLIENT.event
async def on_ready():
    print('Logged in as')
    print(CLIENT.user.name)
    print(CLIENT.user.id)
    print('------')


CLIENT.loop.create_task(overwatch_news_timer())
CLIENT.run(TOKEN)
