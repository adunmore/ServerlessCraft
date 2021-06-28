import os

from app import discord

if __name__ == "__main__":
    discord.update_slash_commands(guild_id=os.environ["GUILD_ID"])
