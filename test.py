from database_bot import databse_bot
import ast
import json

directory = r"c:\users\Steven\PycharmProjects\HydrationBot\DiscordHydrationBot\BOT.db"
bot = databse_bot(directory)
bot.restart_database()
bot.read_database()
