# -*- coding: utf-8 -*-
"""
A Discord bot component for handling phone-like interface interactions in a game.
This module implements a phone-like interface for a Discord bot game where users can:
- Manage their virtual home/crib (place/remove/upgrade items)
- Perform activities like fishing, begging, and robbing
- Access store to buy items
- Customize their interface
- View inventory/pocket
- Check quests and rewards
The component uses Hikari and Tanjun frameworks for Discord interactions.
Global Variables:
    message_ids (dict): Tracks active message IDs for interface management
    fake (Faker): Faker instance for generating random names
    component (tanjun.Component): The main component instance
Key Features:
- Interactive button-based interface
- Persistent state management
- Multiple activity systems
- Virtual economy with multiple currencies
- Inventory and customization systems
- Time-based activities and cooldowns
Dependencies:
    - hikari: Discord API wrapper
    - tanjun: Command handler
    - numpy: Array operations
    - humanize: Time formatting
    - faker: Random name generation
    - datetime: Time operations
    - pickle: State persistence
    - logging: Debug logging
    - database: Custom database interface
    - imageprocessing: Custom image processing
"""
# cython: language_level=3
import asyncio
import datetime
import hikari
import hikari.api.cache
import hikari.guilds
import humanize
import logging
import math
import numpy as np
import pickle
import random
import re
import tanjun
from faker import Faker

#Temporary until tanjun has been updated to not use deprecated functions 
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import database
import imageprocessing

logger = logging.getLogger(__name__)

#Faker is used for generating fake data, in this case it is used to generate fake names for organizations, begging etc.
fake = Faker('en-us')
component = tanjun.Component()

message_ids = {}
#Load messages file, so messages state is same as before the bot went offline
try:
    with open('messages.pkl', 'rb') as f:
        message_ids = pickle.load(f)
        logger.info("Messages: Messages file loaded")
except:
    logger.error("Messages: Not able to load messages file")

#Here all Discord Interactions are handled and linked to their respective handler functions
@component.with_listener(hikari.InteractionCreateEvent)
async def phoneInteraction(event: hikari.InteractionCreateEvent) -> None:

    if "custom_id" in dir(event.interaction):
        #Log the interaction
        member = event.interaction.member.id
        logger.info(f"Interaction by {event.interaction.member.global_name}({member}): {event.interaction.custom_id}")

        #Check if the interaction is by the user that initiated the king command
        if member != event.interaction.message.interaction.user.id:
            await event.interaction.create_initial_response(4, f"<@{member}> This is not your phone! open your own phone by using the `/king` command :wink:", flags=hikari.MessageFlag.EPHEMERAL)
            logger.warning(f"Interaction by {event.interaction.member.global_name}({member}) was not for their phone")
            return
        
        if message_ids[member] != event.interaction.message.id:
            await event.interaction.create_initial_response(7, f"<@{member}> This phone is outdated! Please use the newer phone that is already open or open a new phone by using the `/king` command :wink:", flags=hikari.MessageFlag.EPHEMERAL, components=[], attachment=None)
            logger.warning(f"Interaction by {event.interaction.member.global_name}({member}) was on a old phone")
            await asyncio.sleep(5)
            await event.interaction.delete_initial_response()
            return

        #Fetch message so we know what message to edit
        message = event.interaction.message
        
        # Define handler mapping
        INTERACTION_HANDLERS = {
            "register": handle_registration,
            "yourcrib": handle_your_crib,
            "harvest": handle_your_crib,
            "remove": handle_remove_menu,
            "activities": handle_activities,
            "fishing": (handle_fishing_start if "_FISHSTART_" in event.interaction.custom_id 
                   else handle_fishing_stop if "_FISHSTOP_" in event.interaction.custom_id
                   else handle_fishing),
            "quests": handle_quests,
            "rob": handle_rob,
            "rotate": handle_rotate,
            "upgrade": (handle_upgrade_screen if "_UPGRADESCREEN_" in event.interaction.custom_id 
                    else handle_upgrade_selection),
            "place2": handle_place_selection,
            "place1": handle_place_list,
            "pocket": handle_pocket,
            "settings": handle_settings,
            "store": handle_store,
            "beg": handle_beg,
            "homemenu": handle_main_menu,
            "stop": handle_stop
        }

        # Extract command from custom_id
        command = event.interaction.custom_id.replace(str(member), "")
        base_command = next((k for k in INTERACTION_HANDLERS.keys() if command.startswith(k)), None)

        if base_command:
            await INTERACTION_HANDLERS[base_command](event, member, message)


async def handle_harvest(event, member, message):
    timers = database.getHarvestTimer(member)
    print(timers)

    # Check if user has plants to harvest
    if database.getStat(member, "harvest") != 1:
        await message.edit(f'<@{member}>, You do not have any plants to harvest!')

    # Check if user has plants to harvest but they are not ready
    elif database.isHarvestable(member) == False:
        await message.edit(f'<@{member}>, Your harvest is ready in `'+str(humanize.precisedelta(timers.min()))+'!`')

    # Check if user has plants to harvest and they are ready
    elif database.getStat(member, "harvest") == 1 and (timers.min() <= datetime.datetime.now()):
        plants = database.getItemsIDByBehaviour('420')
        harvestreward = 0
        for x in range(0, len(database.getHomeLayout(member))):
            for y in range(0, database.getHomeLayout(member).shape[1]):
                if database.getHomeLayout(member)[x, y] in plants and timers[x, y] <= datetime.datetime.now():
                    harvestreward += database.getReward(database.getHomeLayout(member)[x, y])
                    timers[x, y] = datetime.datetime.now() + datetime.timedelta(hours=3)
                else:
                    timers[x, y] = datetime.datetime.max
        database.addObject(member, -100, harvestreward)
        database.setStat(member, 'lastharvest', datetime.datetime.now())
        print(timers.flatten())
        database.setHome(member, 'harvesttimer', timers.flatten().tolist())
        await message.edit(f'<@{member}> harvested `{database.money} {harvestreward}` !')

async def handle_place(event, member, message):
    string = re.sub(r'^.*?_', '', str(event.interaction.custom_id[:-7]))
    itemid = int(string.split("_", 1)[0])
    rowid = int(string.split("_", 1)[1].split("_", 1)[0])
    colid = int(string.split("_", 1)[1].split("_", 1)[1])
    roomlayout = np.asarray((database.getHomeLayout(member)))
    harvesttimerlayout = np.asarray((database.getHarvestTimer(member)))
    if roomlayout[rowid][colid] == -1:
        plantsdb = database.getItemsIDByBehaviour('420')
        storagedb = database.getItemsIDByBehaviour('STR')
        if itemid in plantsdb and database.getStat(member, 'harvest') == 0:
            database.setStat(member, 'harvest', True)
            database.setStat(member, 'lastharvest', datetime.datetime.now())
            harvesttimerlayout[rowid][colid] = datetime.datetime.now() + datetime.timedelta(hours=3)
        database.removeObject(member, itemid, 1)
        database.setHomeLayout(member, (colid, rowid), itemid)
        database.setHome(member, 'harvesttimer', harvesttimerlayout.flatten().tolist())
        await message.edit("<@"+str(member)+"> placed a `"+database.getItemName(itemid)+'` in their crib.')

async def handle_upgrade(event, member, message):
    string = re.sub(r'^.*?_', '', str(event.interaction.custom_id[:-11]))
    itemid = int(string.split("_", 1)[0])
    rowid = int(string.split("_", 1)[1].split("_", 1)[0])
    colid = int(string.split("_", 1)[1].split("_", 1)[1])
    upgradeable, upgrade, upgradeamount = database.getIfUpgradeable(itemid)
    coins = database.getObject(member, -100)
    krediet = database.getObject(member, -200)
    upgradecoins = database.getItemDB(upgrade, 'money')
    upgradekrediet = database.getItemDB(upgrade, 'credits')
    if upgradeable != 0:
        if coins >= upgradecoins and krediet >= upgradekrediet:
            database.removeObject(member, -100, upgradecoins)
            database.removeObject(member, -200, upgradekrediet)
            database.setHomeLayout(member, (colid,rowid), upgrade)
            await message.edit(f'<@{member}> Upgraded `{database.getItemName(itemid)}` to `{database.getItemName(upgrade)}`!')

