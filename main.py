import aiocron
from typing import Optional
import discord
from discord import app_commands
import os, sys
import json_manager, client

commandsDir = os.getcwd() + '/command_data.json'

_client = client.NewClient(intents=discord.Intents.default(), commandDataPath=commandsDir)
_client.tree = app_commands.CommandTree(_client)


#region USER COMMANDS
@_client.tree.command(name='subscribe', description='Subscribes you to recieve daily notifications on scrum updates!')
async def self(interaction: discord.Interaction):
    role = discord.utils.get(interaction.guild.roles, id= _client.commandData['notifyRoleId'])
    if(role == None):
        await interaction.response.send_message(f'Role not set. | Ask an admin to set this up.', ephemeral= True)
        return
    elif(role in interaction.user.roles):
        await interaction.response.send_message(f'You are already subscribed to recieve notifications!', ephemeral= True)
        return
    await interaction.user.add_roles(role)
    await interaction.response.send_message(f'You now have the {role.name} role! | (You will now recieve scrum notifications)', ephemeral= True)

@_client.tree.command(name='unsubscribe', description='Unsubscribes you from recieving daily notifications on scrum updates!')
async def self(interaction: discord.Interaction):
    role = discord.utils.get(interaction.guild.roles, id= _client.commandData['notifyRoleId'])
    if(role == None):
        await interaction.response.send_message(f'Role not set. | Ask an admin to set this up.', ephemeral= True)
        return
    elif(not (role in interaction.user.roles)):
        await interaction.response.send_message(f'You are not subscribed to recieve notifications!', ephemeral= True)
        return
    await interaction.user.remove_roles(role)
    await interaction.response.send_message(f'You no longer have the {role.name} role! | (You will no longer recieve scrum notifications)', ephemeral= True)
#endregion
    
#region ADMIN COMMANDS
@_client.tree.command(name='setrole', description='Sets the role this bot will ping | ADMIN')
async def self(interaction: discord.Interaction, role: discord.Role):
    _client.commandData['notifyRoleId'] = role.id
    json_manager.WriteFile(commandsDir, _client.commandData)
    await interaction.response.send_message(f'Successfully set notify role', ephemeral= True)   

@_client.tree.command(name='setscrumforum', description='Sets the forum this bot will write in | ADMIN')
async def self(interaction: discord.Interaction, forum: discord.ForumChannel):
    _client.commandData['scrumForumId'] = forum.id
    json_manager.WriteFile(commandsDir, _client.commandData)
    await interaction.response.send_message(f'Successfully set scrum forum', ephemeral= True)

@_client.tree.command(name='setpingtime', description='The time of day this bot will ping the forum | ADMIN',)
@app_commands.describe(cronkey='https://crontab.guru/ <- Visit this for keys')
async def self(interaction: discord.Interaction, cronkey: str):
    if(not aiocron.croniter.is_valid(cronkey)):
        await interaction.response.send_message(f'Failed setting ping time... Please check cron key!', ephemeral=True)
        return 

    _client.commandData['crontabKey'] = cronkey
    json_manager.WriteFile(commandsDir, _client.commandData)
    
    if(_client.cronFunction):
        _client.cronFunction.stop()
    _client.cronFunction = aiocron.crontab(_client.commandData['crontabKey'], func= _client.manage_thread, start= True)
    await interaction.response.send_message(f'Successfully set the ping time', ephemeral= True)

@_client.tree.command(name='shutdown', description='Can only be called by the owner of this bot | OWNER',)
async def self(interaction: discord.Interaction):
    if(interaction.user.id != _client.commandData['ownerId']): return
    print(f'{interaction.user} has issued a shutdown!')
    await interaction.response.send_message(f'Shutting down...', ephemeral= True)
    sys.exit(0)


# -- Main -- #
with open('token.txt', 'r') as f:
    _client.run(f.read())
    f.close()