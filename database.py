import asyncio
import random
import psycopg2
import numpy as np
import config
import logging
import datetime
logger = logging.getLogger(__name__)

import hikari
from PIL import Image, ImageDraw, ImageFont, ImageOps

import logging
logger = logging.getLogger(__name__)

money = "💵"
credit = "💳"

fishingchannels = {}
fishingchannelstimes = {}


#load the config with the database info
loaded_config = config.KingConfig.load()


#connect to the database
try:
    conn = psycopg2.connect(dbname=loaded_config.database_name, user=loaded_config.database_user, password=loaded_config.database_password, host=loaded_config.database_ip, port=loaded_config.database_port, sslmode=loaded_config.database_ssl)
    logger.info("Database connection established at " + loaded_config.database_ip + ":" + str(loaded_config.database_port))	
except (Exception) as err:
    logger.info(err)
    conn = None
    cur = None

#Pre setup to add customization per server
def price(hoeveelheid:int,valuta):
    if valuta == "credit":
        valuta = credit
    elif valuta == "money":
        valuta = money

    return f"`{hoeveelheid} {valuta}`"

def checkIfUserExists(user):
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT * FROM discord_stats WHERE user_id = {user}")
        if cur.fetchone() is not None:
            result = True
        else:
            result = False
    except:
        conn.rollback()
        cur.execute(f"SELECT * FROM discord_stats WHERE user_id = {user}")
        if cur.fetchone() is not None:
            result = True
        else:
            result = False
    
    finally:
        cur.close()
    return result

def initiation(user):
    cur = conn.cursor()
    try:
        cur.execute(f"""INSERT INTO discord_stats (user_id)
            VALUES ({user}) 
            ON CONFLICT (user_id) do nothing""")
        conn.commit()
    except Exception as error:
        print(error)
        conn.rollback()
        cur.execute(f"""INSERT INTO discord_stats (user_id)
            VALUES ({user}) 
            ON CONFLICT (user_id) do nothing""")
        conn.commit()
    finally:
        cur.close()

    cur = conn.cursor()
    try:
        cur.execute(f"""INSERT INTO discord_home (user_id,type,background,backgroundurl,layout,rotation,walls,floor)
            VALUES ({user}, 'starter', {False}, 'https://afbeelding.jpg', '-1 -1 -1 -1', '0 0 0 0', -1, -1) 
            ON CONFLICT (user_id) do nothing""")
        conn.commit()
    except:
        conn.rollback()
        cur.execute(f"""INSERT INTO discord_home (user_id,type,background,backgroundurl,layout,rotation,walls,floor)
            VALUES ({user}, 'starter', {False}, 'https://afbeelding.jpg', '-1 -1 -1 -1', '0 0 0 0', -1, -1)  
            ON CONFLICT (user_id) do nothing""")
        conn.commit()
    finally:
        cur.close()

    cur = conn.cursor()
    try:
        cur.execute(f"""INSERT INTO discord_userinventory (user_id,item_id,amount)
            VALUES ({user}, '-100', '50') 
            ON CONFLICT (user_id, item_id) do nothing""")
        conn.commit()
    except:
        conn.rollback()
        cur.execute(f"""INSERT INTO discord_userinventory (user_id,item_id,amount)
            VALUES ({user}, '-100', '50') 
            ON CONFLICT (user_id, item_id) do nothing""")
        conn.commit()
    finally:
        cur.close()

def getHarvestTimer(user):
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT harvesttimer FROM discord_home WHERE user_id = {user}")
        result = cur.fetchall()[0][0]
    except:
        conn.rollback()
        cur.execute(f"SELECT harvesttimer FROM discord_home WHERE user_id = {user}")
        result = cur.fetchall()[0][0]
    finally:
        cur.close()
    
    if getHome(user)['huistype'] == "starter":
        r = np.asmatrix(np.array(result).reshape(2,2))
        return r
    if getHome(user)['huistype'] == "starterx":
        r = np.asmatrix(np.array(result).reshape(2,3))
        return r
    if getHome(user)['huistype'] == "startery":
        r = np.asmatrix(np.array(result).reshape(3,2))
        return r
    if getHome(user)['huistype'] == "starter+":
        r = np.asmatrix(np.array(result).reshape(3,3))
        return r
    if getHome(user)['huistype'] == "starter+y":
        r = np.asmatrix(np.array(result).reshape(4,2))
        return r
    if getHome(user)['huistype'] == "starter+x":
        r = np.asmatrix(np.array(result).reshape(2,4))
        return r
    if getHome(user)['huistype'] == "deluxeplusplus":
        r = np.asmatrix(np.array(result).reshape(6,6))
        return r

