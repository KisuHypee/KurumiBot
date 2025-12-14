import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import random
import asyncio

#load token from .env file
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

#constants
kisu_id = 595224459783307264
WHITELIST_ROLES = ["Where Winds Meet", "Valorant", "Roblox", "Minecraft"] #self-assignable roles

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

#online message (terminal)
@bot.event
async def on_ready():
    print(f'Coming online, {bot.user.name}!')

#welcome message (to new members)
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        await channel.send(f'Welcome to the server, {member.mention}! Make yourself at home.')

#love you too message (from kisuhypee only)
@bot.event
async def on_message(message):
    # Ignore the bot itself
    if message.author == bot.user:
        return

    # Always let command messages be processed by commands framework regardless of author
    if isinstance(message.content, str) and message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return

    # For non-command messages, enforce the kisuhypee-only filter
    try:
        target_id = int(kisu_id)
    except Exception:
        target_id = 0

    if target_id:
        if message.author.id != target_id:
            return
    else:
        author_name = getattr(message.author, "name", "") or getattr(message.author, "display_name", "")
        if author_name.lower() != "kisuhypee":
            return

    # Handle the "love" behavior for the allowed user
    if "love" in message.content.lower():
        if "kurumi" in message.content.lower():
            await message.channel.send("❤️ Love you too")
        else:
            await message.channel.send("💔 Love who?")

#what's my name command
@bot.command()
async def whatsmyname(ctx):
    await ctx.send(f'You are... {ctx.author.mention}!')

#getrole command
@bot.command()
async def getrole(ctx, *, role_name: str = None):
    """Assign a role by name. Usage: `!getrole Human`"""
    if role_name is None:
        return await ctx.send("Usage: !getrole <role name>")

    if ctx.guild is None:
        return await ctx.send("This command must be used in a server/guild.")

    # Find role by exact-case-insensitive name
    role = discord.utils.find(lambda r: r.name.lower() == role_name.lower(), ctx.guild.roles)
    if role is None:
        return await ctx.send(f"Role '{role_name}' not found in this server.")

    # If a whitelist is defined, only allow roles in it
    if WHITELIST_ROLES and role.name not in WHITELIST_ROLES:
        return await ctx.send(f"The role '{role.name}' cannot be self-assigned.")

    # Check if user already has the role
    if role in ctx.author.roles:
        await ctx.send(f"{ctx.author.mention}, the role '{role.name}' has been removed from you.")
        return await ctx.author.remove_roles(role, reason="Self-removed via !getrole")
        
    # Try to assign the role
    try:
        await ctx.author.add_roles(role, reason="Self-assigned via !getrole")
    except discord.Forbidden:
        return await ctx.send("I don't have permission to assign that role. Ensure my role is above the target role and I have Manage Roles permission.")
    except Exception:
        logging.exception('Failed to assign role')
        return await ctx.send("Failed to assign role due to an error.")

    await ctx.send(f"{ctx.author.mention}, you've been given the role '{role.name}'.")

#random number generator command
@bot.command(name='rand')
async def rand(ctx, *args: str):
    """Random generator with settable margin.

    Usage:
    - `!rand <max>` -> integer between 1 and <max>
    - `!rand <base> <margin>` -> number between base-margin and base+margin
    Both integers and floats are accepted. If both base and margin are integers, an integer is returned.
    """
    if len(args) == 0:
        return await ctx.send("Usage: !rand <max>  OR  !rand <base> <margin>")

    # One argument: treat as max (1..max)
    if len(args) == 1:
        try:
            maxv = float(args[0])
        except ValueError:
            return await ctx.send("`max` must be a number.")

        if maxv < 1:
            return await ctx.send("`max` must be >= 1")

        # if max is integer-valued, use randint
        if maxv.is_integer():
            val = random.randint(1, int(maxv))
        else:
            val = random.uniform(1.0, maxv)

        return await ctx.send(f"🎲 {val}")

    # Two arguments: base and margin
    if len(args) >= 2:
        try:
            base = float(args[0])
            margin = float(args[1])
        except ValueError:
            return await ctx.send("Both `base` and `margin` must be numbers.")

        if margin < 0:
            return await ctx.send("`margin` must be non-negative.")

        low = base - margin
        high = base + margin
        if low > high:
            low, high = high, low

        # If both base and margin were integer-valued, return integer
        if base.is_integer() and margin.is_integer():
            val = random.randint(int(low), int(high))
        else:
            val = random.uniform(low, high)

        return await ctx.send(f"🎲 {val}")

    # Fallback
    await ctx.send("Usage: !rand <max>  OR  !rand <base> <margin>")

#funni command
@bot.command()
async def funni(ctx, member: discord.Member = None, times: int = 10):
    
    if member is None:
        member = ctx.author

    # Send pings with a short delay to avoid hitting rate limits
    for _ in range(times):
        await ctx.send(member.mention)
        await asyncio.sleep(0.2)

#run the bot
bot.run(token, log_handler=handler, log_level=logging.DEBUG)