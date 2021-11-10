import discord
from discord import channel
from discord import player
from discord.ext import commands
import datetime

import asyncio
import random
from asyncio.tasks import sleep

from discord.ext.commands.core import group
import pymongo
from pymongo import MongoClient
import re
import itertools

from discord_buttons_plugin import *


intents = discord.Intents.default() # get the default intents where members and presence are disabled
intents.members = True # enable the members intent
client = commands.Bot(command_prefix='#', intents=intents)
buttons = ButtonsClient(client)

client.remove_command('help')

############################################################
# DATABASE PART
cluster = MongoClient(" ") ## MongoDBClient
db = cluster[" "] ## Databse
collection = db[" "] ## Collection

############################################################



@client.event
async def on_ready():
  print('Connected to client: {}'.format(client.user.name))
  print('client ID: {}'.format(client.user.id))
  activity = discord.Game(name="#help", type=3)
  await client.change_presence(status=discord.Status.online, activity=activity)




#---------------------------ส่วนของการนัดหมาย----------------------------------

@client.command()
async def dm(ctx, user: discord.User, *, msg):
  guild = client.get_guild( ) # <<- int id server
  member = guild.get_member(ctx.author.id)
  await ctx.send('ส่งข้อความสำเร็จ')
  await user.send(f'{msg}')

@client.command()
async def dmrole(ctx, role: discord.Role, *, args=None):
    guild = client.get_guild( )# <<- int id server
    member1 = guild.get_member(ctx.author.id)  
    tk = guild.get_role(role.id)
    members = tk.members
    if args != None:
        for member in members:
            try:
                await member.send(f'{args}')

            except:
                pass
            
            await ctx.send('ส่งข้อความสำเร็จ')
    
    else:
        await ctx.channel.send("You didnt provide arguments")


@client.command()
async def announce(ctx, channel: discord.TextChannel, *, msg):
    await ctx.send('ส่งข้อความสำเร็จ')
    await channel.send(f'{msg}')

@client.command(pass_context=True)
async def dmall(ctx, *, args=None):
    guild = client.get_guild( )# <<- int id server
    member1 = guild.get_member(ctx.author.id)  
    if args != None:
        members = ctx.guild.members  
        for member in members:
            try:
                await member.send(f'{args}')


            except:
                pass
        await ctx.send('ส่งข้อความสำเร็จ')    
    else:
        await ctx.channel.send("You didnt provide arguments")

#--------------------------------ส่วนของการกิจกรรมนัดหมาย--------------------------------

def convert(time):
  pos = ["s","m","h","d"]

  time_dict = {"s" : 1, "m" : 60, "h" : 3600, "d" : 3600*24}

  unit = time[-1]

  if unit not in pos:
    return -1
  try:
    val = int(time[:-1])
  except:
    return -2

  return val * time_dict[unit]  


