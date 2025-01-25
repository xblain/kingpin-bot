from pilmoji import Pilmoji
from pilmoji.source import TwitterEmojiSource
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
from hikari.snowflakes import Snowflake
import datetime
import numpy as np
import textwrap
import database
import hikari
import random


#Will move this functionality to its own application later in time so load can be separated from the rest of the code

async def background(member):
    backint = database.getStat(member, 'background')
    if backint != 0:
        backgroundImg = Image.open(f"images/homes/items/{backint}_0.png")
    else:
        backgroundImg = Image.open(f"images/phone_files/backgroundbase.png")
    return backgroundImg
async def menuText(left : str=""):
    right = "KINGPIN NETWORK"
    menuImg = Image.new("RGBA", (570,22), color="#0D0D13")
    font = ImageFont.truetype("fonts/VT323-Regular.ttf", 20)
    draw = ImageDraw.Draw(menuImg)

    #_, _, w, h = draw.textlength(right.upper(), font=font)

    w = draw.textlength(right.upper(), font=font)
    #h = font.size

    draw.text((10,1),left.upper(), (255,255,255), font=font)
    draw.text((568-w-10,1),right.upper(), (255,255,255), font=font)
    return menuImg

async def PhoneOverlay(user):
    if (database.getStat(user, "harvest") == 1 and database.getHarvestTimer(user).min() <= datetime.datetime.now()) or (
        database.getStat(user, 'lastdaily') <= (datetime.datetime.now() - datetime.timedelta(days = 1))):
        path = "images/renders/phones/menu/"+str(user)+"-overlay.png"
        notif = Image.open("images/phone_files/phoneoverlaynotification.png")
        overlay = Image.open("images/phone_files/phoneoverlay.png")
        overlay.paste(notif,(0,0),notif.convert('RGBA'))
        overlay.save(path)
        return str(path)
    else:
        return "images/phone_files/phoneoverlay.png"

async def registerUser():
    overlayImg = Image.open("images/phone_files/phoneoverlay.png")
    backgroundImg = Image.open("images/phone_files/registerbackground.png")
    phoneImg = Image.new("RGBA", (600,600))
    path = "images/renders/phones/menu/register.png"
    menuImg = await menuText("Connecting to network")
    phoneImg.paste(backgroundImg,(15,97),backgroundImg.convert('RGBA'))
    phoneImg.paste(menuImg,(15,75),menuImg.convert('RGBA'))
    phoneImg.paste(overlayImg,(0,0),overlayImg.convert('RGBA'))

    phoneImg.save(path)
    return path

async def GetPhoneMenu(user : Snowflake):
    overlayImg = Image.open(await PhoneOverlay(user))
    backgroundImg = await background(user)

    phoneImg = Image.new("RGBA", (600,600))
    path = "images/renders/phones/menu/"+str(user)+".png"
    menuImg = await menuText("menu")
    OssoImg = await menuIcon("Your Crib", str(user))
    ActivitiesImg = await menuIcon("Activities", str(user))
    QuestsImg = await menuIcon("Quests", str(user))
    ProfileImg = await menuIcon("Profile", str(user))
    PocketImg = await menuIcon("Pocket", str(user))
    HiscoresImg = await menuIcon("Hi-scores", str(user))
    SettingsImg = await menuIcon("Settings", str(user))
    ShopImg = await menuIcon("Store", str(user))
    phoneImg.paste(backgroundImg,(15,97),backgroundImg.convert('RGBA'))
    phoneImg.paste(menuImg,(15,75),menuImg.convert('RGBA'))
    phoneImg.paste(OssoImg,(115,110),OssoImg.convert('RGBA'))
    phoneImg.paste(ActivitiesImg,(247,110),ActivitiesImg.convert('RGBA'))
    phoneImg.paste(QuestsImg,(379,110),QuestsImg.convert('RGBA'))
    phoneImg.paste(ProfileImg,(115,252),ProfileImg.convert('RGBA'))
    phoneImg.paste(HiscoresImg,(247,252),HiscoresImg.convert('RGBA'))
    phoneImg.paste(PocketImg,(379,252),PocketImg.convert('RGBA'))
    phoneImg.paste(ShopImg,(115,394),ShopImg.convert('RGBA'))
    phoneImg.paste(SettingsImg,(247,394),SettingsImg.convert('RGBA'))
    #phoneImg.paste(OssoImg,(379,394),OssoImg.convert('RGBA'))
    phoneImg.paste(overlayImg,(0,0),overlayImg.convert('RGBA'))

    phoneImg.save(path)
    return path

async def GetBegging(user : Snowflake):
    overlayImg = Image.open(await PhoneOverlay(user))
    backgroundImg = Image.open("images/phone_files/begbackground.png")

    phoneImg = Image.new("RGBA", (600,600))
    path = "images/renders/phones/menu/beg"+str(user)+".png"
    menuImg = await menuText("begging")
    phoneImg.paste(backgroundImg,(15,97),backgroundImg.convert('RGBA'))
    phoneImg.paste(menuImg,(15,75),menuImg.convert('RGBA'))

    font = ImageFont.truetype("fonts/VT323-Regular.ttf", 70)
    draw = ImageDraw.Draw(phoneImg)

    if database.getStat(user, "lastbeg") + datetime.timedelta(seconds=30) >= datetime.datetime.now():
        w = draw.textbbox((0, 0), '0'+str(database.getStat(user, "lastbeg") + datetime.timedelta(seconds=30) - datetime.datetime.now())[:-7], font=font)[2]
        draw.text((300-(w/2),140),'0'+str(database.getStat(user, "lastbeg") + datetime.timedelta(seconds=30) - datetime.datetime.now())[:-7], (255,255,255), font=font)
    else:
        w = draw.textbbox((0, 0), 'ARE YOU SURE?', font=font)[2]

        draw.text((300-(w/2),140),'ARE YOU SURE?', (255,255,255), font=font)

    phoneImg.paste(overlayImg,(0,0),overlayImg.convert('RGBA'))

    phoneImg.save(path)
    return path

