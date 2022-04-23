import os

# Gets all files in the cogs directory; used in loading the bot to auto-load all cogs
def get_cogs():
    cogs = []
    for file in os.listdir("cogs/"):
        if file.endswith(".py"):
            cogs.append(f"cogs.{file.split('.')[0]}")
    return cogs