@client.command()
async def cevent(ctx):
  await ctx.send("กรุณาตอบคำถามภายใน 15 วินาที")

  questions = ["ต้องการจัด Event ที่ Channel ใด? Ex/ #general",
  "ต้องการระยะเวลาของ Event นี้นานเท่าใด? (s|m|h|d)",
  "หัวข้อ Event?"]
  
  answers = []
  
  def check(m):
    return m.author == ctx.author and m.channel == ctx.channel

  for i in questions:
    await ctx.send(i)

    try:
      msg = await client.wait_for('message', timeout=15.0, check=check)
    except asyncio.TimeoutError:
      await ctx.send('คุณไม่ได้ตอบคำถามในเวลา, กรุณารีบๆตอบคำถาม')
      return
    else:
      answers.append(msg.content)
  
  try:
    c_id = int(answers[0][2:-1])
  except:
    await ctx.send("คุณไม่ได้เลือก Channel")
    return

  channel = client.get_channel(c_id)

  time = convert(answers[1])
  if time == -1:
    await ctx.send("คุณใช้หน่วยระยะเวลาผิด. กรุณาใช้หน่วย (s|m|h|d) ด้วย")
    return  
  elif time == -2:
    await ctx.send("เวลาต้องเป็น int. กรุณาใส่ int ครั้งหน้าด้วย")
    return
  print(time)
  prize = answers[2]
  await ctx.send(f"Event จะเริ่มต้นใน Channel {channel.mention} และจะเริ่มต้นใน {answers[1]}!")

  embed = discord.Embed(title = "Event!", description = f"{prize}", color = ctx.author.color)

  embed.add_field(name = "Event นี้จัดโดย:", value = ctx.author.mention)
  end = datetime.datetime.timestamp(datetime.datetime.now()) + time
  embed.add_field(name = f"จะจบ Event ในเวลา: ",value = f'<t:{int(end)}:R>',inline= False)


  players = []
  message1 = await ctx.send(embed = embed)

  emoji = '✅'

  await message1.add_reaction(emoji)




  def check1(reaction, user):
      return reaction.message.id == message1.id and user != client.user and str(
          reaction.emoji) in [emoji]

  while True:
 
    try:
        timeout1 = end - datetime.datetime.timestamp(datetime.datetime.now())
        if timeout1 <= 0:
          break
        print(timeout1)
        reaction, user = await client.wait_for("reaction_add", timeout=timeout1, check=check1)

        if user not in players and not user.bot:
            players.append(user)

        if str(reaction.emoji) == emoji:
            await user.send('คุณเข้าร่วม Event นี้')
            await message1.remove_reaction(reaction, user)


    except asyncio.TimeoutError:
        embed = discord.Embed(title = "จบกิจกรรมแล้วนะจ้ะ", description = "หมดเวลาลงทะเบียนแล้วววว", color = ctx.author.color)
        await message1.edit(embed=embed) 
        await message1.remove_reaction(reaction,client.user)
        for user in players:
            await user.send("อย่าลืมมาร่วม Event ที่ลงทะเบียนด้วยนะจ้ะ")

##########################################################################################################
                                #Saving Data
###########################################################################################################

Album = []
name = []

@client.command(pass_context=True, aliases=['cfolder'])
async def createfolder(ctx, nam=None):
    if nam is None:
        return await ctx.send("!createfolder (name) or !cfolder (name)")
    Album.append([])
    name.append(nam)
    ## Save key database
    d1 = {"key": nam} 
    if collection.find_one(d1):
        return  await ctx.send('คุณมี folder นี้อยู่แล้ว')
    collection.insert_one(d1)
    await ctx.send(str(nam) + ' ได้ถูกสร้างขึ้นแล้ว. คุณมี ' + str(collection.count_documents({})) + ' folder/s')

@client.command(pass_context=True, aliases=['p']) 
async def put(ctx, lenal=None,*,pic=None):
    if lenal is None or pic is None:
        return await ctx.send("!put (folder) (detail)")
    ## Update value database
    myquery = {"key": lenal }
    found = collection.find_one(myquery)
    if not found:
        return await ctx.send("คุณยังไม่มี folder นี้")
    newvalues = { "$push": { "value": f'{pic}\ถูกสร้างขึ้นเมื่อ : {datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}\nUser: <@{ctx.author.id}>'} }
    collection.update_one(myquery, newvalues, upsert = True)
    await ctx.send('ข้อความได้ถูกเพิ่มเข้าไปใน folder เรียบร้อย ' + lenal)

@client.command(pass_context=True, aliases=['v'])
async def view(ctx, lenal=None, pos=None):
    if lenal is None or pos is None:
        return await ctx.send("!view (folder) (position)")
    found = collection.find_one({"key": lenal})
    embedVar = discord.Embed(title=f"ข้อความจาก folder {str(lenal)} ตำแหน่งที่ {str(pos)}", description=str(found["value"][int(pos) -1]) , color=0x00ff00)    
    await ctx.send(embed=embedVar)
    