async def GetRobbing(user, ctx):
    overlayImg = Image.open(await PhoneOverlay(ctx.interaction.member.id))
    backgroundImg = Image.new("RGBA", (570,450), 'black')
    phoneImg = Image.new("RGBA", (600,600))
    placeholderImg = Image.new("RGBA", (100,100),"white")
    path = "images/renders/phones/menu/rob"+str(ctx.interaction.member.id)+".png"
    menuImg = await menuText("robbing")
    phoneImg.paste(backgroundImg,(15,97),backgroundImg.convert('RGBA'))
    phoneImg.paste(menuImg,(15,75),menuImg.convert('RGBA'))

    font = ImageFont.truetype("fonts/VT323-Regular.ttf", 60)
    font2 = ImageFont.truetype("fonts/VT323-Regular.ttf", 30)
    draw = ImageDraw.Draw(phoneImg)
    lastrob = database.getStat(ctx.interaction.member.id, "lastrob")
    current_time = datetime.datetime.now()
    threshold_time = lastrob + datetime.timedelta(hours=4)

    rob_attempts = database.getStat(ctx.interaction.member.id, "rob")
    if rob_attempts > 0:
        time_left = datetime.timedelta(hours=2)-(datetime.datetime.now()-database.getStat(ctx.interaction.member.id,"lastrob"))
        msg = f'{rob_attempts}/4 ROB ATTEMPTS USED, REFRESH IN {time_left}'[:-7]
        w = draw.textbbox((0, 0), msg, font=font2)[2]
        draw.text((300-(w/2),110), msg, (255,255,255), font=font2)
    else:
        w = draw.textbbox((0, 0), f'0/4 ROB ATTEMPTS USED', font=font2)[2]
        draw.text((300-(w/2),110), f'0/4 ROB ATTEMPTS USED', (255,255,255), font=font2)
    phoneImg.paste(overlayImg,(0,0),overlayImg.convert('RGBA'))

    phoneImg.save(path)
    return path

async def GetPocket(user : Snowflake, itemid : int):
    overlayImg = Image.open(await PhoneOverlay(user))
    backgroundImg = await background(user)

    itemdb = database.getItemDetailedDB(itemid)
    itemdb = list(itemdb)
    if "{reward}" in itemdb[2]:
        itemdb[2] = itemdb[2].replace("{reward}", str(database.getItemDB(itemid, 'reward')))

    if "{money}" in itemdb[2]:
        itemdb[2] = itemdb[2].replace("{money}", database.money)

    phoneImg = Image.new("RGBA", (600,600))
    path = "images/renders/phones/menu/item"+str(user)+".png"
    menuImg = await menuText("pocket")
    phoneImg.paste(backgroundImg,(15,97),backgroundImg.convert('RGBA'))
    phoneImg.paste(menuImg,(15,75),menuImg.convert('RGBA'))

    font = ImageFont.truetype("fonts/VT323-Regular.ttf", 40)
    bigEmojiFont = ImageFont.truetype("fonts/VT323-Regular.ttf", 200)
    draw = ImageDraw.Draw(phoneImg)


    try:
        
        
        if database.getItemDB(itemid, 'behaviour') == "BCK":
            img1 = Image.open("images/homes/items/"+str(itemid)+"_0.png")
            W, H = img1.size
            phoneImg.paste(img1,(15,97),img1.convert('RGBA'))

        elif database.getItemDB(itemid, 'behaviour') == "UPG":
            crib = None
            itemid = int(itemid)
            print(itemid, database.getHome(user)['huistype'])
            if itemid == 9901 and database.getHome(user)['huistype']== 'starter':
                crib = await drawHome(user, y=True)
            if itemid == 9900 and database.getHome(user)['huistype']== 'starter':
                crib = await drawHome(user, x=True)
            if itemid == 9902 and database.getHome(user)['huistype']== 'starterx':
                crib = await drawHome(user, y=True)
            if itemid == 9902 and database.getHome(user)['huistype']== 'startery':
                crib = await drawHome(user, x=True)
            if itemid == 9903 and database.getHome(user)['huistype']== 'starterx':
                crib = await drawHome(user, y=True)
            if itemid == 9904 and database.getHome(user)['huistype']== 'startery':
                crib = await drawHome(user, x=True)
            W,H = phoneImg.size
            w,h = crib.size

            phoneImg.paste(crib,(int((W/2)-(w/2)),int((H/2)-(h/2))),crib.convert('RGBA'))
        elif database.getItemDB(itemid, 'behaviour') == "WAL":
            crib = await drawHome(user,drawWall=int(itemid))
            W,H = phoneImg.size
            w,h = crib.size

            phoneImg.paste(crib,(int((W/2)-(w/2)),int((H/2)-(h/2))),crib.convert('RGBA'))
        elif database.getItemDB(itemid, 'behaviour') == "FLR":
            crib = await drawHome(user,drawFloor=int(itemid))
            W,H = phoneImg.size
            w,h = crib.size
            phoneImg.paste(crib,(int((W/2)-(w/2)),int((H/2)-(h/2))),crib.convert('RGBA'))
        elif itemid == -100:
            #already supports discord emoji's :)
            Pilmoji(phoneImg).text((283,280), database.money, font=bigEmojiFont, stroke_width=3, fill='black', stroke_fill='white', anchor= 'mt')
        elif itemid == -200:
            #already supports discord emoji's :)
            Pilmoji(phoneImg).text((283,280), database.credit, font=bigEmojiFont, stroke_width=3, fill='black', stroke_fill='white', anchor= 'mt')
        else:
            img1 = Image.open("images/homes/items/"+str(itemid)+"_0.png")
            W, H = img1.size
            phoneImg.paste(img1,(206,490-H),img1.convert('RGBA'))
    except Exception as e: 
        print(e)


    w = draw.textbbox((0, 0), itemdb[1].title(), font=font, stroke_width=3)[2]
    draw.text((300- int(w/2),103), str(itemdb[1]).title(), font=font, stroke_width=3, fill='black', stroke_fill='white')
    
    desc = textwrap.fill(text=itemdb[2], width= 30)

    w = draw.textbbox((0, 0), desc, font=font, stroke_width=3)[2]
    Pilmoji(phoneImg).text((300- int(w/2),150), desc, font=font, stroke_width=3, fill='black', stroke_fill='white')



    


        

    phoneImg.paste(overlayImg,(0,0),overlayImg.convert('RGBA'))

    phoneImg.save(path)
    return path