def isHarvestable(member):
    timers = getHarvestTimer(member)
    for x in range(0, len(timers)):
        for y in range(0, timers.shape[1]):
            print(timers[x, y])
            if timers[x, y] < datetime.datetime.now() and getStat(member, "harvest") == 1:
                return True   
    return False
    

#function to calculate if fish bites
async def hasFishBitten(member, channel):
    totalmembers = 0
    for x, i in enumerate(fishingchannels[channel]):
        for y, b in enumerate(i):
            if fishingchannels[channel][x][y] == member:
                timestarted = fishingchannelstimes[channel][x][y]
            if fishingchannels[channel][x][y] != 0:
                totalmembers += 1
    seed = int((datetime.datetime.now() - timestarted).total_seconds() / 10) # Seed changes every 15 seconds
    random.seed(seed + member)
    chance = 1/6  # Base chance (once per minute)
    if totalmembers > 0:
        bonus = totalmembers / 120  # Up to +0.16+ chance with 20 members (20/120)
        chance += bonus
    if (datetime.datetime.now() - timestarted).total_seconds() < 15:
        return False
    else:
        return random.random() < chance

async def isFishing(member, channel):
    if channel in fishingchannels:
        for x, i in enumerate(fishingchannels[channel]):
            for y, e in enumerate(i):
                if e == member:
                    return True
    return False
#rewrite this
def getObject(user, data = None):
    cur = conn.cursor()
    items = {}
    try:
        cur.execute(f"SELECT * FROM discord_userinventory WHERE user_id = {user} ORDER BY item_id ASC")
        aaa = cur.fetchall()
    except:
        conn.rollback()
        cur.execute(f"SELECT * FROM discord_userinventory WHERE user_id = {user} ORDER BY item_id ASC")
        aaa = cur.fetchall()
    finally:
        cur.close()
    for i in aaa:
        if i[1] != -102: 
            items[i[1]] = int(i[2])
        else:
            items[i[1]] = i[2]
    if data == "crypto" or data == -102:
        try:
            return float(items[-102])
        except:
            return 0
    if data == "money":
        return int(items[int(-100)])
    if data == "credits":
        return int(items[int(-200)])
    
    if data == "storedmoney":
        try:
            return int(items[-101])
        except:
            return 0
    if data is None:
        if items is not None:
            return items
        else:
            return 0
    try:
        return items[int(data)]
    except:
        return 0

def getLocale(user):
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT language FROM dashboard_discordguild WHERE id = {user.guild.id}")
        results = cur.fetchone()
    except:
        conn.rollback()
        cur.execute(f"SELECT language FROM dashboard_discordguild WHERE id = {user.guild.id}")
        results = cur.fetchone()
    finally:
        cur.close()
    try:
        results = int(results[0])
    except:
        return "en_US"
    if results == 0:
        return "en_US"
    if results == 1:
        return "nl_NL"
    return results
    
#rewrite this
def isObjectLimit(user, data = None):
    data = int(data)
    if data == -100:
        return 99999999
    if data >= 10000:
        return 1
    return 64


def getObjectAll(data, hoeveelheid : int = 0):
    cur = conn.cursor()
    datadict = {}
    if data == "money":
        data = -100
    if data == "credits":
        data = -200
    if data == "storedmoney":
        data = -101
    cur.execute(f"SELECT user_id, amount FROM discord_userinventory WHERE item_id = '{data}'")
    for i in cur.fetchall():
            datadict[i[0]] = int(i[1])
    if hoeveelheid == 0:
        datadict = dict(sorted(datadict.items(), key=lambda x: x[1], reverse=True))
    else:
        datadict = dict(sorted(datadict.items(), key=lambda x: x[1], reverse=True)[:int(hoeveelheid)]) 
    cur.close()
    return datadict

def getStat(user, data):
    cur = conn.cursor()
    cur.execute(f"SELECT {data} FROM discord_stats WHERE user_id = '{user}'")
    statDB = cur.fetchall()[0]
    cur.close()
    return statDB[0]