@client.command()
async def all(ctx):
    found_all = collection.find({})
    found_list = list(found_all)
    if len(found_list) == 0:
        await ctx.send("ไม่มี folder อยู่ในระบบ")
    else :
        await ctx.send("คณมี " + str(len(found_list)) + " folder/s")
        toSend = ""
        for u in range (len(found_list)):
            toSend += str(u+int(1))+str(". ")+str(found_list[u]["key"]) + "\n"
        await ctx.send(toSend) 

@client.command(pass_context=True, aliases=['dfolder'])
async def deletefolder(ctx, lenal=None):
    if lenal is None:
        return await ctx.send("!deletefolder (folder) or !dfolder (folder)")
    collection.delete_one({"key":lenal})
    await ctx.send("folder " + str(lenal) + " ถูกลบ")

@client.command(pass_context=True, aliases=['ddt'])
async def deletedetail(ctx, lenal=None, pos=None):
    if lenal is None or pos is None:
        return await ctx.send("!deletedetail (folder) (position) or !ddt (folder) (position)")
    collection.update_one({ "key": lenal}, {"$unset": {f'value.{int(pos)-1}': 1 }})
    collection.update_many({ "key": lenal}, {"$pull": {"value": None}})
    await ctx.send("ข้อความใน folder " + str(lenal) + " ตำแหน่งที่ " + pos + " ถูกลบเรียบร้อย")

@client.command(pass_context=True, aliases=['sfolder'])
async def showfolder(ctx,lenal=None):
    if lenal is None:
        return await ctx.send("!showfolder (folder) or !sfolder (folder)") 
    found_showal = collection.find_one({"key":lenal})


    if found_showal is None:
        return await ctx.send("ไม่มีโฟลเดอร์นั้น")
    elif "value" not in found_showal or len(found_showal["value"]) == 0:
        return await ctx.send("ไม่มีข้อมูลในโฟลเดอร์นั้น")
    else:
        page = 0
        contents = [""]

        for u in range(len(found_showal["value"])):
            if len(contents[page]+f'{str(u+1)}. {str(found_showal["value"][u])}\n\n') > 4096:
                page += 1
                contents.append(f'{str(u+1)}. {str(found_showal["value"][u])}\n\n')
            else:
                contents[page] += f'{str(u+1)}. {str(found_showal["value"][u])}\n\n'
        
        if contents[0] == "":
            contents[0] =  "Not Found"

        results = len(found_showal["value"])
        ttp = len(contents)
        cur_page = 1

        embedVar = discord.Embed(title=f'Total Result: {results} Page {cur_page}/{ttp}:', description=f'{contents[cur_page-1]}', color=0x00ff00)
        message = await ctx.send(embed=embedVar)
        # getting the message object for editing and reacting

        await message.add_reaction("⏮")
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        await message.add_reaction("⏭")
        await message.add_reaction("❌")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["⏮","◀️", "▶️","⏭","❌"]
            # This makes sure nobody except the command sender can interact with the "menu"

        while True:
            try:
                reaction, user = await client.wait_for("reaction_add", timeout=60, check=check)
                # waiting for a reaction to be added - times out after x seconds, 60 in this
                # example

                if str(reaction.emoji) == "▶️" and cur_page != ttp:
                    cur_page += 1
                    embedVar = discord.Embed(title=f'Total Result: {results} Page {cur_page}/{ttp}:', description=f'{contents[cur_page-1]}', color=0x00ff00)
                    await message.edit(embed = embedVar)
                    await message.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "◀️" and cur_page > 1:
                    cur_page -= 1
                    embedVar = discord.Embed(title=f'Total Result: {results} Page {cur_page}/{ttp}:', description=f'{contents[cur_page-1]}', color=0x00ff00)
                    await message.edit(embed = embedVar)
                    await message.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "⏭" and cur_page != ttp:
                    cur_page = ttp
                    embedVar = discord.Embed(title=f'Total Result: {results} Page {cur_page}/{ttp}:', description=f'{contents[cur_page-1]}', color=0x00ff00)
                    await message.edit(embed = embedVar)
                    await message.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "⏮" and cur_page > 1:
                    cur_page = 1
                    embedVar = discord.Embed(title=f'Total Result: {results} Page {cur_page}/{ttp}:', description=f'{contents[cur_page-1]}', color=0x00ff00)
                    await message.edit(embed = embedVar)
                    await message.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "❌":
                    await message.delete()
                    break

                else:
                    await message.remove_reaction(reaction, user)
                    # removes reactions if the user tries to go forward on the last page or
                    # backwards on the first page
            except asyncio.TimeoutError:
                await message.delete()
                break
                # ending the loop if user doesn't react after x seconds
    

    