async def GetActivitiesMenu(user : Snowflake):
    overlayImg = Image.open(await PhoneOverlay(user))
    backgroundImg = await background(user)

    phoneImg = Image.new("RGBA", (600,600))
    path = "images/renders/phones/menu/activities"+str(user)+".png"
    menuImg = await menuText("activities")
    BegImg = await menuIcon("Beg", str(user))
    RobImg = await menuIcon("Rob", str(user))
    FishImg = await menuIcon("Fishing", str(user))
    EnterprisesImg = await menuIcon("Enterprise", str(user))
    ExploreImg = await menuIcon("Explore", str(user))
    JobImg = await menuIcon("Work Job", str(user))
    phoneImg.paste(backgroundImg,(15,97),backgroundImg.convert('RGBA'))
    phoneImg.paste(menuImg,(15,75),menuImg.convert('RGBA'))
    phoneImg.paste(BegImg,(115,110),BegImg.convert('RGBA'))
    phoneImg.paste(RobImg,(247,110),RobImg.convert('RGBA'))
    phoneImg.paste(FishImg,(379,110),FishImg.convert('RGBA'))
    phoneImg.paste(EnterprisesImg,(115,252),EnterprisesImg.convert('RGBA'))
    phoneImg.paste(ExploreImg,(247,252),ExploreImg.convert('RGBA'))
    phoneImg.paste(JobImg,(379,252),JobImg.convert('RGBA'))
    #phoneImg.paste(ShopImg,(115,394),ShopImg.convert('RGBA'))
    #phoneImg.paste(SettingsImg,(247,394),SettingsImg.convert('RGBA'))
    #phoneImg.paste(OssoImg,(379,394),OssoImg.convert('RGBA'))
    phoneImg.paste(overlayImg,(0,0),overlayImg.convert('RGBA'))

    phoneImg.save(path)
    return path

async def GetStore(user : Snowflake):
    overlayImg = Image.open(await PhoneOverlay(user))
    backgroundImg = await background(user)
    shopImg = Image.open("images/phone_files/shop.png")
    menuImg = await menuText("store")
    phoneImg = Image.new("RGBA", (600,600))
    path = "images/renders/phones/menu/shop"+str(user)+".png"

    phoneImg.paste(backgroundImg,(15,97),backgroundImg.convert('RGBA'))
    phoneImg.paste(menuImg,(15,75),menuImg.convert('RGBA'))
    phoneImg.paste(shopImg,(15,97),shopImg.convert('RGBA'))
    phoneImg.paste(overlayImg,(0,0),overlayImg.convert('RGBA'))

    phoneImg.save(path)
    return path

async def GetStoreCrib(user : Snowflake):
    overlayImg = Image.open(await PhoneOverlay(user))
    backgroundImg = await background(user)
    shopImg = Image.open("images/phone_files/shopcrib.png")
    menuImg = await menuText("store")
    phoneImg = Image.new("RGBA", (600,600))
    path = "images/renders/phones/menu/shop"+str(user)+".png"

    phoneImg.paste(backgroundImg,(15,97),backgroundImg.convert('RGBA'))
    phoneImg.paste(menuImg,(15,75),menuImg.convert('RGBA'))
    phoneImg.paste(shopImg,(15,97),shopImg.convert('RGBA'))
    phoneImg.paste(overlayImg,(0,0),overlayImg.convert('RGBA'))

    phoneImg.save(path)
    return path

async def GetFishing(user : Snowflake, channel):
    overlayImg = Image.open(await PhoneOverlay(user))
    backint = int((datetime.datetime.now().timestamp() % 4) + 1)
    bobint = random.randint(1,4)
    otherBobint = random.randint(1,2)
    backgroundImg = Image.open(f"images/phone_files/fishingbackground{backint}.png")

    phoneImg = Image.new("RGBA", (600,600))
    path = "images/renders/phones/menu/fishing"+str(user)+".png"
    menuImg = await menuText("fishing")
    transpaste = Image.new("RGBA", (600,600))
    phoneImg.paste(backgroundImg,(15,97),backgroundImg.convert('RGBA'))
    phoneImg.paste(menuImg,(15,75),menuImg.convert('RGBA'))
    phoneImg.paste(overlayImg,(0,0),overlayImg.convert('RGBA'))
    rodImg = Image.open(f"images/phone_files/fishingbob{bobint}.png")
    otherRodImg = Image.open(f"images/phone_files/otherbob{otherBobint}.png")
    catchImg = Image.open(f"images/phone_files/fishingbobunderwater.png")
    if channel in database.fishingchannels:
        for x, i in enumerate(database.fishingchannels[channel]):
            for y, e in enumerate(i):
                if e > 0:
                    if e == user:
                        if await database.hasFishBitten(user, channel):
                            transpaste.paste(catchImg,(30 +(114*y),112+(113*x)),catchImg)
                        else:
                            transpaste.paste(rodImg,(30 +(114*y),112+(113*x)),rodImg)
                    elif await database.hasFishBitten(database.fishingchannels[channel][x][y], channel):
                        transpaste.paste(catchImg,(30 +(114*y),112+(113*x)),catchImg)
                    else:
                        transpaste.paste(otherRodImg,(30 +(114*y),112+(113*x)),otherRodImg)

    phoneImg = Image.alpha_composite(phoneImg, transpaste)



    phoneImg.save(path)
    return path




