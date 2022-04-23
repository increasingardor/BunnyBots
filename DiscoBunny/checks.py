import discord
from discord.ext import commands

# Various Checks
# In discord.py a check is a function run before a command to determine if it should be run. 
# Checks for permissions, channels, etc.

# Just an error we raise if a user has the Creep role
class CreepError(commands.CommandError):
    pass

# An error we raise if the user doesn't have the role provided in a list
class MissingRoleInList(commands.CommandError):
    pass

# Check is a user has role Level 5 or higher, or has a specific override role.
def is_level_5(role=None):
    def predicate(ctx):
        # User's top role in the hierarchy
        top_role = ctx.author.top_role
        # List of all roles in the guild/server
        guild_roles = ctx.guild.roles
        # The Creep role
        creep = discord.utils.get(guild_roles, name="Creep")
        # List of all the user's roles
        member_roles = ctx.author.roles
        # Level 4 Role
        level4 = discord.utils.get(guild_roles, name="Level 4")
        # Raise error if has Creep rile
        if creep in member_roles:
            raise CreepError()
        elif role == None:
            return top_role > level4
        else:
            # The override role
            passed_role = discord.utils.get(guild_roles, name=role)
            return top_role > level4 or passed_role in member_roles
    return commands.check(predicate)

# Same as above, except Level 10
def is_level_10(role=None):
    def predicate(ctx):
        top_role = ctx.author.top_role
        guild_roles = ctx.guild.roles
        creep = discord.utils.get(guild_roles, name="Creep")
        member_roles = ctx.author.roles
        level9 = discord.utils.get(guild_roles, name="Level 9")
        if creep in member_roles:
            raise CreepError()
        elif role == None:
            return top_role > level9
        else:
            passed_role = discord.utils.get(guild_roles, name=role)
            return top_role > level9 or passed_role in member_roles
    return commands.check(predicate)

# A check for any level number or an override role; not yet implemented in any module
def level_check(level, role=None):
    def predicate(ctx):
        top_role = ctx.author.top_role
        guild_roles = ctx.guild.roles
        creep = discord.utils.get(guild_roles, name="Creep")
        member_roles = ctx.author.roles
        level_role = discord.utils.get(guild_roles, name=f"Level {level}")
        if creep in member_roles:
            raise CreepError()
        elif role == None:
            return top_role > level_role
        else:
            passed_role = discord.utils.get(guild_roles, name=role)
            return top_role > level_role or passed_role in member_roles
    return commands.check(predicate)

# Checks to see if user has any of the roles in a provided list
def has_role_in_list(roles):
    def predicate(ctx):
        allowed_roles = []
        # The roles parameter is a comma separated string so we split on ','
        for role in roles.split(","):
            # There may be spaces before or after, so we remove them
            allowed_roles.append(role.strip())
        # Create a list of all roles the user has that are in allowed roles; if none, raise error
        if not len([role for role in ctx.author.roles if role.name in allowed_roles]):
           raise MissingRoleInList()
        else:
            return True
    return commands.check(predicate)