async def handle_your_crib(event, member, message):
    if event.interaction.custom_id == "harvest":
        await handle_harvest(event, member, message)
    elif event.interaction.custom_id.endswith("_PLACE_"):
        await handle_place(event, member, message)
    elif event.interaction.custom_id.endswith("_DOUPGRADE_"):
        await handle_upgrade(event, member, message)
    row = hikari.impl.MessageActionRowBuilder()
    row.add_interactive_button(hikari.ButtonStyle.PRIMARY, "place1" , label='Place')
    row.add_interactive_button(hikari.ButtonStyle.PRIMARY, "remove" , label='Remove')
    row.add_interactive_button(hikari.ButtonStyle.PRIMARY, "rotate" , label='Rotate')
    row.add_interactive_button(hikari.ButtonStyle.PRIMARY, "upgrade" , label='Upgrade')
    row2 = hikari.impl.MessageActionRowBuilder()
    if database.getStat(member, "harvest") == 1 and database.getHarvestTimer(member).min() <= datetime.datetime.now():
        row2.add_interactive_button(hikari.ButtonStyle.SUCCESS, "harvest", label='Harvest 🌿')
    elif database.getStat(member, "harvest") == 0:
        row2.add_interactive_button(hikari.ButtonStyle.SECONDARY, "harvest", label='Harvest 🌿', is_disabled=True)
    else:
        row2.add_interactive_button(hikari.ButtonStyle.SECONDARY, "harvest", label='🌿 in '+str(humanize.precisedelta(database.getHarvestTimer(member).min(),minimum_unit='hours',format='%0.2f'))+'!')
    row2.add_interactive_button(hikari.ButtonStyle.PRIMARY, "homemenu" , label='Back')
    row2.add_interactive_button(hikari.ButtonStyle.DANGER, "stop" , label='Stop')
    await event.interaction.create_initial_response(7, attachment=await imageprocessing.GetPhoneHome(member), components=[row, row2])

async def handle_registration(event, member, message):
    database.initiation(member)
    await handle_main_menu(event, member, message)

async def handle_activities(event, member, message):
    row = hikari.impl.MessageActionRowBuilder()
    if database.getStat(member, "lastbeg") + datetime.timedelta(seconds=60) <= datetime.datetime.now():
        row.add_interactive_button(hikari.ButtonStyle.PRIMARY, "beg", label='Beg')
    else:
        row.add_interactive_button(hikari.ButtonStyle.SECONDARY, "beg", label='🤲 in '+str(humanize.precisedelta(database.getStat(member, "lastbeg") + datetime.timedelta(seconds=60)))+'!')
    row.add_interactive_button(hikari.ButtonStyle.PRIMARY, "rob" , label='Rob')
    row.add_interactive_button(hikari.ButtonStyle.PRIMARY, "fishing" , label='Fishing')
    row2 = hikari.impl.MessageActionRowBuilder()
    row2.add_interactive_button(hikari.ButtonStyle.SECONDARY, "enterprises" , label='Enterprises', is_disabled=True)
    row2.add_interactive_button(hikari.ButtonStyle.SECONDARY, "explore" , label='Explore', is_disabled=True)
    row2.add_interactive_button(hikari.ButtonStyle.SECONDARY, "workjob" , label='Work Job', is_disabled=True)
    row3 = hikari.impl.MessageActionRowBuilder()
    row3.add_interactive_button(hikari.ButtonStyle.PRIMARY, "homemenu" , label='Back')
    row3.add_interactive_button(hikari.ButtonStyle.DANGER, "stop" , label='Stop')
    await event.interaction.create_initial_response(7, attachment=await imageprocessing.GetActivitiesMenu(member), components=[row, row2, row3])

async def handle_fishing(event, member, message):
    fishingitems = database.getItemsIDByBehaviour('FSH')
    rods = []
    hasrod = False
    for i in fishingitems:
        if database.getItemDB(i,"fishitemtype") == 'rod':
            rods.append(i)
    for i in rods:
        try:
            if database.getObject(member,i) > 0:
                hasrod = True
        except:
            logger.info('error with checking rods')

    # Make fishing channel if does not exist
    if event.interaction.channel_id not in database.fishingchannels:
        database.fishingchannels[event.interaction.channel_id] = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
    

    if hasrod:
        

        # Create fishing button grid
        rows = []
        for i in range(4):  # 4 rows
            row = hikari.impl.MessageActionRowBuilder()
            for j in range(5):  # 5 columns
                if database.fishingchannels[event.interaction.channel_id][i][j] == 0:
                    row.add_interactive_button(
                        hikari.ButtonStyle.PRIMARY,
                        f"fishing_{i}_{j}_FISHSTART_",
                        label='🎣'
                    )
                else:
                    row.add_interactive_button(
                        hikari.ButtonStyle.DANGER,
                        f"fishing_{i}_{j}",
                        label='🎣'
                    )
            rows.append(row)

        row, row2, row3, row4 = rows
        row5 = hikari.impl.MessageActionRowBuilder()
        row5.add_interactive_button(hikari.ButtonStyle.PRIMARY, "activities", label='Back')
        message = await event.interaction.create_initial_response(7, components=[row, row2, row3,row4,row5], attachment=await imageprocessing.GetFishing(member, event.interaction.channel_id))
                
    else:
        row5 = hikari.impl.MessageActionRowBuilder()
        row5.add_interactive_button(hikari.ButtonStyle.PRIMARY, "activities", label='Back')
        message = await event.interaction.create_initial_response(7, f'<@{member}>, you need a fishing rod to be able to fish!', components=[row5], attachment=await imageprocessing.GetFishing(member, event.interaction.channel_id))
    
async def handle_fishing_start(event, member, message):
    string = re.sub(r'^.*?_', '', str(event.interaction.custom_id[:-11]))
    posx = int(string.split("_", 1)[0])
    posy = int(string.split("_", 1)[1].split("_", 1)[0])
    if event.interaction.channel_id not in database.fishingchannels:
        database.fishingchannels[event.interaction.channel_id] = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]

    #TODO if spot already taken
    if database.fishingchannels[event.interaction.channel_id][posx][posy] != 0:
        return
    database.fishingchannels[event.interaction.channel_id][posx][posy] = member
    try:
        database.fishingchannelstimes[event.interaction.channel_id][posx][posy] = datetime.datetime.now()
    except: #create fishing channel if missing
        database.fishingchannelstimes[event.interaction.channel_id] = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
        database.fishingchannelstimes[event.interaction.channel_id][posx][posy] = datetime.datetime.now()

    row = hikari.impl.MessageActionRowBuilder()
    row.add_interactive_button(hikari.ButtonStyle.SECONDARY, "fishing"  + '_FISHSTOP_', label='Pull rod')
    await event.interaction.create_initial_response(7, component=row)
    await message.edit(f'<@{member}> cast their `{database.getItemDB(60, 'emoji')} {database.getItemDB(60, 'name')}`', attachment=await imageprocessing.GetFishing(member, event.interaction.channel_id))
    
    #Fishing loop, Updates every 10 seconds
    async def fishing_task():
        fishtimer = 0
        while await database.isFishing(member, event.interaction.channel_id):
            await asyncio.sleep(10)
            now = int((datetime.datetime.now() - datetime.datetime.utcfromtimestamp(0)).total_seconds() / 10)
            random.seed(member - now)
            r = random.random()
            if fishtimer >= 30:  # If afk too long, remove player from fishing (30 cycles, 5 minutes)
                for a, i in enumerate(database.fishingchannels[event.interaction.channel_id]):
                    for y, b in enumerate(i):
                        if database.fishingchannels[event.interaction.channel_id][a][y] == member:
                            database.fishingchannels[event.interaction.channel_id][a][y] = 0
                            break
                
                await message.edit(f'<@{member}>, your connection to the fishing channel has been closed for being afk for too long!')
                return
            fishtimer += 1
            await message.edit(attachment=await imageprocessing.GetFishing(member, event.interaction.channel_id))

    # Create and start the task
    task = asyncio.create_task(fishing_task(), name='Fishing Task - '+str(member))
    try:
        await task
    except asyncio.CancelledError:
        pass
    finally:
        if not await database.isFishing(member, event.interaction.channel_id):
            task.cancel()
    
        