@client.command(pass_context=True, aliases=['sr-folder'])
async def searchfolder(ctx,keyy=None,search_str=None):
    if keyy is None or search_str is None:
        return await ctx.send("!searchfolder (folder) (keyword) or !srfolder (folder) (keyword)")
        
    found_shgrp = collection.find_one({"key":keyy})

    num = 0
    page = 0
    contents = [""]

    for x in found_shgrp["value"]:
        if search_str.upper() in x.upper():
            num += 1
            if len(contents[page]+f'{num}. {x}\n\n') > 4096:
                page += 1
                contents.append(f'{num}. {x}\n\n')
            else:
                contents[page] += f'{num}. {x}\n\n'

    # print(contents)       

    if contents[0] == "":
        contents[0] =  "Not Found"

    ttp = len(contents)
    cur_page = 1

    embedVar = discord.Embed(title=f'Total Result: {num} Page {cur_page}/{ttp}:', description=f'{contents[cur_page-1]}', color=0x00ff00)
    message = await ctx.send(embed=embedVar)
    # getting the message object for editing and reacting

    await message.add_reaction("⏮")
    await message.add_reaction("◀️")
    await message.add_reaction("▶️")
    await message.add_reaction("⏭")
    await message.add_reaction("❌")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["⏮","◀️", "▶️","⏭","❌"]
        # This makes sure nobody except the command sender can interact with the "menu"

    while True:
        try:
            reaction, user = await client.wait_for("reaction_add", timeout=60, check=check)
            # waiting for a reaction to be added - times out after x seconds, 60 in this
            # example

            if str(reaction.emoji) == "▶️" and cur_page != ttp:
                cur_page += 1
                embedVar = discord.Embed(title=f'Total Result: {num} Page {cur_page}/{ttp}:', description=f'{contents[cur_page-1]}', color=0x00ff00)
                await message.edit(embed = embedVar)
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "◀️" and cur_page > 1:
                cur_page -= 1
                embedVar = discord.Embed(title=f'Total Result: {num} Page {cur_page}/{ttp}:', description=f'{contents[cur_page-1]}', color=0x00ff00)
                await message.edit(embed = embedVar)
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "⏭" and cur_page != ttp:
                cur_page = ttp
                embedVar = discord.Embed(title=f'Total Result: {num} Page {cur_page}/{ttp}:', description=f'{contents[cur_page-1]}', color=0x00ff00)
                await message.edit(embed = embedVar)
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "⏮" and cur_page > 1:
                cur_page = 1
                embedVar = discord.Embed(title=f'Total Result: {num} Page {cur_page}/{ttp}:', description=f'{contents[cur_page-1]}', color=0x00ff00)
                await message.edit(embed = embedVar)
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "❌":
                await message.delete()
                break

            else:
                await message.remove_reaction(reaction, user)
                # removes reactions if the user tries to go forward on the last page or
                # backwards on the first page
        except asyncio.TimeoutError:
            await message.delete()
            break
            # ending the loop if user doesn't react after x seconds