#rework this
def getStatAll(data, hoeveelheid : int = 0):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM discord_stats")
    statDB = {}
    datadict = {}
    for i in cur.fetchall():
        statDB[i[0]] = {}
        statDB[i[0]]['rob'] = i[1]
        statDB[i[0]]['laatsteprank'] =i[2]
        statDB[i[0]]['saus'] = i[3]
        statDB[i[0]]['allesaus'] =i[4]
        statDB[i[0]]['laatsteoogst']= i[5]
        if i[6]:
            statDB[i[0]]['oogst']= 1
        else:
            statDB[i[0]]['oogst']= 0
        statDB[i[0]]['laatstebedel']= i[7]
        statDB[i[0]]['laatstesaus']= i[8]
        datadict[i[0]] = statDB[i[0]][data]
    if hoeveelheid == 0:
        datadict = dict(sorted(datadict.items(), key=lambda x: x[1], reverse=True))
    else:
        datadict = dict(sorted(datadict.items(), key=lambda x: x[1], reverse=True)[:int(hoeveelheid)])
    cur.close()
    return dict(datadict)


#rework this
def setStat(user: hikari.User, data, waarde):
    query =  f"""
            INSERT INTO discord_stats (user_id,"{data}")
            VALUES (%s, %s) 
            ON CONFLICT (user_id)
            DO UPDATE SET user_id = %s, "{data}" = %s
            """
    query2 = f"""
            INSERT INTO discord_stats_history (user_id,operation,new_val)
            VALUES (%s, '{data}', %s) 
            """
    dataa = (user, waarde,user, waarde)
    cur = conn.cursor()
    try:
        cur.execute(query, dataa)
        cur.execute(query2, dataa[:2])
    except:
        query2 = f"""
                    INSERT INTO discord_stats_history (user_id,operation,new_val)
                    VALUES (%s, '{data}', '%s') 
                    """
        cur.execute(query2, dataa[:2])
    conn.commit()
    cur.close()
#rewrite this
def addObject(user, data, hoeveelheid : int):
    if hoeveelheid <=0:
        return
    if data == 'storedmoney':
        data = -101
    if data == 'money':
        data = -100
    if data == 'credits':
        data = -200
    try:
        int(data)
    except:
        data = getItemID(data)

    limit = isObjectLimit(user,data) 
    item = getObject(user, data)
    if item+hoeveelheid > limit:
        pass
    else:
        query=f"""
                INSERT INTO discord_userinventory (user_id, item_id, amount) 
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id,item_id) 
                DO UPDATE SET amount = discord_userinventory.amount + {hoeveelheid};
        """
        dataa = (user,data, hoeveelheid)
        cur = conn.cursor()
        print(dataa)
        cur.execute(query, dataa)

        query2 = f"""
                    INSERT INTO discord_userinventory_history (user_id,operation, id, new_val)
                    VALUES (%s, 'ADD', %s, %s) 
                    """
        cur.execute(query2, dataa)


        conn.commit()
        cur.close()

#delete function
def addCredits(user, hoeveelheid : int):
        query =  f"""
                UPDATE discord_stats 
                SET credits = credits + {hoeveelheid}
                WHERE user_id = '{user}';
                """
        dataa = (user, hoeveelheid)
        cur = conn.cursor()
        cur.execute(query, dataa)

        query2 = f"""
            INSERT INTO discord_stats_history (user_id,operation,new_val)
            VALUES (%s, 'credits', %s) 
            """
        cur.execute(query2, dataa)


        conn.commit()
        cur.close()

#delete function
def removeCredits(user, hoeveelheid : int):
        query =  f"""
                UPDATE discord_stats 
                SET credits = credits - {hoeveelheid}
                WHERE user_id = '{user}';
                """
        dataa = (user, hoeveelheid)
        cur = conn.cursor()
        cur.execute(query, dataa)

        query2 = f"""
            INSERT INTO discord_stats_history (user_id,operation,new_val)
            VALUES (%s, 'credits', %s) 
            """
        cur.execute(query2, dataa)


        conn.commit()
        cur.close()