async def handle_fishing_stop(event, member, message):
    # cancel fishing task if still running
    task, = [task for task in asyncio.all_tasks() if task.get_name() == 'Fishing Task - '+str(member)]
    task.cancel()
    
    # Make fishing channel if does not exist
    if event.interaction.channel_id not in database.fishingchannels:
        database.fishingchannels[event.interaction.channel_id] = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
    
    

    if await database.isFishing(member, event.interaction.channel_id):
        if await database.hasFishBitten(member, event.interaction.channel_id):
            # Get all items from database
            fsh_behaviour = database.getAllItemIDWhere('behaviour','FSH')
            fish_item = database.getAllItemIDWhere('fishitemtype','fish')

            fish_items = []

            for i in fsh_behaviour:
                if i in fish_item:
                    fish_items.append(i[0])

            weights = {}
            for i in fish_items:
                fish_rarity = database.getItemDB(i, 'fishrarity') 
                weights[i] = fish_rarity + 1

            # reverse weights
            for id in weights:
                weights[id] = max(weights.values()) + 1 - weights[id]
            # Select random fish based on weights
            reward = random.choices(fish_items, 
                                    weights=list(weights.values()), 
                                    k=1)[0]
            database.addObject(member, reward, 1)
            await message.edit(f"<@{member}> caught a `{database.getItemDB(reward, 'emoji')} {database.getItemName(reward)}` while fishing.")

        #Get the member id and the message id to clear fishing channel if in use by user
        fishingchannel = database.fishingchannels[message.channel_id]
        if message.channel_id in database.fishingchannels:
            for x, i in enumerate(fishingchannel):
                for y, b in enumerate(i):
                    if database.fishingchannels[message.channel_id][x][y] == member:
                        database.fishingchannels[message.channel_id][x][y] = 0
    
    # Create fishing button grid
    rows = []
    for i in range(4):  # 4 rows
        row = hikari.impl.MessageActionRowBuilder()
        for j in range(5):  # 5 columns
            if database.fishingchannels[event.interaction.channel_id][i][j] == 0:
                row.add_interactive_button(
                    hikari.ButtonStyle.PRIMARY,
                    f"fishing_{i}_{j}_FISHSTART_",
                    label='🎣'
                )
            else:
                row.add_interactive_button(
                    hikari.ButtonStyle.DANGER,
                    f"fishing_{i}_{j}",
                    label='🎣'
                )
        rows.append(row)

    row, row2, row3, row4 = rows  # Unpack for backward compatibility
    row5 = hikari.impl.MessageActionRowBuilder()
    row5.add_interactive_button(hikari.ButtonStyle.PRIMARY, "activities", label='Back')
    
    message = await event.interaction.create_initial_response(7, components=[row, row2, row3,row4,row5], attachment=await imageprocessing.GetFishing(member, event.interaction.channel_id))
    
async def handle_quests(event, member, message):
    # if _DAILY_ is in the interaction id, check if the daily reward can be claimed, if so claim it, if not show the time left
    if str(event.interaction.custom_id).endswith("_DAILY_"):
        # Check if reward was claimed over 24 hours ago
        if database.getStat(member, 'lastdaily') <= (datetime.datetime.now() - datetime.timedelta(days=1)):
            # if reward was claimed over 48 hours ago, reset counter else get counter
            if database.getStat(member, 'lastdaily') <= (datetime.datetime.now() - datetime.timedelta(days=2)):
                dailycounter = 0
            else:
                dailycounter = database.getStat(member, 'dailycounter')

            rewards = {
                0: (10, 10),
                1: (20, 15), 
                2: (50, 20),
                3: (100, 25),
                4: (200, 30)
            }
            
            money, credits = rewards[dailycounter]
            
            # Add rewards
            database.addObject(member, -100, money)
            database.addObject(member, -200, credits)
        
            await message.edit(f"<@{member}> gained `{database.money} {money}` and `{database.credit} {credits}` from their daily task. Come back tomorrow for more rewards!")
            
            dailycounter += 1
            if dailycounter >= 5:
                dailycounter = 0
            database.setStat(member, 'dailycounter', dailycounter)
            database.setStat(member, 'lastdaily', datetime.datetime.now())
        else:
            await message.edit("<@"+str(member)+f'>, come back in {humanize.naturaltime((database.getStat(member, "lastdaily") + datetime.timedelta(days=1)), future=True)} for more rewards!')

    row = hikari.impl.MessageActionRowBuilder()
    row.add_interactive_button(hikari.ButtonStyle.PRIMARY, "homemenu" , label='Back')
    if database.getStat(member, 'lastdaily') <= (datetime.datetime.now() - datetime.timedelta(days=1)):
        row.add_interactive_button(hikari.ButtonStyle.SUCCESS, "quests"  + '_DAILY_', label='Daily Rewards')
    else:
        row.add_interactive_button(hikari.ButtonStyle.SECONDARY, "quests"  + '_DAILY_', label='🎁 in '+str(humanize.precisedelta(database.getStat(member, 'lastdaily') + datetime.timedelta(days=1),minimum_unit='hours'))+'!', is_disabled=True)
    await event.interaction.create_initial_response(7, components=[row], attachment=await imageprocessing.getQuests(member))

async def handle_rob(event, member, message):
    try:
        page = int(event.interaction.custom_id.split('_')[-1])
    except:
        page = 1

    lastrob = database.getStat(member, "lastrob")
    if datetime.datetime.now() >= lastrob + datetime.timedelta(hours=2):
        database.setStat(member, 'rob', 0)

    row = hikari.impl.MessageActionRowBuilder()
    row4 = hikari.impl.ModalActionRowBuilder()
    row4.add_text_input('robbed', 'Player to Rob (USERNAME, not DISPLAY NAME)', )
    row.add_interactive_button(hikari.ButtonStyle.SUCCESS, 'rob_mostwanted', label='Rob by 🏆')
    row.add_interactive_button(hikari.ButtonStyle.SUCCESS, 'rob_mostwanted_you', label='Your 🏅')
    row.add_interactive_button(hikari.ButtonStyle.SUCCESS, 'rob_byname', label='Rob by Name')
    row.add_interactive_button(hikari.ButtonStyle.PRIMARY, "activities" , label='Back')
    row2 = hikari.impl.MessageActionRowBuilder()
    pagesrow = hikari.impl.MessageActionRowBuilder()

    if 'byname' in event.interaction.custom_id:
        await event.interaction.create_modal_response(custom_id = 'robname', title='Works across all servers! 🦹', components=[row4])
        return
    
    target = 0
    if 'robbing' in event.interaction.custom_id:
        target : int = event.interaction.values[0]
    if 'robname' in event.interaction.custom_id:
        users = event.app.cache.get_users_view()
        # Get user id from username by checking all users in cache
        for i in users:
            if event.app.cache.get_user(i).username == event.interaction.components[0].components[0].value:
                target : int = event.app.cache.get_user(i).id
                break
    if 'robbing' in event.interaction.custom_id or 'robname' in event.interaction.custom_id:
        if database.getStat(member, "rob") >= 4:
            await message.edit(f'You have robbed too many times, come back later!')
        elif int(target) != 0:
            if int(target) != member:
                targetname = event.app.cache.get_user(target).display_name
                if database.getStat(member, "rob") < 4:
                    if database.getObject(member, -100) < 10:
                        await message.edit(f'You need some `{database.money}` to rob players, come back when you have atleast `{database.money} 10`.')
                    elif database.getObject(target, -100) < 10:
                        await message.edit(
                            (f'`{targetname}` is too poor to be robbed.'))
                    elif random.random() < (1/2):
                        maxreward = database.getObject(target, -100)
                        robreward = random.choices(range(5, maxreward), k=1, weights=list(range(maxreward-5, 0, -1)))[0]
                        await message.edit((f"You robbed **{targetname}** of `{database.money} {robreward}`"))
                        await event.app.cache.get_user(target).send(f'`{event.interaction.member.display_name}` has stolen `{database.money} {robreward}` from you in `{event.interaction.get_guild()}`!')
                        database.addObject(member, -100, robreward)
                        database.removeObject(target, -100, robreward)
                        database.setStat(member, "rob", int(database.getStat(member, "rob")) + 1)
                    else:
                        maxreward = database.getObject(member, -100) 
                        robreward = random.choices(range(5, maxreward), k=1, weights=list(range(maxreward-5, 0, -1)))[0]
                        await message.edit(f"Your attempt of robbery has failed. For this failure you paid `{targetname}` `{database.money} {robreward}`.")
                        await event.app.cache.get_user(target).send(f'`{event.interaction.member.display_name}` failed robbing you in `{event.interaction.get_guild()}`. For this failure you receive `{database.money} {robreward}`!')
                        database.removeObject(member, -100, robreward)
                        database.addObject(target, -100, robreward)
                        database.setStat(member, "rob", int(database.getStat(member, "rob")) + 1)
                    if int(database.getStat(member, "rob")) == 1:
                        database.setStat(member, "lastrob", datetime.datetime.now())
            else:
                await message.edit(f'You cannot rob yourself!')
        else:
            await message.edit(f'User not found!')

    if 'mostwanted' in event.interaction.custom_id:
        guildmembers = event.app.cache.get_members_view_for_guild(event.interaction.get_guild())
        botmembers = database.getObjectAll(-100)

        wanteddict = {}
        for i in botmembers:
            if i in guildmembers:    
                wanteddict[event.app.cache.get_user(i).id] = event.app.cache.get_user(i).display_name, event.app.cache.get_user(i)
        wanteddictids = list(wanteddict.keys())
        
        
        playerranking = wanteddictids.index(member)
        # Calculate number of pages and range for current page
        pages = math.ceil(len(wanteddictids)/25)
        if page == 1:
            min_range = 0
        else:
            min_range = 25*(page-1)
        max_range = (25 * page)

        # Calculate page containing player ranking if pressing Your 🏅
        if 'mostwanted_you' in event.interaction.custom_id:
            # Calculate page containing player ranking
            page = math.ceil((playerranking + 1)/25) 
            min_range = 25*(page-1)
            max_range = (25*page)
        # Ensure max_range doesn't exceed list length on last page
        final_max = min(max_range, len(wanteddict))
        
        pagesrow.add_interactive_button(hikari.ButtonStyle.PRIMARY, f"rob_mostwanted_{page-5}", label='-5', is_disabled=(page <= 5))
        pagesrow.add_interactive_button(hikari.ButtonStyle.PRIMARY, f"rob_mostwanted_{page-1}", label='◀', is_disabled=(page == 1))
        pagesrow.add_interactive_button(hikari.ButtonStyle.PRIMARY, f"rob_mostwanted_randompage_{random.randint(1,pages)}", label='Random Page', is_disabled=(pages < 3))
        pagesrow.add_interactive_button(hikari.ButtonStyle.PRIMARY, f"rob_mostwanted_{page+1}", label='▶', is_disabled=(page == pages))
        pagesrow.add_interactive_button(hikari.ButtonStyle.PRIMARY, f"rob_mostwanted_{page+5}", label='+5', is_disabled=(page + 5 > pages))

        selectlist = row2.add_text_menu('robbing', placeholder=f'Most Wanted in {event.interaction.get_guild().name} - Page #{page}', min_values=1)

        
        emoji_map = {
            0: '🥇',
            1: '🥈', 
            2: '🥉'
        }

        # Build options list
        for idx in range(min_range, final_max):
            is_default = (idx == playerranking and 'mostwanted_you' in event.interaction.custom_id)
            
            # Get emoji for this rank
            if idx == playerranking and idx > 2:
                emoji = '⭐'
            else:
                emoji = emoji_map.get(idx, '👤')
                
            if idx == playerranking:
                description = 'GEAR IS WIP, CANNOT ROB YOURSELF'
            else:
                description = f'GEAR IS WIP, Select to rob "{wanteddict[wanteddictids[idx]][0]}"'
            
            # Add option to dropdown
            selectlist.add_option(
                f'#{idx+1} - {wanteddict[wanteddictids[idx]][0]} ({wanteddict[wanteddictids[idx]][1]})',
                wanteddictids[idx], 
                description=description,
                emoji=emoji,
                is_default=is_default,
            )
            
    

        await event.interaction.create_initial_response(7, components=[row, row2, pagesrow], attachment=await imageprocessing.GetRobbing(member, event))
    else:
        await event.interaction.create_initial_response(7, components=[row], attachment=await imageprocessing.GetRobbing(member, event))
        


