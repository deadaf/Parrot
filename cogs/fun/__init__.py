
import discord, random, io, base64, datetime, aiohttp, urllib, asyncio, time, json
from discord.ext import commands
from discord.ext.commands import command, guild_only, bot_has_permissions, cooldown, BucketType
from random import choice
from discord import Embed 


from utilities.database import parrot_db, telephone_update
collection = parrot_db['telephone']

from aiohttp import request

import akinator
from akinator.async_aki import Akinator

from utilities.paginator import Paginator
from core import Parrot, Context, Cog


with open("extra/truth.txt") as f:
  _truth = f.read()

with open("extra/dare.txt") as g:
  _dare = g.read()

with open("extra/lang.json") as lang:
    lg = json.load(lang)

from typing import List, Optional


response = ["All signs point to yes...","Yes!", "My sources say nope.", "You may rely on it.", "Concentrate and ask again...", "Outlook not so good...", "It is decidedly so!", "Better not tell you.", "Very doubtful.", "Yes - Definitely!", "It is certain!", "Most likely.", "Ask again later.", "No!", "Outlook good.", "Don't count on it.", "Why not", "Probably", "Can't say", "Well well..."]

class fun(Cog):
    """Parrot gives you huge amount of fun commands, so that you won't get bored"""

    def __init__(self, bot: Parrot):
        self.bot = bot
  
    @command(name='8ball')
    @Context.with_type
    async def _8ball(self, ctx: Context, *, question:commands.clean_content):
        """
        8ball Magic, nothing to say much
        """
        await ctx.reply(f'Question: **{question}**\nAnswer: **{random.choice(response)}**')

    @commands.command()
    @Context.with_type
    async def choose(self, ctx: Context, *, options:commands.clean_content):
        """
        Confuse something with your decision? Let Parrot choose from your choice.
        NOTE: The `Options` should be seperated by commas `,`.
        """
        options = options.split(',')
        await ctx.reply(f'{ctx.author.mention} I choose {choice(options)}')
  

    @commands.command(aliases=['colours', 'colour'])
    @commands.bot_has_permissions(embed_links=True)
    @Context.with_type
    async def color(self, ctx: Context, colour):
        """
        To get colour information using the hexadecimal codes.
        """
        
        link = f"https://www.thecolorapi.com/id?format=json&hex={colour}"
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as response:
                if response.status == 200:
                    res = await response.json()
                else:
                    return

        green = round(res['rgb']['fraction']['g'], 2)
        red = round(res['rgb']['fraction']['r'], 2)
        blue = round(res['rgb']['fraction']['b'], 2)
        _green = res['rgb']['g']
        _red = res['rgb']['r']
        _blue = res['rgb']['b']
        
        #HSL VALUE
        hue = round(res['hsl']['fraction']['h'], 2)
        saturation = round(res['hsl']['fraction']['s'], 2)
        lightness = round(res['hsl']['fraction']['l'], 2)
        _hue = res['hsl']['h']
        _saturation = res['hsl']['s']
        _lightness = res['hsl']['l']
        
        #HSV VALUE
        hue_ = round(res['hsv']['fraction']['h'], 2)
        saturation_ = round(res['hsv']['fraction']['s'], 2)
        value_ = round(res['hsv']['fraction']['v'], 2)
        _hue_ = res['hsv']['h']
        _saturation_ = res['hsv']['s']
        _value_ = res['hsv']['v']
        
        #GENERAL
        name = res['name']['value']
        close_name_hex = res['name']['closest_named_hex']
        exact_name = res['name']['exact_match_name']
        distance = res['name']['distance']

        embed = discord.Embed(title="Parrot colour prompt", timestamp=datetime.datetime.utcnow(), colour = discord.Color.from_rgb(_red, _green, _blue), description=f"Colour name: `{name}` | Close Hex code: `{close_name_hex}` | Having exact name? `{exact_name}` | Distance: `{distance}`")
        embed.set_thumbnail(url=f"https://some-random-api.ml/canvas/colorviewer?hex={colour}")
        embed.set_footer(text=f"{ctx.author.name}")
        fields = [
            ("RGB value (fraction)", f"Red: `{_red}` (`{red}`)\nGreen: `{_green}` (`{green}`)\nBlue: `{_blue}` (`{blue}`)", True),
            ("HSL value (fraction)", f"Hue: `{_hue}` (`{hue}`)\nSaturation: `{_saturation}` (`{saturation}`)\nLightness: `{_lightness}` (`{lightness}`)", True),
            ("HSV value (fraction)", f"Hue: `{_hue_}` (`{hue_}`)\nSaturation: `{_saturation_}` (`{saturation_}`)\nValue: `{_value_}` (`{value_}`)", True)		
          ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        await ctx.send(embed=embed)
      
  
    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    @Context.with_type
    async def decode(self, ctx: Context, *, string:str):
        """
        Decode the code to text from Base64 encryption
        """
        base64_string = string
        base64_bytes = base64_string.encode("ascii") 
        
        sample_string_bytes = base64.b64decode(base64_bytes) 
        sample_string = sample_string_bytes.decode("ascii") 
        
        embed = discord.Embed(title="Decoding...", colour=discord.Colour.red(), timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Encoded text:", value=f'```\n{base64_string}\n```', inline=False)
        embed.add_field(name="Decoded text:", value=f'```\n{sample_string}\n```', inline=False)
        embed.set_thumbnail(url='https://upload.wikimedia.org/wikipedia/commons/4/45/Parrot_Logo.png')
        embed.set_footer(text=f"{ctx.author.name}", icon_url=f'{ctx.author.avatar.url}')
        await ctx.send(embed=embed)



    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    @Context.with_type
    async def encode(self, ctx: Context, *, string:str):
        """
        Encode the text to Base64 Encryption and in Binary
        """
        sample_string = string
        sample_string_bytes = sample_string.encode("ascii") 
        res = ''.join(format(ord(i), 'b') for i in string)
        base64_bytes = base64.b64encode(sample_string_bytes) 
        base64_string = base64_bytes.decode("ascii") 
        
        embed = discord.Embed(title="Encoding...", colour=discord.Colour.red(), timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Normal [string] text:", value=f'```\n{sample_string}\n```', inline=False)
        embed.add_field(name="Encoded [base64]:", value=f'```\n{base64_string}\n```', inline=False)
        embed.add_field(name="Encoded [binary]:", value=f'```\n{str(res)}\n```', inline=False)
        embed.set_thumbnail(url='https://upload.wikimedia.org/wikipedia/commons/4/45/Parrot_Logo.png')
        embed.set_footer(text=f"{ctx.author.name}", icon_url=f'{ctx.author.avatar.url}')
        await ctx.send(embed=embed)

  
      
    @commands.command(name="fact")
    @commands.bot_has_permissions(embed_links=True)
    @Context.with_type
    async def animal_fact(self, ctx: Context, *, animal: str):
        """
        Return a random Fact. It's useless command, I know

        NOTE: Available animals - Dog, Cat, Panda, Fox, Bird, Koala
        """
        if (animal := animal.lower()) in ("dog", "cat", "panda", "fox", "bird", "koala"):
            fact_url = f"https://some-random-api.ml/facts/{animal}"
            image_url = f"https://some-random-api.ml/img/{'birb' if animal == 'bird' else animal}"

            async with request("GET", image_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()
                    image_link = data["link"]

                else:
                    image_link = None

            async with request("GET", fact_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()

                    embed = Embed(title=f"{animal.title()} fact", description=data["fact"], colour=ctx.author.colour)
                    if image_link is not None:
                        embed.set_image(url=image_link)
                        return await ctx.reply(embed=embed)

                    else:
                        return await ctx.reply(f"{ctx.author.mention} API returned a {response.status} status.")

                else:
                    return await ctx.reply(f"{ctx.author.mention} no facts are available for that animal. Available animals: `dog`, `cat`, `panda`, `fox`, `bird`, `koala`")


    @commands.command()
    @commands.bot_has_permissions(attach_files=True, embed_links=True)
    @Context.with_type
    async def gay(self, ctx: Context, *, member:discord.Member=None):
        """
        Image Generator. Gay Pride.
        """
        if member is None: member = ctx.author
        async with aiohttp.ClientSession() as wastedSession:
            async with wastedSession.get('https://some-random-api.ml/canvas/gay?avatar={}'.format(member.avatar.url)) as wastedImage: 
                imageData = io.BytesIO(await wastedImage.read()) # read the image/bytes
                
                await wastedSession.close() # closing the session and;
                
                await ctx.reply(file=discord.File(imageData, 'gay.png')) # replying the file


    @commands.command()
    @commands.bot_has_permissions(attach_files=True, embed_links=True)
    @Context.with_type
    async def glass(self, ctx: Context, *, member:discord.Member=None):
        """
        Provide a glass filter on your profile picture, try it!
        """
        if member is None: member = ctx.author
        async with aiohttp.ClientSession() as wastedSession:
            async with wastedSession.get(f'https://some-random-api.ml/canvas/glass?avatar={member.avatar.url}') as wastedImage: # get users avatar as png with 1024 size
                imageData = io.BytesIO(await wastedImage.read()) # read the image/bytes
                
                await wastedSession.close() # closing the session and;
                
                await ctx.reply(file=discord.File(imageData, 'glass.png')) # replying the file


    @commands.command()
    @commands.bot_has_permissions(attach_files=True, embed_links=True)
    @Context.with_type
    async def horny(self, ctx: Context, *, member:discord.Member=None):
        """
        Image generator, Horny card generator.
        """
        if member is None: member = ctx.author
        async with aiohttp.ClientSession() as wastedSession:
            async with wastedSession.get(f'https://some-random-api.ml/canvas/horny?avatar={member.avatar.url}.') as wastedImage: 
                imageData = io.BytesIO(await wastedImage.read()) # read the image/bytes
                
                await wastedSession.close() # closing the session and;
                
                await ctx.reply(file=discord.File(imageData, 'horny.png')) # replying the file


    @commands.command(aliases=['insult'])
    @Context.with_type
    async def roast(self, ctx: Context, *, member: discord.Member = None):
        """
        Insult your enemy, Ugh!
        """
        if member == None: member = ctx.author
        async with aiohttp.ClientSession() as session:
            async with session.get("https://insult.mattbas.org/api/insult") as response:
                insult = await response.text()
                await ctx.reply(f"**{member.name}** {insult}")



    @commands.command(aliases=['its-so-stupid'])
    @Context.with_type
    @commands.bot_has_permissions(attach_files=True, embed_links=True)
    async def itssostupid(self, ctx, *, comment:str):
      """
      :\ I don't know what is this, I think a meme generator.
      """
      member = ctx.author
      if len(comment) > 20: comment = comment[:19:]
      async with aiohttp.ClientSession() as wastedSession:
          async with wastedSession.get(f'https://some-random-api.ml/canvas/its-so-stupid?avatar={member.avatar.url}&dog={comment}') as wastedImage: # get users avatar as png with 1024 size
              imageData = io.BytesIO(await wastedImage.read()) # read the image/bytes
              
              await wastedSession.close() # closing the session and;
              
              await ctx.reply(file=discord.File(imageData, 'itssostupid.png')) # replying the file

      

    @commands.command()
    @commands.bot_has_permissions(attach_files=True, embed_links=True)
    @Context.with_type
    async def jail(self, ctx: Context, *, member:discord.Member=None):
        """
        Image generator. Makes you behind the bars. Haha
        """
        if member is None: member = ctx.author
        async with aiohttp.ClientSession() as wastedSession:
            async with wastedSession.get(f'https://some-random-api.ml/canvas/jail?avatar={member.avatar.url}') as wastedImage: # get users avatar as png with 1024 size
                imageData = io.BytesIO(await wastedImage.read()) # read the image/bytes
                
                await wastedSession.close() # closing the session and;
                
                await ctx.reply(file=discord.File(imageData, 'jail.png')) # replying the file
  

    @commands.command()
    @commands.bot_has_permissions(attach_files=True, embed_links=True)
    @Context.with_type
    async def lolice(self, ctx: Context, *, member:discord.Member=None):
        """
        This command is not made by me. :\
        """
        if member is None: member = ctx.author
        async with aiohttp.ClientSession() as wastedSession:
            async with wastedSession.get(f'https://some-random-api.ml/canvas/lolice?avatar={member.avatar.url}') as wastedImage: # get users avatar as png with 1024 size
                imageData = io.BytesIO(await wastedImage.read()) # read the image/bytes
                
                await wastedSession.close() # closing the session and;
                
                await ctx.reply(file=discord.File(imageData, 'lolice.png')) # replying the file
  
      
    @commands.command(name='meme')
    @commands.bot_has_permissions(embed_links=True)
    @Context.with_type
    async def meme(self, ctx: Context):
        """
        Random meme generator.
        """
        link = "https://memes.blademaker.tv/api?lang=en"
        async with aiohttp.ClientSession() as session:
          async with session.get(link) as response:
              if response.status == 200:
                  res = await response.json()
              else:
                  return
        title = res['title']
        ups = res["ups"]
        downs = res["downs"]
        sub = res["subreddit"]

        embed = discord.Embed(title=f'{title}', description=f"{sub}", timestamp=datetime.datetime.utcnow())
        embed.set_image(url = res["image"])
        embed.set_footer(text=f"UP(s): {ups} | DOWN(s): {downs}") 

        await ctx.reply(embed=embed)
      

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    @Context.with_type
    async def fakepeople(self, ctx: Context):
        """
        Fake Identity generator.
        """
        link = "https://randomuser.me/api/"
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as response:
                if response.status == 200:
                    res = await response.json()
                else:
                    return
        res = res['results'][0]
        name = f"{res['name']['title']} {res['name']['first']} {res['name']['last']}"
        address = f"{res['location']['street']['number']}, {res['location']['street']['name']}, {res['location']['city']}, {res['location']['state']}, {res['location']['country']}, {res['location']['postcode']}"
        cords = f"{res['location']['coordinates']['latitude']}, {res['location']['coordinates']['longitude']}"
        tz = f"{res['location']['timezone']['offset']}, {res['location']['timezone']['description']}"
        email = res['email']
        usrname = res['login']['username']
        pswd = res['login']['password']
        age = res['dob']['age']
        phone = f"{res['phone']}, {res['cell']}"
        pic = res['picture']['large']

        em = discord.Embed(title=f"{name}", description=f"```\n{address} {cords}```", timestamp=datetime.datetime.utcnow())
        em.add_field(name="Timezone", value=f"{tz}", inline=False)
        em.add_field(name="Email & Password", value=f"**Username:** {usrname}\n**Email:** {email}\n**Password:** {pswd}", inline=False)
        em.add_field(name="Age", value=f"{age}", inline=False)
        em.set_thumbnail(url=pic)
        em.add_field(name="Phone", value=f"{phone}", inline=False)
        em.set_footer(text=f"{ctx.author.name}")

        await ctx.reply(embed=em)


    @commands.command()
    @commands.bot_has_permissions(attach_files=True, embed_links=True)
    @Context.with_type
    async def simpcard(self, ctx: Context, *, member:discord.Member=None):
        """
        Good for those, who are hell simp! LOL
        """
        if member is None: member = ctx.author
        async with aiohttp.ClientSession() as wastedSession:
            async with wastedSession.get(f'https://some-random-api.ml/canvas/simpcard?avatar={member.avatar.url}') as wastedImage: # get users avatar as png with 1024 size
                imageData = io.BytesIO(await wastedImage.read()) # read the image/bytes
                
                await wastedSession.close() # closing the session and;
                
                await ctx.reply(file=discord.File(imageData, 'simpcard.png')) # replying the file
      
  
    @command(name="slap", aliases=["hit"])
    @commands.bot_has_permissions(manage_messages=True)
    @Context.with_type
    async def slap_member(self, ctx: Context, member: discord.Member, *, reason: commands.clean_content = "for no reason"):
        """
        Slap virtually with is shit command.
        """
        await ctx.message.delete()
        await ctx.reply(f"{ctx.author.display_name} slapped {member.mention} {reason}!")
  
    
    @commands.command(aliases=['trans'])
    @commands.bot_has_permissions(embed_links=True)
    @Context.with_type
    async def translate(self, ctx: Context, to: str, *, message: commands.clean_content=None):
        """
        Translates a message to English (default) using Google translate
        """
        if message is None:
            ref = ctx.message.reference
            if ref and isinstance(ref.resolved, discord.Message):
                message = ref.resolved.content
            else:
                return await ctx.reply(f"{ctx.author.mention} you must provide the message reference or message for translation")
        
        link = "https://translate-api.ml/translate?text={}&lang={}".format(message.lower(), to.lower() if to else 'en')

        async with aiohttp.ClientSession() as session:
            async with session.get(link) as response:
                if response.status == 200:
                    data = await response.json()
                else:
                    return await ctx.reply(f"{ctx.author.mention} Something not right!")
                
        success = data['status']
        if success == 200:
            text = data['given']['text']
            lang = data['given']['lang']
            translated_text = data['translated']['text']
            translated_lang = data['translated']['lang']
            translated_pronunciation = data['translated']['pronunciation']
        else: 
            return await ctx.reply(f"{ctx.author.mention} Can not translate **{message[1000::]}** to **{lang}**")
        
        embed = discord.Embed(
            title="Translated", 
            description=f"```\n{translated_text}\n```",
            color=ctx.author.color, 
            timestamp=datetime.datetime.utcnow())
        embed.set_footer(text=f"{ctx.author.name}")
        embed.add_field(name="Info", value=f"Tranlated from **{lg[lang]['name']}** to **{lg[translated_lang]['name']}**", inline=False)
        embed.add_field(name="Pronunciation", value=f"```\n{translated_pronunciation}\n```", inline=False)
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/1/14/Google_Translate_logo_%28old%29.png")
        await ctx.send(embed=embed)

    @commands.command(aliases=['triggered'])
    @commands.bot_has_permissions(attach_files=True, embed_links=True)
    @Context.with_type
    async def trigger(self, ctx: Context, *, member:discord.Member=None):
        """
        User Triggered!
        """
        if member is None: member = ctx.author
        async with aiohttp.ClientSession() as wastedSession:
            async with wastedSession.get(f'https://some-random-api.ml/canvas/triggered?avatar={member.avatar.url}') as wastedImage: # get users avatar as png with 1024 size
                imageData = io.BytesIO(await wastedImage.read()) # read the image/bytes
                
                await wastedSession.close() # closing the session and;
                
                await ctx.reply(file=discord.File(imageData, 'triggered.gif')) # replying the file

    @commands.command(aliases=['def', 'urban'])
    @commands.bot_has_permissions(embed_links=True)
    @Context.with_type
    async def urbandictionary(self, ctx: Context, *, text: commands.clean_content):
      """
      LOL. This command is insane.
      """
      t = text
      text = urllib.parse.quote(text)
      link = 'http://api.urbandictionary.com/v0/define?term=' + text 

      async with aiohttp.ClientSession() as session:
          async with session.get(link) as response:
              if response.status == 200:
                  res = await response.json()
              else:
                  return
      if not res['list']: return await ctx.reply(f"{ctx.author.mention} :\ **{t}** means nothings. Try something else")
      em_list = []
      for i in range(0, len(res['list'])):
          _def = res['list'][i]['definition']
          _link = res['list'][i]['permalink']
          thumbs_up = res['list'][i]['thumbs_up']
          thumbs_down = res['list'][i]['thumbs_down']
          author = res['list'][i]['author']
          example = res['list'][i]['example']
          word = res['list'][i]['word'].capitalize()	
          embed = discord.Embed(title=f"{word}", description=f"{_def}", url=f"{_link}", timestamp=datetime.datetime.utcnow())
          embed.add_field(name="Example", value=f"{example}")
          embed.set_author(name=f"Author: {author}")
          embed.set_footer(text=f"Page {i+1}/{len(res['list'])} | UP(s) {thumbs_up}, DOWNS(s) {thumbs_down}")
          em_list.append(embed)

      paginator = Paginator(pages=em_list, timeout=60.0)
    
      await paginator.start(ctx)


    @commands.command()
    @commands.bot_has_permissions(attach_files=True, embed_links=True)
    @Context.with_type
    async def wasted(self, ctx: Context, *, member:discord.Member=None):
        """
        Overlay 'WASTED' on your profile picture, just like GTA:SA
        """
        if member is None: member = ctx.author
        async with aiohttp.ClientSession() as wastedSession:
            async with wastedSession.get(f'https://some-random-api.ml/canvas/wasted?avatar={member.avatar.url}') as wastedImage: # get users avatar as png with 1024 size
                imageData = io.BytesIO(await wastedImage.read()) # read the image/bytes
                
                await wastedSession.close() # closing the session and;
                
                await ctx.reply(file=discord.File(imageData, 'wasted.png')) # replying the file
  

    @commands.command(aliases=['youtube-comment', 'youtube_comment'])
    @commands.bot_has_permissions(attach_files=True, embed_links=True)
    @Context.with_type
    async def ytcomment(self, ctx: Context, *, comment:str):
        """
        Makes a comment in YT. Best ways to fool your fool friends. :')
        """
        member = ctx.author
        if len(comment) > 1000: comment = comment[:999:]
        if len(member.name) > 20: name = member.name[:20:]
        else: name = member.name
        async with aiohttp.ClientSession() as wastedSession:
            async with wastedSession.get(f'https://some-random-api.ml/canvas/youtube-comment?avatar={member.avatar.url}&username={name}&comment={comment}') as wastedImage: # get users avatar as png with 1024 size
                imageData = io.BytesIO(await wastedImage.read()) # read the image/bytes
                
                await wastedSession.close() # closing the session and;
                
                await ctx.reply(file=discord.File(imageData, 'ytcomment.png')) # replying the file
  
  
    @commands.command() 
    @commands.bot_has_permissions(embed_links=True)
    @Context.with_type
    async def dare(self, ctx: Context, *, member:discord.Member=None):
        """
        I dared you to use this command.
        """
        dare = _dare.split("\n")
        if member is None:
            em = discord.Embed(title="Dare", description=f"{random.choice(dare)}", timestamp=datetime.datetime.utcnow())
        else:
            em = discord.Embed(title=f"{member.name} Dared", description=f"{random.choice(dare)}", timestamp=datetime.datetime.utcnow())
        
        em.set_footer(text=f'{ctx.author.name}')
        await ctx.send(embed=em)


    @commands.command() 
    @commands.bot_has_permissions(embed_links=True)
    @Context.with_type
    async def truth(self, ctx: Context, *, member:discord.Member=None):
        """
        Truth: Who is your crush?
        """
        t = _truth.split("\n")
        if member is None:
            em = discord.Embed(title="Truth", description=f"{random.choice(t)}", timestamp=datetime.datetime.utcnow())
            em.set_footer(text=f'{ctx.author.name}')
        else:
            em = discord.Embed(title=f"{member.name} reply!", description=f"{random.choice(t)}", timestamp=datetime.datetime.utcnow())
            em.set_footer(text=f'{ctx.author.name}')
        await ctx.send(embed=em)

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    @Context.with_type
    async def aki(self, ctx):
        """Answer the questions and let the bot guess your character!"""
        aki = Akinator()
        q = await aki.start_game()
        question_num = 1
        while aki.progression <= 80:
            question = q + "\n\t"
            embed = discord.Embed(color=0xFF0000)
            embed.add_field(
                name=f"Q-{question_num}\n{question}",
                value=
                "Reply with `yes/y` | `no/n` | `i/idk/i don't know` | `p/probably` | `proably not/pn`",
            )
            await ctx.send(embed=embed)

            def check(m):
                replies = [
                    "yes", "y", "no", "n", "i", "idk", "i don't know",
                    "probably", "p", "probably not", "pn"
                ]
                return (m.content in replies and m.channel == ctx.channel
                        and m.author == ctx.author)
            try:
              msg = await self.bot.wait_for("message", check=check, timeout=30)
            except Exception:
              return await ctx.send(f"{ctx.author.mention} you didn't answer on time")
            if msg.content == "b":
                try:
                    q = await aki.back()
                except akinator.CantGoBackAnyFurther:
                    pass
            else:
                q = await aki.answer(msg.content)
            question_num += 1
        await aki.win()

        embed = discord.Embed(
            title=
            f"It's {aki.first_guess['name']} ({aki.first_guess['description']})! Was I correct?\n\t",
            color=0xFF0000,
        )
        embed.set_image(url=f"{aki.first_guess['absolute_picture_path']}")
        embed.add_field(name="Reply with `yes/y` `no/n`", value="\u200b")
        await ctx.send(embed=embed)

        def check(m):
            return (m.content.lower() in ["yes", "y"]
                    and m.channel == ctx.channel and m.author == ctx.author)

        try: 
            correct = await self.bot.wait_for("message", check=check, timeout=30)
        except Exception: 
            return await ctx.send(f"{ctx.author.mention} you didn't answer on time")
        if correct.content.lower() == "yes" or correct.content.lower() == "y":
            embed = discord.Embed(title="Yay! I guessed it right",
                                  color=0xFF0000)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Oof! Kinda hard one",
                                  color=0xFF0000)
            await ctx.send(embed=embed)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(GuessName.guess())
        loop.close()
    
    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.guild)
    @commands.cooldown(1, 30, commands.BucketType.guild)
    @Context.with_type
    async def dial(self, ctx: Context, *, server: discord.Guild):
        """
        To dial to other server. Do not misuse this. Else you RIP :|
        """
        if server is ctx.guild: return await ctx.send(f"Can't make a self call")
        number = server.id
        channel = ctx.channel
        self_guild = await collection.find_one({'_id': ctx.guild.id})
        if not self_guild:
            return await ctx.send(
                f"{ctx.author.mention} no telephone line channel is set for this server, ask your Server Manager to fix this."
            )
        target_guild = await collection.find_one({'_id': number})
        if not target_guild:
            return await ctx.send(
                f"{ctx.author.mention} no telephone line channel is set for the **{number}** server, or the number you entered do not match with any other server!"
            )

        if target_guild['is_line_busy']:
            return await ctx.send(
                f"Can not make a connection to **{number} ({self.bot.get_guild(target_guild['_id']).name})**. Line busy!"
            )

        target_channel = self.bot.get_channel(target_guild['channel'])
        if not target_channel:
            return await ctx.send(
                "Calling failed! Possible reasons: `Channel deleted`, missing `View Channels` permission."
            )

        if (target_guild['_id'] in self_guild['blocked']) or (self_guild['_id'] in target_guild['blocked']):
            return await ctx.send(
                f'Calling failed! Possible reasons: They blocked You, You blocked Them.'
            )
        
        await ctx.send(
            f"Calling to **{number} ({self.bot.get_guild(target_guild['_id']).name})** ... Waiting for the response ..."
        )

        await target_channel.send(
            f"**Incoming call from {ctx.guild.id}. {ctx.guild.name} ...**\n`pickup` to pickup | `hangup` to reject"
        )
        try:
            temp_message = target_channel.send(
                f'{self.bot.get_guild(target_guild["_id"]).get_role(target_guild["pingrole"]).mention} {self.bot.get_user(target_guild["memberping"]).mention}'
            )
            await temp_message.delete()
        except Exception:
            pass

        def check(m):
            return (m.content.lower() in ("pickup", "hangup")) and (m.channel == channel or m.channel == target_channel) # and not m.author.bot

        try:
            _talk = await self.bot.wait_for('message', check=check, timeout=60)
        except Exception:
            await asyncio.sleep(0.5)
            await target_channel.send(
                f"Line disconnected from **{ctx.guild.id} ({ctx.guild.name})**. Reason: Line Inactive for more than 60 seconds"
            )
            await ctx.reply(
                f"Line disconnected from **{number} ({self.bot.get_guild(number).name})**. Reason: Line Inactive for more than 60 seconds"
            )

            await telephone_update(ctx.guild.id, 'is_line_busy', False)
            await telephone_update(number, 'is_line_busy', False)
            return

        if _talk.content.lower() == 'hangup':
            await ctx.send(f'Disconnected')
            await target_channel.send(f'Disconnected')
            await telephone_update(ctx.guild.id, 'is_line_busy', False)
            await telephone_update(number, 'is_line_busy', False)
            return

        elif _talk.content.lower() == 'pickup':
            await ctx.send(
                f"Connected. Say {random.choice(['hi', 'hello', 'heya'])}")
            await target_channel.send(
                f"Connected. Say {random.choice(['hi', 'hello', 'heya'])}")

            await telephone_update(ctx.guild.id, 'is_line_busy', True)
            await telephone_update(number, 'is_line_busy', True)
            ini = time.time() + 120
            while True:

                def check(m):
                    if (m.channel == target_channel) or (m.channel == channel) and (not m.author.bot): 
                        return True

                try:
                    talk_message = await self.bot.wait_for('message',
                                                          check=check,
                                                          timeout=60.0)
                except Exception:
                    await asyncio.sleep(0.5)
                    await target_channel.send(
                        f"Line disconnected from **{ctx.guild.id} ({ctx.guild.name})**. Reason: Line Inactive for more than 60 seconds"
                    )
                    await ctx.reply(
                        f"Line disconnected from **{number} ({self.bot.get_guild(number).name})**. Reason: Line Inactive for more than 60 seconds"
                    )

                    await telephone_update(ctx.guild.id, 'is_line_busy', False)
                    await telephone_update(number, 'is_line_busy', False)
                    return

                if talk_message.content.lower() == 'hangup':
                    await telephone_update(ctx.guild.id, 'is_line_busy', False)
                    await telephone_update(number, 'is_line_busy', False)
                    await ctx.send(f'Disconnected')
                    await target_channel.send(f'Disconnected')
                    return

                if talk_message.channel == target_channel:
                    await channel.send(
                        f"**{talk_message.author.name}#{talk_message.author.discriminator}** {talk_message.clean_content}"
                    )

                elif talk_message.channel == channel:
                    await target_channel.send(
                        f"**{talk_message.author.name}#{talk_message.author.discriminator}** {talk_message.clean_content}"
                    )
                if ini - time.time() <= 60: 
                    await channel.send(f'Disconnected. Call duration reached its maximum limit')
                    await target_channel.send(f'Disconnected. Call duration reached its maximum limit')
                    await telephone_update(ctx.guild.id, 'is_line_busy', False)
                    await telephone_update(number, 'is_line_busy', False)
                    return

def setup(bot):
  bot.add_cog(fun(bot))
