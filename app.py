import discord
import os
import asyncio
import re

file = open('key.txt', 'r')
my_key = file.read()
file.close()

client = discord.Client()



@client.event
async def on_ready():
    print('{} has connected to discord'.format(client.user))



@client.event
async def on_connect():
    block_list = []
    messaged_list = []
    for guild in client.guilds:
        print('connected to {}'.format(guild.name))
        channel_names = {channel: str(channel.type) for channel in guild.channels}
        channel = None
        for key, value in channel_names.items():
            if key.name.lower() == 'general' and value == 'text':
                channel = key

        members = [member for member in guild.members if member.bot is False and str(member.status) != 'offline']
        message_list = []
        for member in members:
            if member not in block_list and member not in messaged_list and channel is not None:
                message_list.append(member)
        message = '{} - Welcome to hydration bot! \n For help about the bot type ***!hydrate help***'\
            .format(''.join([x.mention for x in message_list]))
        await channel.send(message)
        messaged_list += message_list

@client.event
async def on_message(message):
    if message.content.lower().startswith('!hydrate'):
        msg = message.content.lower().replace('!hydrate', '').lstrip()
        if msg.startswith('help'):
            embed = discord.Embed(title='Hydration commands', description='A list of useful commands!')
            embed.add_field(name='!hydrate stop', value='This will remove you from the hydration list.')
            embed.add_field(name='!hydrate timer "time"', value='This will change the time in minutes between hydration reminders.')
            await message.channel.send(content=None, embed=embed)

client.run(my_key)