async def handle_rotate(event, member, message):
    roomlayout = np.asarray(np.fliplr(database.getHomeLayout(member)))

    # Handle rotation if requested
    if str(event.interaction.custom_id).endswith('_ROTATE_'):
        nofliproomlayout = np.asarray(database.getHomeLayout(member))
        string = re.sub(r'^.*?_', '', str(event.interaction.custom_id[:-8]))
        itemid, rowid, colid = map(int, string.split("_"))
        
        if nofliproomlayout[rowid][colid] != -1:
            database.setHomeRotation(member, colid, rowid)

    rows = []
    row_builders = [hikari.impl.MessageActionRowBuilder() for _ in range(5)]
    row_builders[-1].add_interactive_button(hikari.ButtonStyle.PRIMARY, "yourcrib", label='Back')

    for col_idx, row in enumerate(roomlayout):
        if col_idx >= len(row_builders):
            continue
            
        for row_idx, item in enumerate(row):
            if item != -1:
                row_builders[col_idx].add_interactive_button(
                    hikari.ButtonStyle.SUCCESS,
                    f"rotate_{item}_{col_idx}_{len(row)-1-row_idx}_ROTATE_",
                    label=database.getItemDB(item, 'emoji')
                )
            else:
                row_builders[col_idx].add_interactive_button(
                    hikari.ButtonStyle.DANGER,
                    f"asd_{random.randint(0,99)}_{random.randint(0,99)}_asd_",
                    label='😒',
                    is_disabled=True
                )

    rows = []
    for row_builder in row_builders:
        if len(row_builder.components) > 0:
            rows.append(row_builder)

    await event.interaction.create_initial_response(7, components=rows)
    await message.edit(attachment=await imageprocessing.GetPhoneHome(member))

async def handle_upgrade_screen(event, member, message):
    string = re.sub(
            r'^.*?_', '', str(event.interaction.custom_id[:-15]))

    rowid = int(string.split("_", 1)[0])
    colid = int(string.split("_", 1)[1].split("_", 1)[0])
    roomlayout = np.asarray((database.getHomeLayout(member)))
    itemtoup = roomlayout[rowid][colid]
    upgradeable, upgrade, upgradeamount = database.getIfUpgradeable(itemtoup)

    coins = database.getObject(member, -100)
    krediet = database.getObject(member, -200)

    row1 = hikari.impl.MessageActionRowBuilder()
    row1.add_interactive_button(hikari.ButtonStyle.PRIMARY, "upgrade", label='Back')
    upgradecoins = database.getItemDB(upgrade, 'money')
    upgradekrediet = database.getItemDB(upgrade, 'credits')
    if upgradeable != 0:
        if coins >= upgradecoins and krediet >= upgradekrediet:
            row1.add_interactive_button(hikari.ButtonStyle.SUCCESS, "yourcrib"+"_"+str(itemtoup)+"_"+str(rowid)+'_'+str(
            colid)+'_DOUPGRADE_', label=database.getItemDB(upgrade, 'emoji')+" Upgrade Item")
        else:
            row1.add_interactive_button(hikari.ButtonStyle.DANGER, "yourcrib"+"_"+str(itemtoup)+"_"+str(rowid)+'_'+str(
            colid)+'_DOUPGRADE_', label=database.getItemDB(upgrade, 'emoji')+" Upgrade Item", is_disabled=True)

    await event.interaction.create_initial_response(7, component=row1)
    await message.edit(attachment=await imageprocessing.GetPhoneUpgrading(member,itemtoup,upgrade,upgradeamount))

async def handle_upgrade_selection(event, member, message):
    roomlayout = np.asarray(np.fliplr(database.getHomeLayout(member)))
    coins = database.getObject(member, -100)
    krediet = database.getObject(member, -200)

    rows = [hikari.impl.MessageActionRowBuilder() for _ in range(5)]
    rows[-1].add_interactive_button(hikari.ButtonStyle.PRIMARY, "yourcrib", label='Back')

    def create_upgrade_button(row, item_id, col, row_length, can_upgrade=False):
        if item_id != -1:
            upgradeable, upgrade, upgradeamount = database.getIfUpgradeable(item_id)
            if upgradeable and upgrade != 0:
                upgradecoins = database.getItemDB(upgrade, 'money')
                upgradekrediet = database.getItemDB(upgrade, 'credits')
                has_resources = coins >= upgradecoins and krediet >= upgradekrediet
                
                row.add_interactive_button(
                    hikari.ButtonStyle.SUCCESS if has_resources else hikari.ButtonStyle.PRIMARY,
                    f"upgrade_{col}_{row_length}_UPGRADESCREEN_",
                    label=database.getItemDB(item_id, 'emoji')
                )
            else:
                row.add_interactive_button(
                    hikari.ButtonStyle.DANGER,
                    f"noupgrade_{col}_{row_length}",
                    label=database.getItemDB(item_id, 'emoji'),
                    is_disabled=True
                )
        else:
            row.add_interactive_button(
                hikari.ButtonStyle.DANGER,
                f"asd_{random.randint(0,99)}_{random.randint(0,99)}_asd_",
                label='😒',
                is_disabled=True
            )

    for col_idx, row in enumerate(roomlayout):
        if col_idx >= len(rows):
            continue
            
        row_length = len(row) - 1
        for item in row:
            create_upgrade_button(rows[col_idx], item, col_idx, row_length)
            row_length -= 1

    rows_with_components = []
    for row in rows:
        if len(row.components) > 0:
            rows_with_components.append(row)

    await event.interaction.create_initial_response(
        7,
        components=rows_with_components, 
        attachment=await imageprocessing.GetPhoneHome(member)
    )