# NEEDS TO BE CLEANED
async def drawHome(gebruiker: hikari.User, help=False, drawFloor=-1, drawWall=-1, x=False,y=False):
    if x:
        homelayout = database.getHomeLayoutStore(gebruiker, x=True)
    elif y:
        homelayout = database.getHomeLayoutStore(gebruiker, y=True)
    else:
        homelayout = database.getHomeLayout(gebruiker)
    home = database.getHome(gebruiker)
    #fnt = ImageFont.truetype("images/homes/fonts/CREDC___.ttf", 25)
    gif = False
    background = Image.new("RGBA",(1,1))
    shadowbackground = Image.new("RGBA", (1, 1))

    if np.shape(homelayout) == (2, 2):
        extrawidth = 80
        extraheight = 80
        flooroffsetw = 408
        flooroffseth = 424
        walloffsetw = 408
        walloffseth = 225
        wallsidelx, wallsidely = 6,102
        wallsiderx, wallsidery = 10,102
        objectw, objecth = 306, 345
        im = Image.open("images/homes/types/starter.png")
        mask = Image.open('images/homes/masks/startermaskfloor.png').convert('L')
        maskwall = Image.open('images/homes/masks/startermask.png').convert('L')

    if np.shape(homelayout) == (2, 3):
        extrawidth = 80
        extraheight = 80
        flooroffsetw = 396
        flooroffseth = 364
        walloffsetw = 298
        walloffseth = 214
        wallsidelx, wallsidely = 16,159+4
        wallsiderx, wallsidery = 22,110+4
        objectw, objecth = 415, 350
        im = Image.open("images/homes/types/32.png")
        mask = Image.open('images/homes/masks/32maskfloor.png').convert('L')
        maskwall = Image.open('images/homes/masks/32mask.png').convert('L')
    if np.shape(homelayout) == (2, 4):
        extrawidth = 80
        extraheight = 80
        flooroffsetw = 400
        flooroffseth = 318
        walloffsetw = 203
        walloffseth = 220
        wallsidelx, wallsidely = 9,208
        wallsiderx, wallsidery = 11,110
        objectw, objecth = 322+188, 344
        im = Image.open("images/homes/types/42.png")
        mask = Image.open('images/homes/masks/42maskfloor.png').convert('L')
        maskwall = Image.open('images/homes/masks/42mask.png').convert('L')
    if np.shape(homelayout) == (3, 2):
        extrawidth = 80
        extraheight = 80
        flooroffsetw = 297
        flooroffseth = 362
        walloffsetw = 397
        walloffseth = 216
        wallsidelx, wallsidely = 16,159-50
        wallsiderx, wallsidery = 23,110+50
        objectw, objecth = 317, 350
        im = Image.open("images/homes/types/23.png")
        mask = Image.open('images/homes/masks/23maskfloor.png').convert('L')
        maskwall = Image.open('images/homes/masks/23mask.png').convert('L')
    if np.shape(homelayout) == (3, 3):
        extrawidth = 80
        extraheight = 80
        flooroffsetw = 301
        flooroffseth = 318
        walloffsetw = 299
        walloffseth = 220
        wallsidelx, wallsidely = 11,159
        wallsiderx, wallsidery = 15,159
        objectw, objecth = 416, 346
        im = Image.open("images/homes/types/33.png")
        mask = Image.open('images/homes/masks/33maskfloor.png').convert('L')
        maskwall = Image.open('images/homes/masks/33mask.png').convert('L')
    if np.shape(homelayout) == (4, 2):
        extrawidth = 80
        extraheight = 80
        flooroffsetw = 208
        flooroffseth = 318
        walloffsetw = 402
        walloffseth = 220
        wallsidelx, wallsidely = 9,110
        wallsiderx, wallsidery = 11,208
        objectw, objecth = 312, 344
        im = Image.open("images/homes/types/24.png")
        mask = Image.open('images/homes/masks/24maskfloor.png').convert('L')
        maskwall = Image.open('images/homes/masks/24mask.png').convert('L')

    if np.shape(homelayout) == (6, 6):
        extrawidth = 0
        extraheight = 0
        flooroffsetw = 0
        flooroffseth = 0
        walloffsetw = 0
        walloffseth = 198
        wallsidelx, wallsidely = 0,0
        wallsiderx, wallsidery = 0,0
        objectw, objecth = 706, 370
        im = Image.open("images/homes/types/master.png")
        mask = Image.open('images/homes/masks/mastermaskfloor.png').convert('L')
        maskwall = Image.open('images/homes/masks/mastermask.png').convert('L')
        background.save("images/homes/backgrounds/"+str(gebruiker)+".png", "PNG")



    size = list(im.size)
    size[0] = int(extrawidth) + size[0]
    size[1] = int(extraheight) + size[1]
    tsize = tuple(size)
    imwidth, imheight = im.size



    if database.getHome(gebruiker)['vloer'] != -1 or drawFloor >= 0:
        if drawFloor >= 0:
            floorid = drawFloor
        else:
            floorid = database.getHome(gebruiker)['vloer']
        wall = Image.open(f"images/homes/floors/{floorid}_1.png")
        croppedfloor = wall.crop((flooroffsetw, flooroffseth, imwidth+flooroffsetw, imheight+flooroffseth))
        im = Image.composite(im, croppedfloor, mask)
        

    if database.getHome(gebruiker)['behang'] != -1 or drawWall >= 0:
        if drawWall >= 0:
            wallid = drawWall
        else:
            wallid = database.getHome(gebruiker)['behang']
        wall = Image.open(f"images/homes/walls/{wallid}_1.png")
        croppedwall = wall.crop((walloffsetw, walloffseth, imwidth+walloffsetw, imheight+walloffseth))
        im = Image.composite(im, croppedwall, maskwall)
        if np.shape(homelayout) != (6, 6):
            wallside = Image.open(f"images/homes/walls/{wallid}_1_side.png")
            im.paste(wallside,(wallsidelx,wallsidely))
            wallside = ImageOps.mirror(wallside)
            im.paste(wallside,(imwidth-wallsiderx,wallsidery))
    background = ImageOps.fit(background, tsize, bleed = 0.0, centering =(0.5, 0.5))
    background.paste(im, (int(extrawidth / 2), int(extraheight / 2)), im)
    shadowbackground = ImageOps.fit(Image.new("RGBA",(1,1)), tsize, bleed = 0.0, centering =(0.5, 0.5))

    #background.save("images/homes/get.gif", save_all=True, loop=0)
    itembackground= shadowbackground
    background = background.convert("RGBA")
    d = ImageDraw.Draw(background)
    plants = database.getItemsIDByBehaviour('420')
    for a, x in enumerate(range(0, np.shape(homelayout)[0])):
        truey = 0
        for b, y in enumerate(range(0, -np.shape(homelayout)[1], -1)):
            shadowbackgroundPaste = ImageOps.fit(Image.new("RGBA",(1,1)), tsize, bleed = 0.0, centering =(0.5, 0.5))
            ix = (x*196/2) + (y*196/2)
            iy = (y*99/2) - (x*99/2)
            offsettext = objectw - 7 + int(ix)-126+int(extrawidth/2), objecth - int(iy) - 70+int(extraheight/2)
            if homelayout[x,truey]  >= 0:
                if homelayout[x,truey] in plants:
                    if datetime.datetime.now() < database.getHarvestTimer(gebruiker)[x,truey]:
                        object = Image.open("images/homes/items/"+str(homelayout[x,truey])+"_"+str(database.getHomeRotation(gebruiker, x, truey))+"_0.png")
                    else:
                        object = Image.open("images/homes/items/"+str(homelayout[x,truey])+"_"+str(database.getHomeRotation(gebruiker, x, truey))+".png")
                else:
                    object = Image.open("images/homes/items/"+str(homelayout[x,truey])+"_"+str(database.getHomeRotation(gebruiker, x, truey))+".png")
                object_w, object_h = object.size
                offset = int(objectw-object_w - 7 + int(ix) +int(extrawidth/2)), -object_h + objecth - int(iy)+int(extraheight/2)
                shadow = Image.open("images/homes/shadows/shadow.png")
                shadow_w, shadow_h = shadow.size
                shadow_offset = int(objectw-shadow_w - 7 + int(ix) +int(extrawidth/2)), -shadow_h + objecth - int(iy)+int(extraheight/2)
                shadowbackgroundPaste.paste(shadow, shadow_offset, shadow)
                backgroundpasted = Image.alpha_composite(background, shadowbackgroundPaste)
                background = Image.blend(backgroundpasted,background,0.6)
                #background.paste(sbackground)
                background.paste(object, offset, object)
                if str(database.getItemName(homelayout[x,truey])).endswith('+'):
                    object = Image.open("images/homes/items/plusbig.png")
                    offset = int(objectw-object_w - 7 + int(ix) +int(extrawidth/2))+32, -object_h + objecth - int(iy)+int(extraheight/2)
                    background.paste(object, offset, object)
                if str(database.getItemName(homelayout[x,truey])).endswith('++'):
                    object = Image.open("images/homes/items/plusbig.png")
                    offset = int(
                        objectw - object_w - 7 + int(ix) + int(extrawidth / 2)) + 32, -object_h + objecth - int(
                        iy) + int(extraheight / 2)+42
                    background.paste(object, offset, object)
            truey = truey + 1
    width, height = background.size
    background = background.resize((int(width/2),int(height/2))) 
    #background.save("images/renders/phones/crib/"+str(gebruiker)+".png", "PNG")

    return background