@client.command(pass_context=True, aliases=['s'])
async def search(ctx,search_str=None):
    if search_str is None:
        return await ctx.send("!search (keyword) or !s (keyword)")
    
    results = 0
    page = 0
    contents = [""]

    regx = re.compile(f"{search_str}",re.IGNORECASE)
    found = collection.aggregate([
        { "$match" : {
            "value": { "$regex": regx }
        }},
        { "$unwind" : "$value" },
        { "$match" : {
            "value": { "$regex": regx }
        }}]
    )

    for _, category in itertools.groupby(found, key=lambda item:item['key']):
        numm = 0
        list1 = list(category)
        contents[page] += f'From Folder: {list1[0]["key"]}\n\n'
        for i in list1:
            numm += 1
            results += 1
            if len(i["value"]) > 100:
                i["value"] = i["value"] + "..."
            if len(contents[page]+f'{numm}. {i["value"]}\n\n') > 4096:
                page += 1
                contents.append(f'{numm}. {i["value"]}\n\n')
            else:
                contents[page] += f'{numm}. {i["value"]}\n\n'
        contents[page] += '\n'

    if contents[0] == "":
        contents[0] =  "Not Found"

    ttp = len(contents)
    cur_page = 1

    embedVar = discord.Embed(title=f'Total Result: {results}', description=f'{contents[cur_page-1]}', color=0x00ff00)    
    message = await ctx.send(embed=embedVar)
    # getting the message object for editing and reacting

    await message.add_reaction("⏮")
    await message.add_reaction("◀️")
    await message.add_reaction("▶️")
    await message.add_reaction("⏭")
    await message.add_reaction("❌")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["⏮","◀️", "▶️","⏭","❌"]
        # This makes sure nobody except the command sender can interact with the "menu"

    while True:
        try:
            reaction, user = await client.wait_for("reaction_add", timeout=60, check=check)
            # waiting for a reaction to be added - times out after x seconds, 60 in this
            # example

            if str(reaction.emoji) == "▶️" and cur_page != ttp:
                cur_page += 1
                embedVar = discord.Embed(title=f'Total Result: {results} Page {cur_page}/{ttp}:', description=f'{contents[cur_page-1]}', color=0x00ff00)
                await message.edit(embed = embedVar)
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "◀️" and cur_page > 1:
                cur_page -= 1
                embedVar = discord.Embed(title=f'Total Result: {results} Page {cur_page}/{ttp}:', description=f'{contents[cur_page-1]}', color=0x00ff00)
                await message.edit(embed = embedVar)
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "⏭" and cur_page != ttp:
                cur_page = ttp
                embedVar = discord.Embed(title=f'Total Result: {results} Page {cur_page}/{ttp}:', description=f'{contents[cur_page-1]}', color=0x00ff00)
                await message.edit(embed = embedVar)
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "⏮" and cur_page > 1:
                cur_page = 1
                embedVar = discord.Embed(title=f'Total Result: {results} Page {cur_page}/{ttp}:', description=f'{contents[cur_page-1]}', color=0x00ff00)
                await message.edit(embed = embedVar)
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "❌":
                await message.delete()
                break

            else:
                await message.remove_reaction(reaction, user)
                # removes reactions if the user tries to go forward on the last page or
                # backwards on the first page
        except asyncio.TimeoutError:
            await message.delete()
            break
            # ending the loop if user doesn't react after x seconds

@buttons.click
async def mainpage(ctx):
    embed = discord.Embed(title='Hamster command', description="สวัสดีเราคือบอทของโรงเรียน Smart School\n"
    "หรืออีกชื่อที่คนรู้จักก็คืออ HamsterHub นั้นเอง\n"
    "\n"
    "\n"
    "**Prefix ของเราก็คือ**: `#`", color=0xffcc00)
    embed.set_image(url='https://cdn.discordapp.com/icons/699984143542517801/10f65a4e9d0ba090224ae7819f9813a4.webp?size=128')
    await ctx.message.edit(embed = embed)
    await ctx.reply()

