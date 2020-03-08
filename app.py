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


block_list = []
messaged_list = []
user_timing = {}
usr_temp_time = {}

@client.event
async def on_connect(messaged_list=messaged_list, block_list=block_list):
    # Runs through and prints all the guilds it is connected to
    for guild in client.guilds:
        print('connected to {}'.format(guild.name))
        channel_names = {channel: str(channel.type) for channel in guild.channels} # Finds the names of the channels in the guild
        channel = None
        for key, value in channel_names.items(): # iterats through the channel names and tries to find a general channel
            if key.name.lower() == 'general' and value == 'text':
                channel = key # If not found No channel will be messaged

        # Searches for members that aren't bots and are online
        members = [member for member in guild.members if member.bot is False and str(member.status) != 'offline']
        message_list = []
        for member in members:
            # Goes through members who have never been messaged before and are not blocked and if the channel is not None
            if member not in block_list and member not in messaged_list and channel is not None:
                message_list.append(member)
                user_timing[member] = 60
        message = '{} - Welcome to hydration bot! \n For help about the bot type ***!hydrate help***'\
            .format(''.join([x.mention for x in message_list])) # @'s every user possible in one message
        await channel.send(message)
        messaged_list += message_list # Updates the global message list

@client.event
async def on_message(message):
    if message.content.lower().startswith('!hydrate'):
        msg = message.content.lower().replace('!hydrate', '').lstrip() # Strips any message that starts with hydrate to get the content
        if msg.startswith('help'):
            embed = discord.Embed(title='Hydration commands', description='A list of useful commands!')
            embed.add_field(name='!hydrate stop', value='This will remove you from the hydration list.')
            embed.add_field(name='!hydrate timer "time"', value='This will change the time in minutes between hydration reminders.')
            await message.channel.send(content=None, embed=embed) # An embed of all the commands

        if msg.startswith('stop'):
            block_list.append(message.author) # Adds the user to the block list and sends a notification
            await message.channel.send('{}, you will no longer receive notifications from this bot.'.format(message.author.name))

        if msg.startswith('timer'):
            msg = msg.replace('timer', '').lstrip().rstrip() #repalces timer and any rogue spaces from the front and back
            if msg.isdigit():
                user_timing[message.author] = int(msg) #If the entire message is a digit make the user timing that
                #Confirmation message
                await message.channel.send('{}, Your time between notifications have been changed to {}'
                                           .format(message.author.name, int(msg)))
            else:
                start = len(msg)+1
                for i in range(len(msg)):
                    if msg[i].isdigit():
                        start = i
                        break
                end = len(msg)+1
                if start < len(msg):
                    for j in range(start, len(msg)):
                        if not msg[j].isdigit():
                            end = j
                            break
                usr_temp_time[message.author] = msg[start:end]
                await message.channel.send('{}, is {} the correct time? \nPlease reply "Yes" to confirm'
                                           .format(message.author.name, msg[start:end]))

    if message.author in usr_temp_time.keys():
        if message.content.lower().startswith('yes'):
            user_timing[message.author] = usr_temp_time.get(message.author)
            await message.channel.send('{}, Your time between notifications have been changed to {}'
                                       .format(message.author.name, usr_temp_time.get(message.author)))
            usr_temp_time.pop(message.author)
        elif 'timer' not in message.content.lower():
            usr_temp_time.pop(message.author)
            await message.channel.send('Please try the command again')

client.run(my_key)