async def drawHomeIcon(gebruiker: hikari.User):
    background = Image.new("RGBA",(1,1))

    extrawidth = 80
    extraheight = 80
    flooroffsetw = 408
    flooroffseth = 424
    walloffsetw = 408
    walloffseth = 225
    objectw, objecth = 306+ 49, 345+50
    im = Image.open("images/homes/types/starter.png")
    mask = Image.open('images/homes/masks/startermaskfloor.png').convert('L')
    maskwall = Image.open('images/homes/masks/startermask.png').convert('L')

    homelayout = database.getHomeLayout(gebruiker)[:2,:2]
    home = database.getHome(gebruiker)


    size = list(im.size)
    size[0] = int(extrawidth) + size[0]
    size[1] = int(extraheight) + size[1]
    tsize = tuple(size)
    imwidth, imheight = im.size
    

    home = database.getHome(gebruiker)

    
    if home.get("vloer", -1) != -1:
        floorid = database.getHome(gebruiker)['vloer']
        
        wall = Image.open(f"images/homes/floors/{floorid}_1.png")
        croppedfloor = wall.crop((flooroffsetw, flooroffseth, imwidth+flooroffsetw, imheight+flooroffseth))
        im = Image.composite(im, croppedfloor, mask)
        

    if home.get("behang", -1) != -1:
        wallid = database.getHome(gebruiker)['behang']
        wall = Image.open(f"images/homes/walls/{wallid}_1.png")
        croppedwall = wall.crop((walloffsetw, walloffseth, imwidth+walloffsetw, imheight+walloffseth))
        im = Image.composite(im, croppedwall, maskwall)
    background = ImageOps.fit(background, tsize, bleed = 0.0, centering =(0.5, 0.5))
    background.paste(im, (int(extrawidth / 2), int(extraheight / 2)), im)

    background = background.convert("RGBA")
    d = ImageDraw.Draw(background)
    for a, x in enumerate(range(0, np.shape(homelayout)[0])):
        truey = 0
        for b, y in enumerate(range(0, -np.shape(homelayout)[1], -1)):
            shadowbackgroundPaste = ImageOps.fit(Image.new("RGBA",(1,1)), tsize, bleed = 0.0, centering =(0.5, 0.5))
            ix = (x*196/4) + (y*196/4)
            iy = (y*99/4) - (x*99/4)
            offsettext = objectw - 7 + int(ix)-126+int(extrawidth/2), objecth - int(iy) - 70+int(extraheight/2)
            if homelayout[x,truey]  >= 0:
                if homelayout[x,truey] in database.getItemsIDByBehaviour('420'):
                    if datetime.datetime.now() < database.getHarvestTimer(gebruiker)[x,truey]:
                        object = Image.open("images/homes/items/"+str(homelayout[x,truey])+"_"+str(database.getHomeRotation(gebruiker, x, truey))+"_0.png")
                    else:
                        object = Image.open("images/homes/items/"+str(homelayout[x,truey])+"_"+str(database.getHomeRotation(gebruiker, x, truey))+".png")
                else:
                    object = Image.open("images/homes/items/"+str(homelayout[x,truey])+"_"+str(database.getHomeRotation(gebruiker, x, truey))+".png")
                object_w, object_h = object.size
                object = object.resize((int(object_w/2),int(object_h/2)))
                offset = int(objectw-object_w - 7 + int(ix) +int(extrawidth/2)), -object_h + objecth - int(iy)+int(extraheight/2)
                shadow = Image.open("images/homes/shadows/shadow.png")
                shadow_w, shadow_h = shadow.size
                shadow = shadow.resize((int(shadow_w/2),int(shadow_h/2)))
                shadow_offset = int(objectw-shadow_w - 7 + int(ix) +int(extrawidth/2)), -shadow_h + objecth -50- int(iy)+int(extraheight/2)
                shadowbackgroundPaste.paste(shadow, shadow_offset, shadow)
                backgroundpasted = Image.alpha_composite(background, shadowbackgroundPaste)
                background = Image.blend(backgroundpasted,background,0.6)

                background.paste(object.convert('RGB'), offset, object.convert('RGBA'))
            truey = truey + 1
    
    width, height = background.size
    #background = background.resize((int(width/2),int(height/2))) 
    ww = 142
    hh = 186
    background = background.crop((ww,hh,ww+200,hh+200))
    iconmask = Image.open("images/phone_files/cribIconMask.png").convert('L')
    iconmaskinvert = ImageOps.invert(iconmask)
    background.paste(iconmaskinvert,(0,0),iconmask)

    icon = Image.new("RGBA", (200,200),(0,0,0,0))
    iconborder = Image.open("images/phone_files/cribborder.png")

    icon.paste(background,(0,0),iconmaskinvert)
    icon.paste(iconborder,(0,0),iconborder)

    icon.save("images/renders/phones/menu/"+str(gebruiker)+"crib.png", "PNG")

    return "images/renders/phones/menu/"+str(gebruiker)+"crib.png"