@buttons.click
async def dm(ctx):
    embed = discord.Embed(title='ระบบการ Dm', description="**สำหรับ User** `dm (@tagเพื่อน) (ข้อความ)`-เพื่อที่จะส่งหาคนๆนั้น\n"
    "**สำหรับ Admin** `dmrole (role) (ข้อความ)`-เพื่อส่งข้อความไปยัง role ทั้งหมด"
    "**สำหรับ Admin** `announce (#ห้องที่ต้องการ) (ข้อความ)`-เพื่อที่จะส่งข้อความไปยังห้องที่เลือ\n"
    "**สำหรับ Admin** `dmall (ข้อความ)`-เพื่อส่งข้อความหาคนทั้งหมดใน server", color=0xffcc00)
    await ctx.message.edit(embed = embed)
    await ctx.reply()



@buttons.click
async def keep(ctx):
    embed = discord.Embed(title='ระบบการบันทึกข้อความ & การเสริช \n**ในรูปแบบ Text**', description="`createfolder (ชื่อfolder)`-เพื่อสร้างfolder\n"
    "`put (folder) (ข้อมูล)`-เพื่อใส่ข้อมูล\n"
    "`all`-เพื่อดูชื่อ folder ทั้งหมด\n"
    "`showfolder (folder)`-เพื่อดูข้อมูลที่อยู่ใน folder นั้น\n"
    "`view (folder) (position)`-เพื่อดูข้อมูลในตำแหน่งที่กำหนดของ folder ที่เลือก\n"
    "`search (Keyword)`-หาคำๆนั้น\n"
    "`searchfolder (folder) (keyword)`-เพื่อดูคำๆนั้นใน folder\n"
    "`deletedetail (folder) (position)`-เพื่อลบข้อมูลใน folder ตามตำแหน่ง\n"
    "`deletefolder (folder)`-เพื่อลบ folder", color=0xffcc00)
    await ctx.message.edit(embed = embed)
    await ctx.reply()

@buttons.click
async def delete(ctx):
    await ctx.message.delete()
    await ctx.reply()    

@buttons.click
async def event(ctx):
    embed = discord.Embed(title='การสร้าง Event', description="**สำหรับ Admin**`cevent`-เพื่อสร้าง Event", color=0xffcc00)
    await ctx.message.edit(embed = embed)
    await ctx.reply()

@client.command()
async def help(ctx):
    embed = discord.Embed(title='Hamster command', description="สวัสดีเราคือบอทของโรงเรียน Smart School\n"
    "หรืออีกชื่อที่คนรู้จักก็คืออ HamsterHub นั้นเอง\n"
    "\n"
    "\n"
    "**Prefix ของเราก็คือ**: `#`", color=0xffcc00)
    embed.set_image(url='https://cdn.discordapp.com/icons/699984143542517801/10f65a4e9d0ba090224ae7819f9813a4.webp?size=128')
    await buttons.send(
		content=None,
        embed = embed,
		channel = ctx.channel.id,
		components = [
			ActionRow([
				Button(

					style = ButtonType().Primary,
					label = "🏠หน้าหลัก",
					custom_id = "mainpage",

				),

				Button(
					style = ButtonType().Success,
					label = "📧ระบบการ Dm",
					custom_id = "dm"
				),
				Button(
					style = ButtonType().Success,
					label = "📣ระบบการสร้าง Event",
					custom_id = "event",
				)
			]),
            ActionRow([
                Button(
                    style = ButtonType().Success,
                    label = "📌Keep & 🔍Search",
                    custom_id = "keep"
                ),
                Button(
                    style = ButtonType().Link,
                    label = "หน้าเว็ป/Webpage",
                    url = "http://hamsterhub.co/",
                ),
                Button(
                    style = ButtonType().Danger,
                    label = "X",
                    custom_id = "delete"
                )
            ])

		]
	)

client.run(" ") #<- Discord Token