def removeObject(user: hikari.User, data, hoeveelheid : int):
    if data == 'storedmoney':
        data = -101
    if data == 'money':
        data = -100
    if data == 'credits':
        data = -200
    try:
        int(data)
    except:
        data = getItemID(data)
    query =  f"""
            UPDATE discord_userinventory 
            SET amount = amount - {hoeveelheid}
            WHERE user_id = '{user}' AND item_id = '{data}';
            """
    dataa = (user, hoeveelheid,user, hoeveelheid)
    cur = conn.cursor()
    cur.execute(query, dataa)
    query2 = f"""
                    INSERT INTO discord_userinventory_history (user_id,operation, id, new_val)
                    VALUES (%s, 'REMOVE', {data}, -%s) 
                    """
    cur.execute(query2, dataa[:2])
    conn.commit()
    cur.close()


#rework this
def checkLimit(user: hikari.User, data):
    kluis = 0
    plants = 0
    for x in range(0,len(getHomeLayout(user))):
        for y in range(0,getHomeLayout(user).shape[1]):
            if getHomeLayout(user)[x, y] == 0:
                plants = plants+1
            if getHomeLayout(user)[x, y] == 1:
                plants = plants+1
            if getHomeLayout(user)[x, y] == 2:
                plants = plants+1
            if getHomeLayout(user)[x, y] == 11:
                kluis = kluis+1
            if getHomeLayout(user)[x, y] == 12:
                kluis = kluis+1
            if getHomeLayout(user)[x, y] == 10:
                kluis = kluis+1
    if "wietplant" in data:
        plants = plants+getObject(user, data)
        if plants >= 12:
            return False
        elif plants == 0:
            return True
        return True
    if "kluis" in data:
        kluis = kluis+getObject(user, data)
        if kluis >= 2:
            return False
        elif kluis == 0:
            return True
    return None


async def getPrank(guildid):
    print(guildid)
    cur = conn.cursor()
    cur.execute("""
            SELECT id, attack_list FROM dashboard_discordguild
            """)
    welcomedb = cur.fetchall()
    cur.close()
    for i in welcomedb:
        if guildid == int(i[0]):
            list = i[1]
            try:
                list[0] = list[0][1:]
                list[-1] = list[-1][:-1]
            except:
                return " "
            return random.choice(list)

def getAllItemDB():
    cur = conn.cursor()
    cur.execute("SELECT * FROM discordlogin_itemdb ORDER BY id ASC")
    itemDB = {}
    a = cur.fetchall()
    cur.close()
    for i in a:
        itemDB[i[0]] = {}
        itemDB[i[0]]['name'] = i[1]
        itemDB[i[0]]['description'] = i[2]
        itemDB[i[0]]['price'] =[]
        itemDB[i[0]]['price'].append(i[3])
        itemDB[i[0]]['price'].append(i[4])
        itemDB[i[0]]['emoji'] = i[5]
        itemDB[i[0]]['category']=(i[6])
        itemDB[i[0]]['forsale']=(i[7])
        itemDB[i[0]]['tradeable']= i[8]
        itemDB[i[0]]['limit']= i[9]
        itemDB[i[0]]['behaviour']= i[10]
        itemDB[i[0]]['sellable']= i[11]
        itemDB[i[0]]['sellprice']= i[12]
        itemDB[i[0]]['upgradeable']= i[13]
        itemDB[i[0]]['fishitemtype']= i[21]
    return itemDB

def getAllItemIDWhere(column:str, value):
    cur = conn.cursor()
    if type(value) == int:
        cur.execute(f"SELECT id FROM discordlogin_itemdb WHERE {column} = {value} ORDER BY id ASC")
    else:
        cur.execute(f"SELECT id FROM discordlogin_itemdb WHERE {column} = '{value}' ORDER BY id ASC")
    result = cur.fetchall()
    cur.close()
    return result


def getItemPlaceable(user):
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT * FROM discord_userinventory WHERE user_id = {user} ORDER BY item_id ASC")
        
    except:
        conn.rollback()
        cur.execute(f"SELECT * FROM discord_userinventory WHERE user_id = {user} ORDER BY item_id ASC")

    items = []
    aaa = cur.fetchall()
    cur.close()
    
    for i in aaa:
        if int(i[2]) == 0:
            continue
        items.append(int(i[1]))
    placeable = getAllItemIDWhere("placeable", True)
    placeableitems = []
    for i in items:
        if (i,) in placeable:
            placeableitems.append(int(i))

    return placeableitems
        
    return items

