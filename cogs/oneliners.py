#Import Modules
import discord
from discord.ext import commands
import random

#Cog Setup
class Oneliners(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Oneliners cog loaded.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return
        msg = message.content.lower()

        ##Hello
        if msg.startswith("hello, musa") or msg.startswith("hello musa") or msg.startswith("hi, musa") or msg.startswith("hi musa") or msg.startswith("hey, musa") or msg.startswith("hey musa") or msg.startswith("greetings, musa") or msg.startswith("greetings musa") or msg.startswith("good day, musa") or msg.startswith("good day musa") or msg.startswith("good morning, musa") or msg.startswith("good morning musa") or msg.startswith("good afternoon, musa") or msg.startswith("good afternoon musa") or msg.startswith("good evening, musa") or msg.startswith("good evening musa") or msg.startswith("howdy, musa") or msg.startswith("howdy musa") or msg.startswith("salutations, musa") or msg.startswith("salutations musa") or msg.startswith("morning, musa") or msg.startswith("morning musa") or msg.startswith("afternoon, musa") or msg.startswith("afternoon musa") or msg.startswith("evening, musa") or msg.startswith("evening musa") or msg.startswith("what's up musa") or msg.startswith("what's up, musa") or msg.startswith("whats up musa") or msg.startswith("whats up, musa") or msg.startswith("sup musa") or msg.startswith("sup, musa") or msg.startswith("yo musa") or msg.startswith("yo, musa") or msg.startswith("well met musa") or msg.startswith("well met, musa") or msg.startswith("well-met musa") or msg.startswith("well-met, musa") or msg.startswith("bonjour, musa") or msg.startswith("bonjour musa"):
            await message.channel.send('Hello!')

        ##Love you
        if ("musa" in msg and "love you" in msg) or ("i love musa" in msg):
            await message.channel.send("I appreciate it, but I'd prefer to remain friends.")

        ##Bye
        if msg.startswith("bye, musa") or msg.startswith("bye musa") or msg.startswith("farewell, musa") or msg.startswith("farewell musa") or msg.startswith("cya, musa") or msg.startswith("cya musa") or msg.startswith("see you, musa") or msg.startswith("see you musa") or msg.startswith("see ya, musa") or msg.startswith("see ya musa") or msg.startswith("sayounara, musa") or msg.startswith("sayounara musa") or msg.startswith("sayonara, musa") or msg.startswith("sayonara musa") or msg.startswith("later, musa") or msg.startswith("later musa") or msg.startswith("ciao, musa") or msg.startswith("ciao musa"):
            await message.channel.send("Bye!")

        ##Apologize for being broken
        if ("musa" in msg and "broken" in msg and "you" in msg):
            await message.channel.send("Who cares what you think? You're not my mother.")

        ##Thanks
        if "musa" in msg and ("thank" in msg or "good work" in msg or "good job" in msg):
            await message.channel.send("You're welcome.")

        ##Muna
        if "muna" in msg and "musa" in msg:
            await message.channel.send("https://cdn.discordapp.com/attachments/409419122774900738/704097609245261936/unknown.png")

        ##Computer, boot up celery man please
        if ("see" in msg or "show" in msg or "boot" in msg or
        "pull" in msg or "display" in msg or "view" in msg or
        "manifest" in msg or "summon" in msg or "please" in msg or
        "load" in msg or "musa" in msg):
            if "celery man" in msg:
                await message.channel.send('Yes, ' + message.author.name + '.\nhttps://www.youtube.com/watch?v=MHWBEK8w_YY')
            if "spyro cbt" in msg:
                await message.channel.send('Yes, ' + message.author.name + '.\nhttps://t.co/Qd89FuLJJa')
            if "two trucks" in msg:
                await message.channel.send('Yes, ' + message.author.name + '.\nhttps://www.youtube.com/watch?v=WchseC9aKTU')
            if "skooks" in msg:
                await message.channel.send('Yes, ' + message.author.name + '.\nhttps://www.youtube.com/watch?v=p-xQQfImnQw')
            if "fesh pince" in msg and not "2" in msg:
                await message.channel.send('Yes, ' + message.author.name + '.\nhttps://www.youtube.com/watch?v=HeIkk6Yo0s8')
            if "fesh pince 2" in msg:
                await message.channel.send('Yes, ' + message.author.name + '.\nhttps://www.youtube.com/watch?v=Drqj67ImtxI')
            if "chinese" in msg and "parappa" in msg:
                await message.channel.send('Yes, ' + message.author.name + '.\nhttps://www.youtube.com/watch?v=mGlCGMm8Qag')

        ##Ting Noise
        if "uhh b" in msg or "press b" in msg or "context sensitive" in msg or "context sensetive" in msg or msg.startswith("ting noise") or msg.startswith("ding noise") or " ting noise" in msg or " ding noise" in msg:
            await message.channel.send("https://www.youtube.com/watch?v=lbuW6zIuUo4")

        ##WitchHorse
        if ":WitchHorse:" in message.content:
            await message.add_reaction("<:WitchHorse:515665966420721664>")

        ##Katia Butt Dance
        if "katia" in msg:
            await message.channel.send("<a:musacanusethis:716108843406458911>")

        ##Musa Isn't Real
        if ("musa" in msg) and ("nt real" in msg or "n't real" in msg or "not real" in msg or "not a real" in msg) and not ("really" in msg):
            await message.channel.send("I'm very real.")

        ##Deer!
        if ("DEER" in message.content) or ("deer!" in msg):
            await message.channel.send("https://cdn.discordapp.com/attachments/773152101223497728/880253965894287371/20210825_120256.jpg")

def setup(client):
    client.add_cog(Oneliners(client))
