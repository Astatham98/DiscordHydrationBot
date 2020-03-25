import discord
import os
import asyncio
from database_bot import databse_bot
from discord.ext import commands

my_key = os.environ.get('DISCORD_KEY')

bot = commands.Bot(command_prefix='!hydrate ')
bot.remove_command("help")

db_dir = r"BOT.db"
db_bot = databse_bot(db_dir)


@bot.event
async def on_connect():
    print('{} has connected to discord'.format(bot.user))
    await bot.change_presence(activity=discord.Game(name='!hydrate help'))


block_list = db_bot.get_blocked_users()
messaged_list = db_bot.get_messaged_users()
user_timing = db_bot.get_user_timings()
usr_temp_time = {}
guild_channel = db_bot.get_guilds()


async def message_users(message_list, guild):
    if len(message_list) > 0:
        for member in message_list:
            dm_channel = await member.create_dm()  # Creates a dm for the non-messaged users
            await dm_channel.send('{} - Welcome to hydration bot in {}! \n '  # sends the users a message
                                  'For help about the bot type ***!hydrate help*** in the channel.'
                                  .format(member.name, guild.name))

            db_bot.insert_values_bot([str(member), 1, 60, 0])


@bot.event
async def on_ready():
    # Runs through and prints all the guilds it is connected to
    for guild in bot.guilds:
        print('connected to {}'.format(guild.name))

        # Finds the names of the channels in the guild
        channel_names = {channel: str(channel.type) for channel in guild.channels}
        if str(guild) in guild_channel:  # Checks if the guild is in the guild channel
            # Find channel from channel name
            channel_name = [channel for channel in guild.channels if str(channel) == guild_channel.get(str(guild))][0]
            guild_channel[guild] = channel_name  # Inserts a new entry of type guild: channel
            guild_channel.pop(str(guild))  # pops the string variant
            channel = channel_name  # Makes channel the channel name
        else:  # If not in the guild channel then do following
            channel = None
            for key, value in channel_names.items():  # iterates through the channel names and tries to find a general
                # channel
                if key.name.lower() == 'general' or key.name.lower == 'bot' and value == 'text':
                    channel = key  # If not found No channel will be messaged
                    guild_channel[guild] = channel  # Insert into the dictionary
                    db_bot.insert_values_guild([str(guild), str(channel)])  # Update database

        # Searches for members that aren't bots and are online
        members = [member for member in guild.members if member.bot is False]
        message_list = []
        for member in members:
            if str(member) in user_timing:
                user_timing[member] = user_timing.pop(str(member))
            # Goes through members who have never been messaged before and are not blocked and if the channel is not None
            if str(member) not in block_list and str(member) not in messaged_list and channel is not None and str(
                    member.status) != 'offline':
                message_list.append(member)
                user_timing[member] = 60  # Adds a default member to every hour

        await message_users(message_list, guild)

    db_bot.read_database()

    await start_timer()  # Starts the timer for the user in general


@bot.event
async def start_timer():
    print('started_timer')
    currently_playing = {user: user_timing.get(user, 60) for user in user_timing if user not in block_list
                         and str(
        user.status) != 'offline' and user.activity is not None}  # Creates a list of playing players

    original_time = user_timing.copy()  # a copy of the original user timings
    original_guild = guild_channel.copy()

    ml_per_min = 3700 / 3600  # The ml per hour that should be drunk
    while True:
        to_pop = []
        to_change = {}
        for user, time in currently_playing.items():  # Iterates through the playing players
            print(user, time)
            print([(key.name, val.name) for key, val in guild_channel.items()])
            if original_time.get(user, 60) != user_timing.get(user, 60):
                original_time[user] = user_timing.get(user, 60)  # Changes the original timer to the current one
                # Changes the user timer and subtracts 1 for the minute that would go by
                to_change[user] = int(user_timing.get(user, 60)) - 1

            if original_guild.get(user.guild) != guild_channel.get(user.guild):
                original_guild[user.guild] = guild_channel.get(user.guild)

            if time == 0:
                channel = guild_channel.get(user.guild)
                try:
                    await channel.send(
                        f"{user.mention}, I hope you're enjoying {user.activity.name} but don't forget to stay hydrated. "
                        f"\nYou should have drunk {int(round(user_timing.get(user, 60) * ml_per_min) * 1.5)}ml since the last mention.")  # Check if there is a name for the game
                    currently_playing[user] = user_timing.get(user, 60)
                except AttributeError:
                    if user.activity is not None:
                        await channel.send(
                            f"{user.mention}, I hope you're enjoying {user.activity} but don't forget to stay hydrated. "  # if no name return the game
                            f"\nYou should have drunk {int(round(user_timing.get(user, 60) * ml_per_min) * 1.5)}ml since the last mention.")
                    else:
                        to_pop.append(user)  # if no activity add to be removed

            else:
                if currently_playing.get(user, 'No') != 'No':
                    currently_playing[user] = time - 1  # if users still in the playing minus the time by 1

        [currently_playing.pop(x) for x in to_pop]  # pop the non playing users
        for key, val in to_change.items():
            currently_playing[key] = val  # Change to the new timer amount

        # Updates currently playing list to new users who are playing
        currently_playing = {user: currently_playing.get(user, 60) for user in user_timing if user not in block_list
                             and str(user.status) != 'offline' and user.activity is not None}

        await asyncio.sleep(60)  # Waits 60 seconds