def getItemsIDByBehaviour(behaviour:str):
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM discordlogin_itemdb WHERE behaviour= '{behaviour}' ORDER BY id ASC")
    result = [r[0] for r in cur.fetchall()]
    cur.close()
    return result

def getItemDB(id, property):
    if type(property) == int:
        raise ValueError("Property cannot be 0")
    cur = conn.cursor()
    cur.execute(f"SELECT {property} FROM discordlogin_itemdb WHERE id = '{id}' ORDER BY id ASC")
    prop = cur.fetchall()
    cur.close()
    return prop[0][0]

def getItemDetailedDB(id):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM discordlogin_itemdb WHERE id = {id} ORDER BY id ASC")
    prop = cur.fetchall()
    cur.close()
    return prop[0]

def getItemID(name):
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM discordlogin_itemdb WHERE name = '{name}'")
    try:
        result = cur.fetchall()[0][0]
    except:
        result = None
    cur.close()
    return result

def getItemName(id):
    cur = conn.cursor()
    cur.execute(f"SELECT name FROM discordlogin_itemdb WHERE id = '{id}'")
    try:
        result = str(cur.fetchall()[0][0]).title()
    except:
        result = None
    cur.close()
    return result

def isBuyable(name):
    cur = conn.cursor()
    cur.execute(f"SELECT id,for_sale FROM discordlogin_itemdb WHERE name = '{name}'")
    if cur.fetchall()[0][1] == True:
        result = True
    else:
        result = False
    cur.close()
    return result


def getHome(user : hikari.User):
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT * FROM discord_home WHERE user_id = '{user}'")
    except:
        conn.rollback()
        cur.execute(f"SELECT * FROM discord_home WHERE user_id = '{user}'")
    huisDB = {}
    f = cur.fetchall()
    cur.close()
    
    huisDB['huistype'] = f[0][1]
    if f[0][2] == True:
        huisDB['background'] = 1
    else:
        huisDB['background'] = 0
    huisDB['backgroundurl'] = f[0][3]
    huisDB['layout'] = f[0][4]
    huisDB['rotation'] = f[0][5]
    huisDB['behang']= f[0][6]
    huisDB['vloer']= f[0][7]
    huisDB['harvesttimer']= f[0][8]
    return huisDB

def setHome(user : hikari.User, data : str, waarde):
    query =  f"""
            INSERT INTO discord_home (user_id,"{data}")
            VALUES (%s, %s) 
            ON CONFLICT (user_id)
            DO UPDATE SET user_id = %s, "{data}" = %s
            """
    dataa = (user, waarde,user, waarde)
    cur = conn.cursor()
    cur.execute(query, dataa)
    conn.commit()
    cur.close()

def getReward(id):
    cur = conn.cursor()
    cur.execute(f"SELECT reward FROM discordlogin_itemdb WHERE id = '{id}'")
    try:
        result = cur.fetchall()[0][0]
    except:
        result = None
    cur.close()
    return result

def getIfUpgradeable(id):
    cur = conn.cursor()
    cur.execute(f"SELECT upgradeable, upgradeto, upgradeamount FROM discordlogin_itemdb WHERE id = '{id}'")
    a= cur.fetchall()
    try:
        result = a[0][0], a[0][1], a[0][2]
    except:
        result = None
    cur.close()
    return result

def getHomeLayout(user : hikari.User):
    if getHome(user)['huistype'] == "starter":
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(2,2))))
        return r
    if getHome(user)['huistype'] == "starterx":
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(2,3))))
        return r
    if getHome(user)['huistype'] == "startery":
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(3,2))))
        return r
    if getHome(user)['huistype'] == "starter+":
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(3,3))))
        return r
    if getHome(user)['huistype'] == "starter+y":
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(4,2))))
        return r
    if getHome(user)['huistype'] == "starter+x":
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(2,4))))
        return r
    if getHome(user)['huistype'] == "deluxeplusplus":
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(6,6))))
        return r

