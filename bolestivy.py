import discord
import random
import datetime
import asyncio
import threading
from time import sleep
from discord.ext import commands

TOKEN_FILE = open("token.txt", "r")
TOKEN = TOKEN_FILE.read()

CURRENT_GAMES = []
MOVIGN = False

# Define intents
intents = discord.Intents.all()

client = commands.Bot(command_prefix=".", intents=intents)

# register = client.create_group("register", "Register People")

# Define the voice channel ID where players gather
QUEUE_VOICE_ID = 1013018493119115284
TFS_CATEGORY_ID = 935506571633508360
SERVER_ID = 935506570601721856

# Define the time range (18:00 to 21:00)
START_HOUR = 18
END_HOUR = 22

@client.event
async def on_ready():
    print(f"Logged in as {client.user.name} ({client.user.id})")
    await client.tree.sync()

# Event triggered when a member's voice state changes
@client.event
async def on_voice_state_update(member, before, after):
    global CURRENT_GAMES, MOVING
    if after.channel and after.channel.id == QUEUE_VOICE_ID:
        # Check if there are 8 players in the voice channel
        if len(after.channel.members) == 8:
            # Check if it's within the specified time range
            current_hour = datetime.datetime.now().hour
            if START_HOUR <= current_hour < END_HOUR and not MOVING:
                # Create two new voice channels
            
                MOVING = True

                GAME_FILE = open("game.txt", "r")
                GAME_NUM = int(GAME_FILE.read())
                GAME_NUM += 1
                GAME_FILE.close()
                GAME_FILE = open("game.txt", "w")
                GAME_FILE.write(str(GAME_NUM))
                GAME_FILE.close()                

                # Shuffle the players randomly
                players = random.sample(after.channel.members, k=2)

                category = client.get_channel(TFS_CATEGORY_ID)
                room_1 = await category.create_voice_channel(f"game-{GAME_NUM} | 💔", user_limit=4)
                room_2 = await category.create_voice_channel(f"game-{GAME_NUM} | 💙", user_limit=4)
                TEAM1 = []
                TEAM2 = []
                # Move players to the new rooms
                for i, player in enumerate(players):
                    if i < 4:
                        await player.move_to(room_1)
                        TEAM1.append(player.name)
                        
                    else:
                        await player.move_to(room_2)
                        TEAM2.append(player.name)

                overwrites = {
                    member.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    member.guild.me: discord.PermissionOverwrite(read_messages=True)
                }
                for member in after.channel.members:
                    overwrites[member] = discord.PermissionOverwrite(read_messages=True)
                category = discord.utils.get(member.guild.categories, id=935506571633508360)
                await member.guild.create_text_channel(f"Game {GAME_NUM}", overwrites=overwrites, category=category)
                
                GAME_TEAMS = [TEAM1, TEAM2]
                CURRENT_GAMES.append(GAME_TEAMS)
                MOVING = False
                # print(CURRENT_GAMES)    

    if before.channel is not None:  # The member has left a voice channel
        print("c")
        text_channel_name = before.channel.name[:-4]  # Remove the last four characters
        print(before.channel.name)
        print(before.channel.name[:-4])
        print(len(before.channel.name))
        text_channel = discord.utils.get(member.guild.text_channels, name=text_channel_name)
        if before.channel.name.startswith("game"):
            print("d")
            await text_channel.set_permissions(member, read_messages=False)

    if after.channel is not None:  # The member connected to a voice channel.
        # Get the text channel with the same name as the voice channel (minus the last 4 characters).
        print("a")
        text_channel_name = after.channel.name[:-4]
        text_channel = discord.utils.get(after.channel.guild.text_channels, name=text_channel_name)
        
        if text_channel is not None:
            print("b")
            # Add the 'read_messages' permission to the member for this text channel.
            await text_channel.set_permissions(member, read_messages=True)

    # if before.channel is not None:
    #     # The member was in a voice channel before this update
    #     text_channel_name = before.channel.name[:-4]
    #     text_channel = discord.utils.get(member.guild.text_channels, name=text_channel_name)
    #     if text_channel is not None:
    #         await text_channel.set_permissions(member, read_messages=False)

    # if after.channel is not None:
    #     # The member is in a voice channel after this update
    #     text_channel_name = after.channel.name[:-4]
    #     text_channel = discord.utils.get(member.guild.text_channels, name=text_channel_name)
    #     if text_channel is not None:
    #         await text_channel.set_permissions(member, read_messages=True)       
                
    if before.channel and before.channel.id != QUEUE_VOICE_ID:
        # Check if the member left a game room
        if before.channel.name.startswith("game"):
            # Get the category of the room
            category = before.channel.category

            # Check if all members have left the room
            if len(before.channel.members) == 0:
                # Delete the room
                await before.channel.delete()
                # print(f"Room {before.channel.name} has been deleted.")

# Load existing usernames from a file (usernames.txt)
def load_usernames():
    try:
        with open("usernames.txt", "r") as file:
            return set(line.strip() for line in file)
    except FileNotFoundError:
        return set()

# Save new usernames to the file
def save_usernames(usernames):
    with open("usernames.txt", "a") as file:
        for username in usernames:
            file.write(username + "\n")

@client.tree.command(name="register",description="Register username")
async def _register(interaction:discord.Interaction, username: str):
    # Load existing usernames
    existing_usernames = load_usernames()
    await interaction.user.edit(nick = username)
    
    print(existing_usernames)

    server = await client.fetch_guild(SERVER_ID)
    member = await server.fetch_member(interaction.user.id)
    nick = member.nick

    je = False
    # Check if the username is already registered

    for name in existing_usernames:
        if name == member.nick:
            je = True
            break

    if je:
        await interaction.response.send_message("You are already registered.")
    else:
        # Register the user
        existing_usernames.add(str(member.nick).lower())
        save_usernames(existing_usernames)
        await interaction.response.send_message("You have been registered successfully!")
"""
    if str(member.nick).lower() in existing_usernames:
        await interaction.response.send_message("You are already registered.")
    else:
        # Register the user
        existing_usernames.add(str(member.nick).lower())
        save_usernames(existing_usernames)
        await interaction.response.send_message("You have been registered successfully!")"""


# Run the bot
client.run(TOKEN)