async def handle_place_selection(event, member, message):
    item = int(event.interaction.values[0])

    roomlayout = np.asarray(np.fliplr(database.getHomeLayout(member)))

    rows = [hikari.impl.MessageActionRowBuilder() for _ in range(5)]
    
    rows[4].add_interactive_button(hikari.ButtonStyle.PRIMARY, "yourcrib", label='Back')

    for collength, i in enumerate(roomlayout):
        rowlenght = len(i)-1
        
        for e in i:
            print(e)
            if e == -1:
                rows[collength].add_interactive_button(
                    hikari.ButtonStyle.SUCCESS,
                    f"yourcrib_{item}_{collength}_{rowlenght}_PLACE_",
                    label='⬇️'
                )
            else:
                rows[collength].add_interactive_button(
                    hikari.ButtonStyle.DANGER, 
                    f"asd_{e}_{collength}_{rowlenght}_PLACE_",
                    label=database.getItemDB(e, 'emoji'),
                    is_disabled=True
                )
            rowlenght -= 1

    filtered_rows = []
    for row in rows:
        if row.components:
            filtered_rows.append(row) 

    rows = filtered_rows
    await message.edit(
        f"Choose where to place `{database.getItemName(item)}`.", 
        attachment=await imageprocessing.GetPhoneHome(member)
    )
    await event.interaction.create_initial_response(7, components=rows)