def getHomeLayoutStore(user : hikari.User, x=False,y=False):
    if getHome(user)['huistype'] == "starter" and x:
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(2,2))))
        addx = np.array([-1,-1])
        r = np.hstack((r, np.atleast_2d(addx).T))
        return r
    if getHome(user)['huistype'] == "starter" and y:
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(2,2))))
        addx = np.array([-1,-1])
        r = np.vstack ((r, addx))
        return r
    if getHome(user)['huistype'] == "starterx" and x:
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(2,3))))
        addx = np.array([-1,-1])
        r = np.hstack((r, np.atleast_2d(addx).T))
        return r
    if getHome(user)['huistype'] == "starterx" and y:
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(2,3))))
        addx = np.array([-1,-1,-1])
        r = np.vstack ((r, addx))
        return r
    if getHome(user)['huistype'] == "startery" and x:
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(3,2))))
        addx = np.array([-1,-1,-1])
        r = np.hstack((r, np.atleast_2d(addx).T))
        return r
    if getHome(user)['huistype'] == "startery" and y:
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(3,2))))
        addx = np.array([-1,-1])
        r = np.vstack ((r, addx))
        return r

def setHomeLayout(user : hikari.User, positie, objectid:int):
    if getHome(user)['huistype'] == "starter":
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(2,2))))
    if getHome(user)['huistype'] == "starterx":
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(2,3))))
    if getHome(user)['huistype'] == "startery":
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(3,2))))
    if getHome(user)['huistype'] == "starter+":
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(3,3))))
    if getHome(user)['huistype'] == "starter+y":
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(4,2))))
    if getHome(user)['huistype'] == "starter+x":
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(2,4))))
    if getHome(user)['huistype'] == "deluxeplusplus":
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(6,6))))
    r[positie[1],positie[0]] = int(objectid)
    r = " ".join(map(str, r.tolist())).replace('[', '').replace(',', '').replace(']', '')
    setHome(user, 'layout', r)


def upgradeHome(user : hikari.User, x=False, y=False):
    if getHome(user)['huistype'] == "starter" and x and not y:
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(2,2))))
        addx = np.array([-1,-1])
        r = np.hstack((r, np.atleast_2d(addx).T))
        r2 = np.asmatrix(np.array(list(np.matrix(getHome(user)['rotation']).reshape(2,2))))
        addx = np.array([0,0])
        r2 = np.hstack((r2, np.atleast_2d(addx).T))
        r3 = np.asmatrix(np.array(getHome(user)['harvesttimer']).reshape(2,2))
        addx = np.array([datetime.datetime.max,datetime.datetime.max])
        r3 = np.hstack((r3, np.atleast_2d(addx).T))
    if getHome(user)['huistype'] == "starter" and y and not x:
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(2,2))))
        addx = np.array([-1,-1])
        r = np.vstack ((r, addx))
        r2 = np.asmatrix(np.array(list(np.matrix(getHome(user)['rotation']).reshape(2,2))))
        addx = np.array([0,0])
        r2 = np.vstack ((r2, addx))
        r3 = np.asmatrix(np.array(getHome(user)['harvesttimer']).reshape(2,2))
        addx = np.array([datetime.datetime.max,datetime.datetime.max])
        r3 = np.vstack ((r3, addx))
    if getHome(user)['huistype'] == "starterx" and x and not y:
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(2,3))))
        addx = np.array([-1,-1])
        r = np.hstack((r, np.atleast_2d(addx).T))
        r2 = np.asmatrix(np.array(list(np.matrix(getHome(user)['rotation']).reshape(2,3))))
        addx = np.array([0,0])
        r2 = np.hstack((r2, np.atleast_2d(addx).T))
        r3 = np.asmatrix(np.array(getHome(user)['harvesttimer']).reshape(2,3))
        addx = np.array([datetime.datetime.max,datetime.datetime.max])
        r3 = np.hstack((r3, np.atleast_2d(addx).T))
    if getHome(user)['huistype'] == "starterx" and y and not x:
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(2,3))))
        addx = np.array([-1,-1,-1])
        r = np.vstack ((r, addx))
        r2 = np.asmatrix(np.array(list(np.matrix(getHome(user)['rotation']).reshape(2,3))))
        addx = np.array([0,0,0])
        r2 = np.vstack ((r2, addx))
        r3 = np.asmatrix(np.array(getHome(user)['harvesttimer']).reshape(2,3))
        addx = np.array([datetime.datetime.max,datetime.datetime.max,datetime.datetime.max])
        r3 = np.vstack ((r3, addx))
    if getHome(user)['huistype'] == "startery" and x and not y:
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(3,2))))
        addx = np.array([-1,-1,-1])
        r = np.hstack((r, np.atleast_2d(addx).T))
        r2 = np.asmatrix(np.array(getHome(user)['rotation']).reshape(3,2))
        addx = np.array([0,0,0])
        r2 = np.hstack((r2, np.atleast_2d(addx).T))
        r3 = np.asmatrix(np.array(getHome(user)['harvesttimer']).reshape(3,2))
        addx = np.array([datetime.datetime.max,datetime.datetime.max,datetime.datetime.max])
        r3 = np.hstack((r3, np.atleast_2d(addx).T))
    if getHome(user)['huistype'] == "startery" and y and not x:
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['layout']).reshape(3,2))))
        addx = np.array([-1,-1])
        r = np.vstack ((r, addx))
        r2 = np.asmatrix(np.array(list(np.matrix(getHome(user)['rotation']).reshape(3,2))))
        addx = np.array([0,0])
        r2 = np.vstack ((r2, addx))
        r3 = np.asmatrix(np.array(getHome(user)['harvesttimer']).reshape(3,2))
        addx = np.array([datetime.datetime.max,datetime.datetime.max])
        r3 = np.vstack ((r3, addx))
    r = " ".join(map(str, r.tolist())).replace('[', '').replace(',', '').replace(']', '')
    r2 = " ".join(map(str, r2.tolist())).replace('[', '').replace(',', '').replace(']', '')
    setHome(user, 'layout', r)
    setHome(user, 'rotation', r2)
    print(r3.flatten().tolist()[0])
    setHome(user, 'harvesttimer', r3.flatten().tolist())


