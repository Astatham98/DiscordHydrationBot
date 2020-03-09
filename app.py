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
currently_playing = {}

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
                user_timing[member] = 60 #Adds a default member to every hour
        if len(message_list) > 0:
            message = '{} - Welcome to hydration bot! \n For help about the bot type ***!hydrate help***'\
                .format(''.join([x.mention for x in message_list])) # @'s every user possible in one message
            await channel.send(message)
            messaged_list += message_list # Updates the global message list

        await start_timer(channel) #Starts the timer for the user in general

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
                for i in range(len(msg)): #finds the first digit in the string
                    if msg[i].isdigit():
                        start = i
                        break
                end = len(msg)+1
                if start < len(msg):
                    for j in range(start, len(msg)): #finds the last digit in the string after the first
                        if not msg[j].isdigit():
                            end = j
                            break
                usr_temp_time[message.author] = msg[start:end] #adds the new timing to the temp dict
                await message.channel.send('{}, is {} the correct time? \nPlease reply "Yes" to confirm'
                                           .format(message.author.name, msg[start:end]))

    if message.author in usr_temp_time.keys():
        if message.content.lower().startswith('yes'): #If the message is yes and the author is in the temp list then add to user timing
            user_timing[message.author] = usr_temp_time.get(message.author)
            await message.channel.send('{}, Your time between notifications have been changed to {}'
                                       .format(message.author.name, usr_temp_time.get(message.author)))
            usr_temp_time.pop(message.author)
        elif 'timer' not in message.content.lower(): #Else remove it from the temp timing
            usr_temp_time.pop(message.author)
            await message.channel.send('Please try the command again')

@client.event
async def start_timer(channel=None):
    currently_playing = {user: user_timing.get(user, 60) for user in user_timing if user not in block_list
                         and str(user.status) != 'offline' and user.activity is not None} # Creates a list of playing players
    original_time = user_timing.copy() # a copy of the original user timings
    ml_per_min = 3700/3600 # The ml per hour that should be drunk
    while True:
        to_pop = []
        to_change = {}
        for user, time in currently_playing.items(): #Iterates through the playing players
            print(user, time)
            if original_time.get(user, 60) != user_timing.get(user, 60):
                original_time[user] = user_timing.get(user, 60) #Changes the original timer to the current one
                to_change[user] = user_timing.get(user, 60) - 1 #Changes the user timer and subtracts 1 for the minute that would go by

            if time == 0:
                try:
                    await channel.send(f"{user.mention}, I hope you're enjoying {user.activity.name} but don't forget to stay hydrated. "
                               f"\nYou should have drunk {int(round(user_timing.get(user, 60)*ml_per_min)*1.5)}ml since the last mention.") #Check if there is a name for the game
                    currently_playing[user] = user_timing.get(user, 60)
                except AttributeError:
                    if user.activity is not None:
                        await channel.send(
                            f"{user.mention}, I hope you're enjoying {user.activity} but don't forget to stay hydrated. " #if no name return the game
                            f"\nYou should have drunk {int(round(user_timing.get(user, 60) * ml_per_min) * 1.5)}ml since the last mention.")
                    else:
                        to_pop.append(user) #if no activity add to be removed

            else:
                if currently_playing.get(user, 'No') != 'No':
                    currently_playing[user] = time - 1 #if users still in the playing minus the time by 1

        [currently_playing.pop(x) for x in to_pop] #pop the non playing users
        for key, val in to_change.items():
            currently_playing[key] = val #Change to the new timer amount

        currently_playing = {user: currently_playing.get(user, 60) for user in user_timing if user not in block_list
                             and str(user.status) != 'offline' and user.activity is not None} #Updates currently playing list to new users who are playing

        await asyncio.sleep(60) #Waits 60 seconds

client.run(my_key)