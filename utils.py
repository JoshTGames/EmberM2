import discord

def CreateEmbed(user, title, url, description, thumbnail, footer, colour, *args):
    embed = discord.Embed(
        title= title,
        url= url,
        description= description,
        color= colour
    )
    embed.set_author(name= user.display_name, icon_url= user.display_avatar, url= f"https://www.discordapp.com/users/{user.id}")
    embed.set_footer(text=footer)
    embed.set_thumbnail(url=thumbnail)
    for i in range(0, len(args)):
        embed.add_field(name= args[i][0], value= args[i][1], inline= args[i][2])
    return embed

async def CreateThread(parentChannel, name, content):
    return (await parentChannel.create_thread(name=name, embed= content)).thread