async def GetPhonePlacing(user :hikari.User):
    overlayImg = Image.open(await PhoneOverlay(user))
    backgroundImg = await background(user)

    phoneImg = Image.new("RGBA", (600,600))
    path = "images/renders/phones/crib/place"+str(user)+".png"
    menuImg = await menuText("place item")
    phoneImg.paste(backgroundImg,(15,97),backgroundImg.convert('RGBA'))
    phoneImg.paste(menuImg,(15,75),menuImg.convert('RGBA'))
    phoneImg.paste(overlayImg,(0,0),overlayImg.convert('RGBA'))

    items = database.getItemPlaceable(user)
    print(items)
    if len(items) >= 1:
        img1 = Image.open("images/homes/items/"+str(items[0])+"_0.png")
        phoneImg.paste(img1,(15,97),img1.convert('RGBA'))
    if len(items) >= 2:
        img2 = Image.open("images/homes/items/"+str(items[1])+"_0.png")
        phoneImg.paste(img2,(203,97),img2.convert('RGBA'))
    if len(items) >= 3:
        img3 = Image.open("images/homes/items/"+str(items[2])+"_0.png")
        phoneImg.paste(img3,(391,97),img3.convert('RGBA'))
    if len(items) >= 4:
        img4 = Image.open("images/homes/items/"+str(items[3])+"_0.png")
        phoneImg.paste(img4,(15,320),img4.convert('RGBA'))
    if len(items) >= 5:
        img5 = Image.open("images/homes/items/"+str(items[4])+"_0.png")
        phoneImg.paste(img5,(203,320),img5.convert('RGBA'))
    if len(items) >= 6:
        img6 = Image.open("images/homes/items/"+str(items[5])+"_0.png")
        phoneImg.paste(img6,(391,320),img6.convert('RGBA'))
    phoneImg.save(path)
    return path

async def GetPhoneUpgrading(user, upgradefrom, upgradeto, multiplier):
    coins = database.getObject(user, 'money')
    krediet = database.getObject(user, 'credits')
    font1 = ImageFont.truetype("fonts/VT323-Regular.ttf", 27)
    font2 = ImageFont.truetype("fonts/VT323-Regular.ttf", 34)
    font3 = ImageFont.truetype("fonts/VT323-Regular.ttf", 22)
    overlayImg = Image.open(await PhoneOverlay(user))
    backgroundImg = await background(user)
    UpgradeImg = Image.open("images/phone_files/upgradeoverlay.png")
    UpgradeBackgroundImg = Image.open("images/phone_files/upgradeoverlaybackgrounddark.png")
    
    phoneImg = Image.new("RGBA", (600,600))
    path = "images/renders/phones/crib/upgr"+str(user)+".png"
    menuImg = await menuText("Upgrade Item")
    phoneImg.paste(backgroundImg,(15,97),backgroundImg.convert('RGBA'))
    phoneImg.paste(UpgradeBackgroundImg,(15,97),UpgradeBackgroundImg.convert('RGBA'))
    phoneImg.paste(menuImg,(15,75),menuImg.convert('RGBA'))
    phoneImg.paste(overlayImg,(0,0),overlayImg.convert('RGBA'))
    
    w, h = backgroundImg.size
    
    
    items = database.getItemPlaceable(user)
    

    img2 = Image.open("images/homes/items/"+str(upgradeto)+"_0.png")
    W, H = img2.size
    white = Image.new("RGBA",(W,H),(255,255,255))
    phoneImg.paste(white,(w-W+30+2,80+h-H+2),img2.convert('RGBA'))
    phoneImg.paste(white,(w-W+30+2,80+h-H-2),img2.convert('RGBA'))
    phoneImg.paste(white,(w-W+30+2,80+h-H),img2.convert('RGBA'))
    phoneImg.paste(white,(w-W+30-2,80+h-H),img2.convert('RGBA'))
    phoneImg.paste(white,(w-W+30-2,80+h-H+2),img2.convert('RGBA'))
    phoneImg.paste(white,(w-W+30-2,80+h-H-2),img2.convert('RGBA'))
    phoneImg.paste(white,(w-W+30,80+h-H+2),img2.convert('RGBA'))
    phoneImg.paste(white,(w-W+30,80+h-H-2),img2.convert('RGBA'))



    phoneImg.paste(img2,(w-W+30,80+h-H),img2.convert('RGBA'))
    
    
    
    phoneImg.paste(UpgradeImg,(15,67),UpgradeImg.convert('RGBA'))
    img1 = Image.open("images/homes/items/"+str(upgradefrom)+"_3.png")
    W, H = img1.size
    phoneImg.paste(img1,(-15,80+h-H),img1.convert('RGBA'))

    draw = ImageDraw.Draw(phoneImg)
    W, H = phoneImg.size[0], phoneImg.size[1]


    
    w, h = draw.textbbox((0, 0), "YOU HAVE", font=font3, stroke_width=3)[2:4]
    draw.text(((W/2)-(w/2),434-h),"YOU HAVE", font=font3, stroke_width=3, stroke_fill='white',fill='black')
    

    item1 = database.getItemDetailedDB(upgradefrom)
    item1 = list(item1)
    if "{reward}" in item1[2]:
        item1[2] = item1[2].replace("{reward}", str(database.getItemDB(upgradefrom, 'reward')))

    if "{money}" in item1[2]:
        item1[2] = item1[2].replace("{money}", database.money)

    item2 = database.getItemDetailedDB(upgradeto)
    item2 = list(item2)
    if "{reward}" in item2[2]:
        item2[2] = item2[2].replace("{reward}", str(database.getItemDB(upgradeto, 'reward')))

    if "{money}" in item2[2]:
        item2[2] = item2[2].replace("{money}", database.money)
    

    w, h = draw.textbbox((0, 0), str(coins), font=font1, stroke_width=3)[2:4]
    Pilmoji(phoneImg).text(((W/2)-w-85,434-h),str(coins)+" "+database.money, font=font1, stroke_width=3, stroke_fill='white',fill='black', emoji_position_offset=(0, -5))
    w, h = draw.textbbox((0, 0), str(krediet), font=font1, stroke_width=3)[2:4]
    Pilmoji(phoneImg).text(((W/2)+54,434-h),database.credit+" "+str(krediet), font=font1, stroke_width=3, stroke_fill='white',fill='black', emoji_position_offset=(0, -3))

    description1= textwrap.fill(text=item1[2], width= 20)
    description2= textwrap.fill(text=item2[2], width= 20)
    
    w, h = draw.textbbox((0, 0), description1, font=font1, stroke_width=3)[2:4]
    Pilmoji(phoneImg).text((35,200),description1, font=font1, stroke_width=3, stroke_fill='white',fill='black', emoji_position_offset=(0, -4))
    
    w, h = draw.textbbox((0, 0), description2, font=font1, stroke_width=3)[2:4]
    Pilmoji(phoneImg).text((560-w,200),description2, font=font1, stroke_width=3, stroke_fill='white',fill='black',align="right", emoji_position_offset=(0, -4))

    
    w, h = draw.textbbox((0, 0), "YOU NEED", font=font3, stroke_width=3)[2:4]
    draw.text(((W/2)-(w/2),510-h),"YOU NEED", font=font3, stroke_width=3, stroke_fill='white',fill='black')

    w, h = draw.textbbox((0, 0), str(item2[3]), font=font1, stroke_width=3)[2:4]
    Pilmoji(phoneImg).text(((W/2)+54,512-h),database.credit+" "+str(item2[4]), font=font1, stroke_width=3, stroke_fill='white',fill='black', emoji_position_offset=(0, -3))
    w, h = draw.textbbox((0, 0), str(item2[4]), font=font1, stroke_width=3)[2:4]
    w, h = draw.textbbox((0, 0), str(item2[4]), font=font1, stroke_width=3)[2:4]
    Pilmoji(phoneImg).text(((W/2)-w-85,512-h),str(item2[3])+" "+database.money, font=font1, stroke_width=3, stroke_fill='white',fill='black', emoji_position_offset=(0, -5))

    w, h = draw.textbbox((0, 0), item1[1].title(), font=font2, stroke_width=3)[2:4]
    draw.text((25,155),item1[1].title(), font=font2, stroke_width=3, stroke_fill='white',fill='black')

    w, h = draw.textbbox((0, 0), item2[1].title(), font=font2, stroke_width=3)[2:4]
    draw.text((580-w,155),item2[1].title(), font=font2, stroke_width=3, stroke_fill='white',fill='black')

    phoneImg.save(path)
    return path

