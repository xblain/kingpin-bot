
![Logo](https://github.com/xblain/kingpin-bot/blob/main/readme-images/BotLogoWord.svg)


# Kingpin

A discord economy bot with GUI and controlled by a single slash command, created in Python, built on top of Hikari-Discord and Tanjun libraries. Database built with PostgreSQL, Dashboard built with Django with OAuth authentification

- Very much WIP, this was a old project of mine which was a learning exercise for me to learn more about Python, over time I've learned more and this repository is for me to update, optimize and improve my code from many years ago.
- ~~Part of the functionality is also broken due to my abandoment of the project and not keeping backups of everything that was needed to keep the bot working~~ (Functionality that was lost has been fully restored and many improvements to UI have been implemented, currently I only need to implement the functionality that was in the text version of the bot such as enterprises activity, money safes, trading, etc, but optimization and code improvements have priority as of now before expanding current existing systems and creating new systems)

## Features

- Web dashboard for database and server management
- Build and customize your own crib and view it easily within the Kingpin UI
- Grow plants, rob other players and multiple other ways to generate income
- Customize your own kingpin phone and show of your wealth to other people on Discord
- Multiplayer fishing
- Cross-server Economy
- Quest system
- ~~Customization per server~~


## Authors

- [@xblain](https://github.com/xblain)


## Screenshots


|![Shop](https://github.com/xblain/kingpin-bot/blob/main/readme-images/shop.png)|![Menu](https://github.com/xblain/kingpin-bot/blob/main/readme-images/menu.png)|![Activities](https://github.com/xblain/kingpin-bot/blob/main/readme-images/activities.png)|
|     :---:      |     :---:      |     :---:      |
|![Crib](https://github.com/xblain/kingpin-bot/blob/main/readme-images/crib.png)|![Itemview](https://github.com/xblain/kingpin-bot/blob/main/readme-images/itemview.png)|![Beg](https://github.com/xblain/kingpin-bot/blob/main/readme-images/beg.png)|
|![Upgrade1](https://github.com/xblain/kingpin-bot/blob/main/readme-images/upgradeplant.png)|![Upgrade2](https://github.com/xblain/kingpin-bot/blob/main/readme-images/upgradesafe.png)|![Fishing](https://github.com/xblain/kingpin-bot/blob/main/readme-images/fishing.png)|


## Roadmap
Repairs and Optimizations:

- [x] Fix and recreate database up to previous state
- [x] Repair all functionality to previous state
- [ ] Optimize the main component (components/kingpin/phone.py) as it was built pretty sloppy. Currently this is progressing very well :+1:
- [ ] Move database code from psycopg2 to asyncpg for async functionality. Optimize code, implement query batching and reduce similar functions.
- [ ] Implement database connection pooling and ability to reconnect when connection lost
- [ ] Optimize imageprocessing component and possibly seperate it from main project to split load

Implement Systems:

- [ ] Expand on quest system
- [ ] Combat equipment
- [ ] Implement enterprises
- [ ] In-game Job System
- [ ] Implement a world for players to explore with possible territories (Turf Wars) to take over

Dashboard:

- [ ] Clean up webdashboard django views, html pages, templates


## Community

Come check the progress of this bot in the community server:

https://discord.gg/6pjZQfwzf7

