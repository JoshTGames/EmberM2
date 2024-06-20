import discord, json_manager, aiocron, datetime, utils, random

class NewClient(discord.Client):
    def __init__(self, *, intents: discord.Intents, commandDataPath: str):
        super().__init__(intents=intents)
        self.synced = False
        self.tree = None
        self.cronFunction = None
        self.userCrons = {}

        self.commandPath = commandDataPath
        self.commandData = json_manager.ReadFile(commandDataPath)
        self.presence = self.commandData['presence']

    async def on_ready(self):
        if(not self.synced):
            await self.tree.sync()
            self.synced = True

            key = self.commandData['crontabKey']

            if(aiocron.croniter.is_valid(key)):
                self.cronFunction = aiocron.crontab(key, func= self.manage_thread, start= True)

            await self.changePresence()
            aiocron.crontab('0 */1 * * *', func=self.changePresence, start=True)


            for k, v in self.commandData['userPings'].items():
                aiocron.crontab(v, func=self.ping_user, start=True, args=(k,))
            print(f'#_- {self.user} Online! -_#')

    async def changePresence(self):
        await self.change_presence(activity= discord.Game(self.presence[random.randint(0, len(self.presence) - 1)]));
    
    async def ping_user(self, userId):
        user = await self.fetch_user(userId)
        thread = await self.fetch_channel(self.commandData['previousThreadId'])
        if(thread == None or user == None): return # Stops any weirdness

        await user.send(f'✨Hello, this is your reminder to update the team on your progress!✨ \n{thread.jump_url}\n\nIf you no longer wish to recieve custom reminders, please type `/removereminder` in this server')


    async def manage_thread(self):
        # Archive old thread
        previousThread = await self.fetch_channel(self.commandData['previousThreadId'])
        if(previousThread):
            await previousThread.edit(archived=True)

        # Get Forum
        forum = await self.fetch_channel(self.commandData['scrumForumId'])
        if(forum is None): return

        
        date = datetime.date.today()

        name = f'{date.day}.{date.month}.{date.year} Update! - Please copy contents'
        ownerUser = await self.fetch_user(self.commandData['ownerId'])
        role = discord.utils.get(forum.guild.roles, id= self.commandData['notifyRoleId'])
        text = ''
        with open('thread_template.txt', 'r') as f:
            text = f.read()
        f.close()
        embed = utils.CreateEmbed(ownerUser, name, None, text, None, f'Any issues with this bot please contact {ownerUser.name}!', discord.Color.random())
        thread = await utils.CreateThread(forum, name, embed)

        self.commandData['previousThreadId'] = thread.id
        json_manager.WriteFile(self.commandPath, self.commandData)
        await thread.send(role.mention)