async def GetPhoneHome(user : hikari.User):
    overlayImg = Image.open(await PhoneOverlay(user))
    backgroundImg = await background(user)

    phoneImg = Image.new("RGBA", (600,600))
    path = "images/renders/phones/crib/"+str(user)+".png"
    
    statusbarImg = await menuText("Your Crib")
    phoneImg.paste(backgroundImg,(15,97),backgroundImg.convert('RGBA'))
    phoneImg.paste(overlayImg,(0,0),overlayImg.convert('RGBA'))
    phoneImg.paste(statusbarImg,(15,75),statusbarImg.convert('RGBA'))
    crib = await drawHome(user)
    W,H = phoneImg.size
    w,h = crib.size

    phoneImg.paste(crib,(int((W/2)-(w/2)),int((H/2)-(h/2))),crib.convert('RGBA'))

    phoneImg.save(path)
    return path

async def getQuests(user : hikari.User):
    """Renders the quest interface with daily rewards in top 1/4 and quests below"""
    overlayImg = Image.open(await PhoneOverlay(user))
    backgroundImg = await background(user)
    phoneImg = Image.new("RGBA", (600,600))
    menuImg = await menuText("quests")
    
    # Create background for daily rewards section - reduced height
    daily_section = Image.new("RGBA", (570, 150), (30, 30, 30))
    
    # Draw daily rewards
    draw = ImageDraw.Draw(daily_section)
    font = ImageFont.truetype("fonts/VT323-Regular.ttf", 24)
    small_font = ImageFont.truetype("fonts/VT323-Regular.ttf", 18)

    # Draw header
    w = draw.textbbox((0, 0), "DAILY REWARDS", font=font)[2]
    draw.text((285-(w/2), 5), "DAILY REWARDS", font=font, fill=(255,255,255))

    # Get user's daily streak info
    daily_counter = database.getStat(user, 'dailycounter')
    last_daily = database.getStat(user, 'lastdaily')
    can_claim = last_daily <= (datetime.datetime.now() - datetime.timedelta(days=1))

    # Calculate time until next daily reset
    next_daily = last_daily + datetime.timedelta(days=1)
    time_until_daily = next_daily - datetime.datetime.now()
    if time_until_daily.total_seconds() > 0:
        time_str = str(time_until_daily)[:-7]  # Remove microseconds
        w = draw.textbbox((0, 0), f"Next daily in: {time_str}", font=small_font)[2]
        draw.text((285-(w/2), 130), f"Next daily in: {time_str}", font=small_font, fill=(255,255,255))

    # Define rewards for each day
    rewards = {
        0: (10, 10),
        1: (20, 15),
        2: (50, 20),
        3: (100, 25),
        4: (200, 30)
    }

    # Draw square reward boxes - increased width
    box_size = 90
    box_spacing = 10  # Reduced spacing to fit wider boxes
    total_width = (box_size * 5) + (box_spacing * 4)
    start_x = (570 - total_width) // 2
    
    for day in range(5):
        x = start_x + (box_size + box_spacing) * day
        money, credits = rewards[day]
        
        if day < daily_counter:
            box_color = (50, 100, 50)  # Claimed
        elif day == daily_counter and can_claim:
            box_color = (100, 100, 50)  # Available  
        else:
            box_color = (50, 50, 50)  # Locked

        draw.rectangle([(x, 30), (x + box_size, 35 + box_size)], 
                      fill=box_color, outline=(255,255,255))
        
        # Adjusted text positioning
        w = draw.textbbox((0, 0), f"DAY {day+1}", font=small_font)[2]
        draw.text((x + (box_size/2)-(w/2), 35), f"DAY {day+1}", 
                  font=small_font, fill=(255,255,255))
        
        w = draw.textbbox((0, 0), f"{money}", font=small_font)[2]
        Pilmoji(daily_section).text((x + (box_size/2)-(w/2), 62), 
                                  f"{money} {database.money}", 
                                  font=small_font, fill=(255,255,255))
        
        w = draw.textbbox((0, 0), f"{credits}", font=small_font)[2]
        Pilmoji(daily_section).text((x + (box_size/2)-(w/2), 82),
                                  f"{credits} {database.credit}",
                                  font=small_font, fill=(255,255,255))

    # Create quests section with darker background and 5px lower position
    quests_section = Image.new("RGBA", (570, 325), (20, 20, 20))  # Darker background, +5 height
    quest_draw = ImageDraw.Draw(quests_section)

    # Draw semi-transparent dark overlay 5px lower
    dark_overlay = Image.new("RGBA", (570, 325), (0, 0, 0, 100))
    quests_section = Image.alpha_composite(quests_section, dark_overlay) 
    quest_draw = ImageDraw.Draw(quests_section)

    # Sample quests data with combined description and progress
    daily_quests = [
        {"name": "Daily Quest 1", "desc": "Complete 10 fishing trips (0/10)", "reward": f"100 {database.credit}"},
        {"name": "Daily Quest 2", "desc": "Rob 20 players (5/20)", "reward": f"200 {database.credit}"},
        {"name": "Daily Quest 3", "desc": "Win 5 fights (1/5)", "reward": f"300 {database.credit}"}
    ]

    weekly_quests = [
        {"name": "Weekly Quest 1", "desc": "Earn 50,000 coins (2/50)", "reward": f"1000 {database.credit}"},
        {"name": "Weekly Quest 2", "desc": "Upgrade 3 items (0/3)", "reward": f"500 {database.credit}"},
        {"name": "Weekly Quest 3", "desc": "Complete 10 daily quests (4/10)", "reward": f"750 {database.credit}"}
    ]

    # Draw side-by-side quest sections
    section_width = 275

    # Daily quests header
    quest_draw.text((20, 10), "DAILY QUESTS", font=font, fill=(255,255,255))
    quest_draw.text((20, 35), "Resets in: 12:34:56", font=small_font, fill=(200,200,200))
    
    # Weekly quests header 
    quest_draw.text((section_width + 20, 10), "WEEKLY QUESTS", font=font, fill=(255,255,255))
    quest_draw.text((section_width + 20, 35), "Resets in: 5d 12:34:56", font=small_font, fill=(200,200,200))

    # Draw daily quests with combined description and progress
    y = 55  # Start slightly higher
    box_height = 65  # Increased box height
    for quest in daily_quests:
        quest_draw.rectangle([(10, y), (section_width-10, y+box_height)], fill=(40,40,40), outline=(255,255,255))
        quest_draw.text((20, y+10), quest["name"], font=font, fill=(255,255,255))
        quest_draw.text((20, y+38), quest["desc"], font=small_font, fill=(200,200,200))  # Moved description down
        # Right-aligned reward
        w = quest_draw.textbbox((0, 0), quest["reward"], font=font)[2]
        Pilmoji(quests_section).text((section_width-30-w, y+10), quest["reward"], font=font, fill=(255,255,255))
        y += box_height + 5  # Added small gap between boxes

    # Draw weekly quests with combined description and progress
    y = 55  # Start at same height as daily quests
    for quest in weekly_quests:
        quest_draw.rectangle([(section_width+10, y), (560, y+box_height)], fill=(40,40,40), outline=(255,255,255))
        quest_draw.text((section_width+20, y+10), quest["name"], font=font, fill=(255,255,255))
        quest_draw.text((section_width+20, y+38), quest["desc"], font=small_font, fill=(200,200,200))  # Moved description down
        # Right-aligned reward
        w = quest_draw.textbbox((0, 0), quest["reward"], font=font)[2]
        Pilmoji(quests_section).text((540-w, y+10), quest["reward"], font=font, fill=(255,255,255))
        y += box_height + 5  # Added small gap between boxes

    # Add diagonal WIP text overlay with shadow for better visibility
    wip_font = ImageFont.truetype("fonts/VT323-Regular.ttf", 120)
    
    # Calculate text size for rotation first
    w = quest_draw.textbbox((0, 0), "WIP", font=wip_font)[2]
    h = quest_draw.textbbox((0, 0), "WIP", font=wip_font)[3]
    
    # Draw shadow text using calculated dimensions
    txt = Image.new('RGBA', (w+20, h+20), (0,0,0,0))
    d = ImageDraw.Draw(txt)
    d.text((12, 12), "WIP", font=wip_font, fill=(0,0,0,150))  # Shadow
    d.text((10, 10), "WIP", font=wip_font, fill=(255,50,50,180))  # Brighter red
    
    # Create temporary image for rotated text
    txt = Image.new('RGBA', (w+20, h+20), (0,0,0,0))
    d = ImageDraw.Draw(txt)
    d.text((10, 10), "WIP", font=wip_font, fill=(200,30,30,128))
    
    # Rotate and position the text
    txt = txt.rotate(-30, expand=1)
    tx = (570 - txt.size[0])//2
    ty = (320 - txt.size[1])//2
    quests_section.paste(txt, (tx, ty), txt)

    # Assemble final image with adjusted positioning
    phoneImg.paste(backgroundImg, (15,97), backgroundImg.convert('RGBA'))
    phoneImg.paste(menuImg, (15,75), menuImg.convert('RGBA'))
    phoneImg.paste(daily_section, (15,97), daily_section.convert('RGBA'))
    phoneImg.paste(quests_section, (15,247), quests_section.convert('RGBA'))  # Moved down 10px from 237 to 247

    phoneImg.paste(overlayImg, (0,0), overlayImg.convert('RGBA'))

    path = f"images/renders/phones/menu/quests{user}.png"
    phoneImg.save(path)
    return path