@commands.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(title='Hydration commands', description='A list of useful commands!')
    embed.add_field(name='!hydrate stop', value='This will remove you from the hydration list.')
    embed.add_field(name='!hydrate timer "time"',
                    value='This will change the time in minutes between hydration reminders.')
    embed.add_field(name='!hydrate channel <channel-name>',
                    value="This will change the channel the bot will post in")
    await ctx.send(content=None, embed=embed)  # An embed of all the commands


@commands.command(pass_context=True)
async def stop(ctx):
    if str(ctx.author) not in block_list:
        block_list.append(str(ctx.author))  # Adds the user to the block list and sends a notification
        db_bot.update_ban(str(ctx.author), True)
        await ctx.send('{}, you will no longer receive notifications from this bot.'.format(ctx.author.name))
    else:
        block_list.remove(str(ctx.author))
        db_bot.update_ban(str(ctx.author), False)
        await ctx.send('{}, you will receive notifications from this bot again.'.format(ctx.author.name))


@commands.command(pass_context=True)
async def timer(ctx, arg=''):
    msg = arg.strip() if arg != '' else ''
    if msg.isdigit():
        user_timing[ctx.author] = int(msg)  # If the entire message is a digit make the user timing that
        db_bot.update_timer(str(ctx.author), int(msg))
        # Confirmation message
        await ctx.channel.send('{}, Your time between notifications have been changed to {}'
                               .format(ctx.author.name, int(msg)))
    else:
        start = len(msg) + 1
        for i in range(len(msg)):  # finds the first digit in the string
            if msg[i].isdigit():
                start = i
                break
        end = len(msg) + 1
        if start < len(msg):
            for j in range(start, len(msg)):  # finds the last digit in the string after the first
                if not msg[j].isdigit():
                    end = j
                    break
        usr_temp_time[ctx.author] = msg[start:end]  # adds the new timing to the temp dict
        if msg != '':
            await ctx.channel.send('{}, is {} the correct time? \nPlease reply "Yes" to confirm'
                                   .format(ctx.author.name, msg[start:end]))
        else:
            await ctx.send(f"{ctx.author.name}, please enter a time")


@commands.command(pass_context=True)
async def channel(ctx, arg=''):
    userRoles = ctx.author.roles
    admin_bools = [True for role in userRoles if role.permissions.administrator is True] + [False]
    admin_bools = admin_bools[0]
    admin_bools = True if (ctx.author == ctx.guild.owner) else admin_bools

    if admin_bools:
        desired_channel = arg.replace('channel', '').strip()
        if desired_channel in [str(x) for x in ctx.guild.channels]:
            desired_channel = [channe for channe in ctx.guild.channels if str(channe) == desired_channel][0]
            guild_channel[ctx.guild] = desired_channel
            db_bot.update_guild(str(ctx.guild), str(desired_channel))

            await ctx.channel.send(f"The bot will now send notifcations to {desired_channel.name}")
        else:
            if arg != '':
                await ctx.channel.send(f"The channel {desired_channel}, either doesn't exist or there is a typo.")
            else:
                await ctx.channel.send("Please enter a channel.")
    else:
        await ctx.channel.send(
            f"{ctx.author.name}, I'm afraid you do not have permission to use this command.")


@bot.event
async def on_message(message):
    if message.author in usr_temp_time.keys():
        if message.content.lower().startswith(
                'yes'):  # If the message is yes and the author is in the temp list then add to user timing
            user_timing[message.author] = usr_temp_time.get(message.author)
            db_bot.update_timer(str(message.author), usr_temp_time.get(message.author))
            await message.channel.send('{}, Your time between notifications have been changed to {}'
                                       .format(message.author.name, usr_temp_time.get(message.author)))
            usr_temp_time.pop(message.author)
        elif 'timer' not in message.content.lower():  # Else remove it from the temp timing
            usr_temp_time.pop(message.author)
            await message.channel.send('Please try the command again')
    await bot.process_commands(message)

bot.add_command(help)
bot.add_command(stop)
bot.add_command(timer)
bot.add_command(channel)

bot.run(my_key)