async def handle_place_list(event, member, message):
    items = database.getItemPlaceable(member)
    freespace = False
    roomlayout = np.asarray(database.getHomeLayout(member))
    for i in roomlayout:
        for e in i:
            if e == -1:
                freespace = True
    
    row1 = hikari.impl.MessageActionRowBuilder()

    # Calculate pagination 
    items_per_page = 25
    total_items = len(items)
    total_pages = math.ceil(total_items / items_per_page)
    if total_pages == 0:
        total_pages = 1

    # Get current page from custom_id, default to 1
    try:
        current_page = int(event.interaction.custom_id.split('_')[1]) 
    except:
        current_page = 1

    start_idx = (current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    select_menu = row1.add_text_menu('place2' if freespace and len(items) > 0 else 'place1', 
        placeholder='You dont have any items to place' if len(items) == 0 else f'Select item to place (Page {current_page}/{total_pages})' if freespace else "You don't have any free spots left",
        min_values=1)

    if freespace == True and len(items) > 0:
        for item_id in list(items)[start_idx:end_idx]:
            select_menu.add_option(
                database.getItemName(item_id),
                f"{item_id}",
                emoji=database.getItemDB(item_id, 'emoji'),
                description=database.getItemDB(item_id, 'description').replace('{reward}', str(database.getItemDB(item_id, "reward"))).replace('{money}',database.money),
            )
    elif freespace == False:
        select_menu.add_option(
            "You don't have any free spots left!",
            "0",
            emoji='🚫',
            description="You can remove items to make space."
        )
    else:
        select_menu.add_option(
            "You don't have any items to place!",
            "0",
            emoji='🚫',
            description="You can buy items from the shop."
        )

    # Add pagination buttons
    page_row = hikari.impl.MessageActionRowBuilder()
    page_row.add_interactive_button(
        hikari.ButtonStyle.PRIMARY, 
        f"place1_{current_page-1}", 
        label='◀',
        is_disabled=(current_page == 1)
    )
    page_row.add_interactive_button(
        hikari.ButtonStyle.SECONDARY,
        "yourcrib",
        label='Back'
    )
    page_row.add_interactive_button(
        hikari.ButtonStyle.PRIMARY,
        f"place1_{current_page+1}",
        label='▶',
        is_disabled=(current_page == total_pages)
    )

    r = [row1, page_row]

    

    await event.interaction.create_initial_response(7, components=r)

async def handle_pocket(event, member, message):
    objects = database.getObject(member)
    item = None
    row1 = hikari.impl.MessageActionRowBuilder() 
    row5 = hikari.impl.MessageActionRowBuilder()
    components = []
    if event.interaction.values:
        item = int(event.interaction.values[0])
    else:
        try:
            item = int(event.interaction.custom_id.split('_')[1])
        except:
            item = None
    if item is not None:
        if event.interaction.custom_id.endswith(("SELL1", "SELL5", "SELL10", "SELLALL")):
            sell_amounts = {
            "SELL1": 1,
            "SELL5": 5, 
            "SELL10": 10,
            "SELLALL": objects[item]
            }
            
            # Get amount to sell based on button pressed
            sell_type = event.interaction.custom_id.split("_")[-1]
            amount = sell_amounts[sell_type]
            
            # Check if user has enough items
            if objects[item] >= amount and amount >= 1:
                # Calculate total sell price
                total_price = database.getItemDB(item, 'sellprice') * amount
                
                # Update database and objects
                database.removeObject(member, item, amount)
                database.addObject(member, -100, total_price)
                objects[item] -= amount
                
                # Send confirmation message
                await message.edit(
                    f"<@{member}> sold {amount} `{database.getItemDB(item, 'emoji')} "
                    f"{database.getItemDB(item, 'name')}` for `{database.money} {total_price}`"
            )
        # Add buttons for selling items if item is sellable
        if item is not None and database.getItemDB(item, 'sellable'):
            row5.add_interactive_button(hikari.ButtonStyle.PRIMARY, "pocket"+'_'+str(item)+'_SELL1', 
                label=f'Sell for 💵 {database.getItemDB(item, "sellprice")}',
                is_disabled=(objects[item] < 1))
            row5.add_interactive_button(hikari.ButtonStyle.PRIMARY, "pocket"+'_'+str(item)+'_SELL5', 
                label=f'Sell x5',
                is_disabled=(objects[item] < 5))
            row5.add_interactive_button(hikari.ButtonStyle.PRIMARY, "pocket"+'_'+str(item)+'_SELL10', 
                label=f'Sell x10',
                is_disabled=(objects[item] < 10))
            row5.add_interactive_button(hikari.ButtonStyle.PRIMARY, "pocket"+'_'+str(item)+'_SELLALL', 
                label=f'Sell ALL',
                is_disabled=(objects[item] < 2))
            
            components.append(row5)
    

    # Add items to menu
    # Calculate total pages and current page
    items_per_page = 25
    total_items = len([i for i in objects if objects[i] != 0 and database.getItemDB(i, 'category') != 7])
    total_pages = math.ceil(total_items / items_per_page)
    
    # Get current page from custom_id, default to 1
    if 'page' in event.interaction.custom_id:
        current_page = int(event.interaction.custom_id.split('_')[-1]) 
    else:
        current_page = 1

    # Create text menu
    select_menu = row1.add_text_menu('pocket_select', placeholder=f'Your Items (Page {current_page}/{total_pages})', min_values=1)


    start_idx = (current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    # Add pagination buttons
    page_row = hikari.impl.MessageActionRowBuilder()
    page_row.add_interactive_button(
        hikari.ButtonStyle.PRIMARY, 
        f"pocket_page_{current_page-1}", 
        label='◀',
        is_disabled=(current_page == 1)
    )
    page_row.add_interactive_button(
        hikari.ButtonStyle.SECONDARY,
        "homemenu",
        label='Back'
    )
    page_row.add_interactive_button(
        hikari.ButtonStyle.PRIMARY,
        f"pocket_page_{current_page+1}",
        label='▶',
        is_disabled=(current_page == total_pages)
    )
    
    
    # Add items for current page to dropdown
    item_count = 0
    for x, i in enumerate(objects):
        if objects[i] != 0 and database.getItemDB(i, 'category') != 7:
            item_count += 1
            
            # Skip items before current page
            if item_count <= start_idx:
                continue
                
            # Stop after reaching items_per_page
            if item_count > end_idx:
                break
                
            name = database.getItemDB(i, 'name')
            description = database.getItemDB(i, 'description')
            emoji = database.getItemDB(i, 'emoji')
            
            # Add option to menu
            select_menu.add_option(
                f"{objects[i]} - {name.title()}", 
                str(i),
                emoji=emoji,
                description=description.replace('{reward}', str(database.getItemDB(i, "reward"))).replace('{money}',database.money),
                is_default=(i == item if item is not None else False)
            )


    components.append(row1)
    components.append(page_row)

    if item is not None and database.getObject(member, item) > 0:
        await event.interaction.create_initial_response(7, components=components, attachment=await imageprocessing.GetPocket(member,item))
    else:
        await event.interaction.create_initial_response(7, components=components, attachment=await imageprocessing.GetPhoneMenu(member))
        

async def handle_settings(event, member, message):
    # Handle setting a background
    if event.interaction.custom_id.endswith('_SETBACKGROUNDS_'):
        item = int(event.interaction.custom_id.split('_')[1])
        database.setStat(member, 'background', item)
        await message.edit(attachment=await imageprocessing.GetPhoneMenu(member))

    # Handle showing background selection menu  
    if event.interaction.custom_id.endswith('BACKGROUNDS_'):
        objects = database.getObject(member)
        background_items = [
            (id, objects[id], database.getItemDB(id, 'emoji'), database.getItemDB(id, 'name'))
            for id in objects
            if objects[id] != 0 and database.getItemDB(id, 'behaviour') == "BCK"
        ][:8] 

        rows = []
        back_row = hikari.impl.MessageActionRowBuilder()
        back_row.add_interactive_button(hikari.ButtonStyle.PRIMARY, "settings", label='Back')
        rows.append(back_row)

        for i in range(0, len(background_items), 2):
            row = hikari.impl.MessageActionRowBuilder()
            for item_id, count, emoji, name in background_items[i:i+2]:
                row.add_interactive_button(
                    hikari.ButtonStyle.SECONDARY,
                    f"settings_{item_id}_SETBACKGROUNDS_",
                    label=f'{count} - {emoji} {name.title()}'
                )
            rows.append(row)

        await event.interaction.create_initial_response(7, components=rows)
        return

    row = hikari.impl.MessageActionRowBuilder()
    row.add_interactive_button(hikari.ButtonStyle.PRIMARY, "settings_BACKGROUNDS_", label='Backgrounds')

    back_row = hikari.impl.MessageActionRowBuilder() 
    back_row.add_interactive_button(hikari.ButtonStyle.PRIMARY, "homemenu", label='Back')

    await event.interaction.create_initial_response(7, components=[row, back_row])

async def handle_store(event, member, message):
    itemdb = database.getAllItemDB()
    
    upgrade_paths = {
            'starter': [9900, 9901],
            'starterx': [9902, 9903], 
            'startery': [9902, 9904]
        }

    # Helper function to create paginated menu
    def create_paginated_menu(items, page=1, items_per_page=25, category=None):
        buy_Row = hikari.impl.MessageActionRowBuilder()
        try:
            item_from_value = int(event.interaction.custom_id.split('_')[2])
        except:
            item_from_value = None
        if event.interaction.values or item_from_value is not None:
            if item_from_value is None:
                item_from_value = int(event.interaction.values[0].split('_')[0])
            buy_Row.add_interactive_button(hikari.ButtonStyle.SUCCESS, event.interaction.custom_id+str(item_from_value)+"_BUYCHECK_", label='Buy for '+database.money
            +' '+str(itemdb[int(item_from_value)]['price'][0])+' '+database.credit
            +' '+str(itemdb[int(item_from_value)]['price'][1]),
            is_disabled=(database.getObject(member, -100) < database.getItemDB(item_from_value, 'money') or database.getObject(member, -200) < database.getItemDB(item_from_value, 'credits')))
        
        pages = math.ceil(len(items)/items_per_page)
        start_idx = (page-1) * items_per_page
        end_idx = start_idx + items_per_page
        
        row = hikari.impl.MessageActionRowBuilder()
        menu = row.add_text_menu(f'store_{category}_', placeholder=f'Page {page}/{pages}', min_values=1)
        
        for item_id in list(items.keys())[start_idx:end_idx]:
            item = items[item_id]
            menu.add_option(
                f"{item['name'].title()}", 
                f"{item_id}_BUY_", 
                emoji=item['emoji'],
                is_default=(item_id == item_from_value),
                description=f"{database.money} {item['price'][0]} {database.credit} {item['price'][1]}"
            )
            

        
        crib_submenu = ["FURNITURE", "FLOORING", "WALLPAPER", "CUSTOM"]

        nav_row = hikari.impl.MessageActionRowBuilder()
        nav_row.add_interactive_button(hikari.ButtonStyle.PRIMARY, f"store_{category}_page_{page-1}", label='◀', is_disabled=(page==1))
        nav_row.add_interactive_button(hikari.ButtonStyle.PRIMARY, "store_CRIB_" if category in crib_submenu else "store", label='Back') 
        nav_row.add_interactive_button(hikari.ButtonStyle.PRIMARY, f"store_{category}_page_{page+1}", label='▶', is_disabled=(page==pages))
        
        if item_from_value is not None:
            return [buy_Row, row, nav_row]
        return [row, nav_row]

    if "_page_" in event.interaction.custom_id:
        page = int(event.interaction.custom_id.split('_')[-1])
        category_map = {
            "GENERAL": 1,
            "FURNITURE": 2,
            "FLOORING": 6,
            "WALLPAPER": 5,
            "CUSTOM": 7
        }
        
        # Get current category from stored state
        current_category = event.interaction.message.components[0].components[0].placeholder.split()[0]
        category_id = category_map[current_category]
        
        # Filter items by category
        items = {k:v for k,v in itemdb.items() 
                if v['category'] == category_id and v['forsale']}
                
        components = create_paginated_menu(items, page, category=current_category)
        await event.interaction.create_initial_response(7, components=components, attachment=await imageprocessing.GetPocket(member, event.interaction.values[0].split('_')[0]) if event.interaction.values else hikari.undefined.UNDEFINED)
        return

    if event.interaction.custom_id.endswith("_BUYCHECK_"):
        item = str(event.interaction.custom_id).split('_')[2]
        if database.getItemDB(item,'forsale'):
            if database.getObject(member, item) >= database.isObjectLimit(member, item):
                await message.edit('<@'+str(member)+'> cant buy anymore of this item')
            elif database.getItemDB(item,'behaviour') == "UPG":
                item = int(item)
                if database.getObject(member, -100) >= database.getItemDB(item, 'money') and database.getObject(member, -200) >= database.getItemDB(item, 'credits'):
                    upgrades = {
                        (9900, "starter"): {"x": True, "type": "starterx"},
                        (9901, "starter"): {"y": True, "type": "startery"},
                        (9902, "starterx"): {"y": True, "type": "starter+"},
                        (9902, "startery"): {"x": True, "type": "starter+"},
                        (9903, "starterx"): {"x": True, "type": "starter+x"},
                        (9904, "startery"): {"y": True, "type": "starter+y"}
                    }

                    current_type = database.getHome(member)['huistype']
                    
                    # Check if upgrade is valid
                    if int(item) in upgrade_paths[current_type]:
                        upgrade = upgrades[(int(item), current_type)]

                        database.removeObject(member, -100, database.getItemDB(item, 'money'))
                        database.removeObject(member, -200, database.getItemDB(item, 'credits'))
                        database.upgradeHome(member, x=upgrade.get('x', False), y=upgrade.get('y', False))
                        database.setHome(member, "type", upgrade['type'])
                        
                        await message.edit(f'<@{member}> upgraded their crib!')
            elif database.getItemDB(item,'behaviour') == "WAL":
                if database.getObject(member, -100) >= database.getItemDB(item, 'money') and database.getObject(member, -200) >= database.getItemDB(item, 'credits'):
                    database.removeObject(member, -100, database.getItemDB(item, 'money'))
                    database.removeObject(member, -200, database.getItemDB(item, 'credits'))
                    database.setHome(member,'walls', int(item))
                    await message.edit('<@'+str(member)+'> just changed their wallpaper to `'+str(database.getItemDB(item, 'emoji'))+' '+str(database.getItemDB(item, 'name')).title()+'`')
            elif database.getItemDB(item,'behaviour') == "FLR":
                if database.getObject(member, -100) >= database.getItemDB(item, 'money') and database.getObject(member, -200) >= database.getItemDB(item, 'credits'):
                    database.removeObject(member, -100, database.getItemDB(item, 'money'))
                    database.removeObject(member, -200, database.getItemDB(item, 'credits'))
                    database.setHome(member,'floor', int(item))
                    await message.edit('<@'+str(member)+'> just changed their flooring to `'+str(database.getItemDB(item, 'emoji'))+' '+str(database.getItemDB(item, 'name')).title()+'`')
            elif database.getObject(member, -100) >= database.getItemDB(item, 'money') and database.getObject(member, -200) >= database.getItemDB(item, 'credits'):
                database.removeObject(member, -100, database.getItemDB(item, 'money'))
                database.removeObject(member, -200, database.getItemDB(item, 'credits'))
                database.addObject(member, item, 1)
                await message.edit('<@'+str(member)+'> just bought 1 `'+str(database.getItemDB(item, 'emoji'))+' '+str(database.getItemDB(item, 'name')).title()+'`')

            elif database.getObject(member, -100) <= database.getItemDB(item, 'money') and database.getObject(member, -200) <= database.getItemDB(item, 'credits'):
                await message.edit('<@'+str(member)+'> is missing `' +database.money+' '+ str(database.getItemDB(item, 'money')-database.getObject(member, -100)) +'` and `' +database.credit +' ' + str(database.getItemDB(item, 'credits')-database.getObject(member, -200)) + '` to buy `' + database.getItemDB(item, 'emoji')+' '+database.getItemDB(item, 'name').title() + '`')
            elif database.getObject(member, -100) <= database.getItemDB(item, 'money'):
                await message.edit('<@'+str(member)+'> is missing `' +database.money + ' ' + str(database.getItemDB(item, 'money')-database.getObject(member, -100)) + '` to buy `' + database.getItemDB(item, 'emoji')+' '+database.getItemDB(item, 'name').title() + '`')
            elif database.getObject(member, -200) <= database.getItemDB(item, 'credits'):
                await message.edit('<@'+str(member)+'> is missing `' +database.credit + ' ' + str(database.getItemDB(item, 'credits')-database.getObject(member, -200)) + '` to buy `' + database.getItemDB(item, 'emoji')+' '+database.getItemDB(item, 'name').title() + '`')
    

    # Handle paginated category views
    for category in ["GENERAL", "FURNITURE", "FLOORING", "WALLPAPER", "CUSTOM"]:
        if event.interaction.custom_id != "store":
            if event.interaction.custom_id.split('_')[1] == category:
                category_id = {"GENERAL":1, "FURNITURE":2, "FLOORING":6, "WALLPAPER":5, "CUSTOM":7}[category]
                items = {k:v for k,v in itemdb.items() 
                        if v['category'] == category_id and v['forsale']}
                
                components = create_paginated_menu(items, category=category)
                await event.interaction.create_initial_response(7, components=components, attachment=await imageprocessing.GetPocket(member, event.interaction.values[0].split('_')[0]) if event.interaction.values else hikari.undefined.UNDEFINED)
                return

    if event.interaction.custom_id.endswith("_ROOMUPGRADES_"):
        valid_upgrades = {}
        house_type = database.getHome(member)['huistype']
        
        valid_ids = upgrade_paths.get(house_type, [])
        valid_upgrades = {k:v for k,v in itemdb.items() 
                         if k in valid_ids and v['forsale']}
        
        components = create_paginated_menu(valid_upgrades, category="ROOMUPGRADES")
        await event.interaction.create_initial_response(7, components=components, attachment=await imageprocessing.GetPocket(member, event.interaction.values[0].split('_')[0]) if event.interaction.values else hikari.undefined.UNDEFINED)
        return

    if event.interaction.custom_id.endswith("_CRIB_"):
        row1 = hikari.impl.MessageActionRowBuilder()
        row2 = hikari.impl.MessageActionRowBuilder() 
        row3 = hikari.impl.MessageActionRowBuilder()

        row2.add_interactive_button(hikari.ButtonStyle.PRIMARY, "store_FURNITURE_", label='Furniture')
        row2.add_interactive_button(hikari.ButtonStyle.PRIMARY, "store_ROOMUPGRADES_", label='Room Upgrades')
        row3.add_interactive_button(hikari.ButtonStyle.PRIMARY, "store_FLOORING_", label='Flooring')
        row3.add_interactive_button(hikari.ButtonStyle.PRIMARY, "store_WALLPAPER_", label='Wallpaper')
        row1.add_interactive_button(hikari.ButtonStyle.PRIMARY, "store", label='Back')

        await event.interaction.create_initial_response(7, components=[row1,row2,row3])
        await message.edit(attachment=await imageprocessing.GetStoreCrib(member))
        return

    # Main store menu
    row1 = hikari.impl.MessageActionRowBuilder()
    row2 = hikari.impl.MessageActionRowBuilder()
    row3 = hikari.impl.MessageActionRowBuilder()
    row4 = hikari.impl.MessageActionRowBuilder()
    
    row2.add_interactive_button(hikari.ButtonStyle.PRIMARY, "store_GENERAL_", label='General & Supplies')
    row2.add_interactive_button(hikari.ButtonStyle.SECONDARY, "store_GEAR_", label='Gear')
    row3.add_interactive_button(hikari.ButtonStyle.PRIMARY, "store_CRIB_", label='Your Crib')
    row3.add_interactive_button(hikari.ButtonStyle.SECONDARY, "store_DARKMARKET_", label='Dark Market')
    row4.add_interactive_button(hikari.ButtonStyle.PRIMARY, "store_CUSTOM_", label='Customization')
    row1.add_interactive_button(hikari.ButtonStyle.PRIMARY, "homemenu", label='Back')

    await event.interaction.create_initial_response(7, components=[row1,row2,row3,row4])
    await message.edit(attachment=await imageprocessing.GetStore(member))

async def handle_beg(event, member, message):
    row3 = hikari.impl.MessageActionRowBuilder()
    
    row3.add_interactive_button(hikari.ButtonStyle.PRIMARY, "activities", label='Back')
    row3.add_interactive_button(hikari.ButtonStyle.PRIMARY, "beg"+'_BEG_', label='🤲 Beg 🤲')
    r = [row3]
    

    await event.interaction.create_initial_response(7, components=r)
    if str(event.interaction.custom_id).endswith("_BEG_"):
        if database.getStat(member, "lastbeg") + datetime.timedelta(seconds=30) <= datetime.datetime.now():
            
            #The more you beg the higher the chance of getting nothing
            if database.getStat(member, "lastbeg") + datetime.timedelta(seconds=2400) <= datetime.datetime.now():
                beg = database.getStat(member, "beg") - int(
                    ((datetime.datetime.now() - database.getStat(member, "lastbeg")).total_seconds() / 2400))
                if beg <= 0:
                    beg = 0
                if beg >= 50:
                    beg = 50
                    beg = database.getStat(member, "beg") - int(
                        ((datetime.datetime.now() - database.getStat(member, "lastbeg")).total_seconds() / 2400))
                database.setStat(member, "beg", beg)
            else:
                beg = database.getStat(member, "beg")
                beg = beg + 1
                if beg < 50:
                    if beg > 10:
                        beg = beg + 1
                    if beg > 20:
                        beg = beg + 2
                    if beg > 40:
                        beg = beg + 3

                database.setStat(member, "beg", beg)

            things = [0, 1, 2, 5, 10, 15, 25, 50]
            chance = [25 + ((database.getStat(member, "beg") * 2)), 33, 25, 17, 10, 7, 3, 1]
            winst = random.choices(things, chance, k=1000)
            rtype = random.randint(0, 100)
            if winst[0] == 0:
                database.setStat(member, "lastbeg", datetime.datetime.now())
                await message.edit("<@"+str(member)+"> received no rewards from begging.", attachment=await imageprocessing.GetBegging(member))
                return
            elif rtype <= 25:
                database.addObject(member, -200, int(math.ceil(winst[0]/2)))
                database.setStat(member, "allcredits", int(database.getStat(member, "allcredits") + int(math.ceil(winst[0]/2))))
                database.setStat(member, "lastbeg", datetime.datetime.now())
                await message.edit(fake.name()+" gave <@"+str(member)+"> "+database.price(int(math.ceil(winst[0]/2)),"credit")+' for their performance.', attachment=await imageprocessing.GetBegging(member))
                return
            elif rtype > 99:
                database.removeObject(member, -100, database.getObject(member, -100))
                await message.edit("You have been robbed from all your `"+database.money+'`.', attachment=await imageprocessing.GetBegging(member))
                return
            else:
                database.addObject(member, -100, winst[0])
                database.setStat(member, "lastbeg", datetime.datetime.now())
                await message.edit(f"{fake.name()} gave <@{str(member)}> `{database.money} {winst[0]}` for their performance.", attachment=await imageprocessing.GetBegging(member))
                return
    
    await message.edit(attachment=await imageprocessing.GetBegging(member))

async def handle_stop(event, member, message):
    await event.interaction.create_initial_response(7, components=[])
    await event.interaction.delete_initial_response()

async def handle_main_menu(event, member, message = None):
    print(database.isHarvestable(member))
    try:
        rows = hikari.impl.MessageActionRowBuilder()
    except:
        rows = event.rest.build_message_action_row()

    if (database.getStat(member, "harvest") == 1 and database.getStat(member, "lastharvest") + datetime.timedelta(hours=4) <= datetime.datetime.now()):
        rows.add_interactive_button(hikari.ButtonStyle.SUCCESS, "yourcrib", label='Your Crib')
    else:
        rows.add_interactive_button(hikari.ButtonStyle.PRIMARY, "yourcrib", label='Your Crib')
    rows.add_interactive_button(hikari.ButtonStyle.PRIMARY, "activities", label='Activities')
    if (database.getStat(member, 'lastdaily') <= (datetime.datetime.now() - datetime.timedelta(days = 1))):
        rows.add_interactive_button(hikari.ButtonStyle.SUCCESS, "quests", label='Quests')
    else:
        rows.add_interactive_button(hikari.ButtonStyle.PRIMARY, "quests", label='Quests')

    try:
        rows2 = hikari.impl.MessageActionRowBuilder()
    except:
        rows2 = event.rest.build_message_action_row()

    rows2.add_interactive_button(hikari.ButtonStyle.SECONDARY, "profile", label='Profile', is_disabled=True)
    rows2.add_interactive_button(hikari.ButtonStyle.SECONDARY, "hiscores", label='Hi-Scores', is_disabled=True)
    rows2.add_interactive_button(hikari.ButtonStyle.PRIMARY, "pocket", label='Pocket')

    try:
        rows3 = hikari.impl.MessageActionRowBuilder()
    except:
        rows3 = event.rest.build_message_action_row()

    rows3.add_interactive_button(hikari.ButtonStyle.PRIMARY, "store", label='Store')
    rows3.add_interactive_button(hikari.ButtonStyle.PRIMARY, "settings", label='Settings')
    rows3.add_interactive_button(hikari.ButtonStyle.DANGER, "stop", label='Stop')
    if type(event) == tanjun.context.slash.SlashContext:
        message = await event.interaction.edit_initial_response("Hi "+event.interaction.member.display_name+"!", attachment=await imageprocessing.GetPhoneMenu(member), components=[rows, rows2, rows3])
    else:
        message = await event.interaction.create_initial_response(7, attachment=await imageprocessing.GetPhoneMenu(member), components=[rows, rows2, rows3])
    return message

async def handle_remove_menu(event, member, message):
    if event.interaction.custom_id.endswith("_ESC_"):
        string = re.sub(
            r'^.*?_', '', str(event.interaction.custom_id[:-5]))

        itemid = int(string.split("_", 1)[0])
        rowid = int(string.split("_", 1)[1].split("_", 1)[0])
        colid = int(string.split("_", 1)[1].split("_", 1)[1])
        roomlayout = np.asarray((database.getHomeLayout(member)))
        harvesttimerlayout = np.asarray(database.getHarvestTimer(member))
        print(harvesttimerlayout)
        if roomlayout[rowid][colid] == itemid:
            plantsdb = database.getItemsIDByBehaviour('420')
            storagedb = database.getItemsIDByBehaviour('STR')
            plants = 0
            for i in roomlayout:
                for e in i:
                    if e in plantsdb:
                        plants += 1

            # Check if there are still plants left if 1 disable harvest ability
            if plants == 1 and itemid in plantsdb:
                database.setStat(
                    member, 'harvest', False)
                harvesttimerlayout[rowid][colid] = datetime.datetime.max
                database.setHome(member, 'harvesttimer', harvesttimerlayout.flatten().tolist())

            # Check if storage is empty enough to be able to pickup
            database.setHomeLayout(
                member, (colid, rowid), -1)
            database.addObject(member, itemid, 1)
            await message.edit("<@"+str(member)+"> removed a `"+database.getItemName(itemid)+'` from his crib.', attachment= await imageprocessing.GetPhoneHome(member))
    
    roomlayout = np.asarray(np.fliplr(database.getHomeLayout(member)))
    collength = 0
    rows = []
    row1 = hikari.impl.MessageActionRowBuilder()
    row2 = hikari.impl.MessageActionRowBuilder()
    row3 = hikari.impl.MessageActionRowBuilder()
    row4 = hikari.impl.MessageActionRowBuilder()
    row5 = hikari.impl.MessageActionRowBuilder()
    row5.add_interactive_button(hikari.ButtonStyle.PRIMARY, "yourcrib" , label='Back')
    for i in roomlayout:
        rowlenght = len(i) - 1
        rows_map = {
            0: row1,
            1: row2, 
            2: row3,
            3: row4,
            4: row5
        }

        for e in i:
            current_row = rows_map[collength]
            
            if e != -1:
                current_row.add_interactive_button(
                hikari.ButtonStyle.DANGER,
                f"remove_{e}_{collength}_{rowlenght}_ESC_",
                label=database.getItemDB(e, 'emoji')
            )
            else:
                current_row.add_interactive_button(
                hikari.ButtonStyle.SECONDARY, 
                f"yourcrib_{e}_{collength}_{rowlenght}",
                label='🛑',
                is_disabled=True
            )
            rowlenght -= 1

        if collength == 0:
            rows.append(row1)
        elif collength < 4:
            rows.append(rows_map[collength])
            
        collength += 1
    rows.append(row5)

    await event.interaction.create_initial_response(7, components=rows)

@component.with_command
@tanjun.as_slash_command("king", "Connect to the Kingpin Network.")
async def king_command(ctx: tanjun.abc.SlashContext) -> None:
    #Get the member id and the message id to clear fishing channel if in use by user
    try:
        member = ctx.author.id
        message = await ctx.rest.fetch_message(message=message_ids[ctx.member.id], channel=message_ids[str(ctx.author.id)+"channel"])
        fishingchannel = database.fishingchannels[message.channel_id]
        if message.channel_id in database.fishingchannels:
            for x, i in enumerate(fishingchannel):
                for y, b in enumerate(i):
                    if database.fishingchannels[message.channel_id][x][y] == member:
                        database.fishingchannels[message.channel_id][x][y] = 0
    except:
        pass

    #If user is not registered, show registration screen else show main menu
    if (database.checkIfUserExists(member) == False):
        row = ctx.rest.build_message_action_row()
        row.add_interactive_button(hikari.ButtonStyle.PRIMARY, "register", label="Connect")
        row.add_interactive_button(hikari.ButtonStyle.DANGER, "stop", label="Cancel")
        await ctx.create_initial_response("Hi "+ctx.member.display_name+", Welcome to the Kingpin Network!", components=[row], attachment=await imageprocessing.registerUser())
        message = await ctx.fetch_initial_response()
    else:
        message = await handle_main_menu(ctx, member)

    logger.info('New interface opened, Messageid: '+ str(message.id) + ", channelid: " + str(message.channel_id))
        
    #Check if the user has message with UI open, if so delete old message
    if ctx.author.id in message_ids:
        try:
            oldmessage = await ctx.rest.fetch_message(message=message_ids[ctx.member.id], channel=message_ids[str(ctx.author.id)+"channel"])
            await oldmessage.delete()
            logger.info('Deleted Old Interface, Messageid: '+ str(message_ids[member]) + ", channelid: " + str(message_ids[str(ctx.author.id)+"channel"]))
        except:
            pass

    #Write message ids to message_ids to track which message to delete in future
    message_ids[ctx.author.id] = message.id
    message_ids[str(ctx.author.id)+"channel"] = message.channel_id

    #write message ids to file in case of bot going offline
    with open('messages.pkl', 'wb') as f:
        pickle.dump(message_ids, f, pickle.HIGHEST_PROTOCOL)

    
    



load_slash = component.make_loader()