async def menuIcon(icon : str, user: int):
    iconImg = Image.new("RGBA", (110,130), (0,255,0,0))
    if icon == "Your Crib":
        iconPng = Image.open(await drawHomeIcon(user))
        iconPng = iconPng.resize((100,100))
    else:
        try:
            iconPng = Image.open("images/phone_files/icon"+icon.replace(" ", "")+".png")
        except:
            iconPng = Image.new("RGBA", (100,100), (255,255,255,255))

    iconImg.paste(iconPng,(5,5),iconPng.convert('RGBA'))
    font = ImageFont.truetype("fonts/VT323-Regular.ttf", 27)
    draw = ImageDraw.Draw(iconImg)

    

    W, H = iconImg.size[0], iconPng.size[1]
    w, h = draw.textbbox((0, 0), icon.upper(), font=font, stroke_width=3)[2:]
    notificationPng = Image.open("images/phone_files/notification.png")
    
    
    draw.text(((W/2)+4-(w/2),H),icon.upper(), font=font, stroke_width=3, stroke_fill='white',fill='black')
    if icon == "Your Crib" and (database.getStat(user, "harvest") == 1 and database.getHarvestTimer(user).min() <= datetime.datetime.now()):
        iconImg.paste(notificationPng, (0,0), notificationPng.convert("RGBA"))

    if icon == 'Quests' and (database.getStat(user, 'lastdaily') <= (datetime.datetime.now() - datetime.timedelta(days = 1))):
        iconImg.paste(notificationPng, (0,0), notificationPng.convert("RGBA"))
    return iconImg