def getHomeRotation(user : hikari.User, x, y):
    try:
        if getHome(user)['huistype'] == "starter":
            r = np.asmatrix(np.array(list(np.matrix(getHome(user)['rotation']).reshape(2,2))))[x,y]
            return r
        if getHome(user)['huistype'] == "starterx":
            r = np.asmatrix(np.array(list(np.matrix(getHome(user)['rotation']).reshape(2,3))))[x,y]
            return r
        if getHome(user)['huistype'] == "startery":
            r = np.asmatrix(np.array(list(np.matrix(getHome(user)['rotation']).reshape(3,2))))[x,y]
            return r
        if getHome(user)['huistype'] == "starter+":
            r = np.asmatrix(np.array(list(np.matrix(getHome(user)['rotation']).reshape(3,3))))[x,y]
            return r
        if getHome(user)['huistype'] == "starter+y":
            r = np.asmatrix(np.array(list(np.matrix(getHome(user)['rotation']).reshape(4,2))))[x,y]
            return r
        if getHome(user)['huistype'] == "starter+x":
            r = np.asmatrix(np.array(list(np.matrix(getHome(user)['rotation']).reshape(2,4))))[x,y]
            return r
        if getHome(user)['huistype'] == "deluxeplusplus":
            r = np.asmatrix(np.array(list(np.matrix(getHome(user)['rotation']).reshape(6,6))))[x,y]
            return r
    except:
        return 0

    

def setHomeRotation(user : hikari.User, x, y):
    if getHome(user)['huistype'] == "starter":
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['rotation']).reshape(2,2))))
    if getHome(user)['huistype'] == "starterx":
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['rotation']).reshape(2,3))))
    if getHome(user)['huistype'] == "startery":
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['rotation']).reshape(3,2))))
    if getHome(user)['huistype'] == "starter+":
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['rotation']).reshape(3,3))))
    if getHome(user)['huistype'] == "starter+y":
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['rotation']).reshape(4,2))))
    if getHome(user)['huistype'] == "starter+x":
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['rotation']).reshape(2,4))))
    if getHome(user)['huistype'] == "deluxeplusplus":
        r = np.asmatrix(np.array(list(np.matrix(getHome(user)['rotation']).reshape(6,6))))
    if r[y,x] > 0:
        r[y,x] = r[y,x]-1
    elif r[y,x] == 0:
        r[y,x] = 3
    r = " ".join(map(str, r.tolist())).replace('[', '').replace(',', '').replace(']', '')
    setHome(user, 'rotation', r)
async def getHomeTiles(user:hikari.User):
    homelayout = getHomeLayout(user)
    return int(np.shape(homelayout)[0] * np.shape(homelayout)[1])


