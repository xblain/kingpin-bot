![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Discord](https://img.shields.io/discord/801694163568951296)
![License](https://img.shields.io/github/license/xblain/kingpin-bot)

![Logo](https://github.com/xblain/kingpin-bot/blob/main/readme-images/BotLogoWord.svg)

# Kingpin

A feature-rich Discord economy bot with a modern GUI interface, controlled through an intuitive single slash command. Built with Python using Hikari-Discord and Tanjun libraries, featuring a PostgreSQL database and a Django-powered dashboard with OAuth authentication.

## Core Features

🎮 **User Experience**
- Sleek GUI interface controlled by a single slash command
- Personal "Kingpin Phone" interface for each user with built-in notification system
- Cross-server economy system
- [Web dashboard for administration](https://github.com/xblain/kingbin-webui/tree/main)

🏠 **Player Activities**
- Build and customize your personal crib
- Beg to gain money and other rewards
- Grow plants within your own crib
- Engage in multiplayer fishing
- Rob other players
- Complete quests for rewards

## Project Status

This project started as a learning exercise during the COVID-19 pandemic and has evolved into a more comprehensive Discord bot. Currently undergoing major improvements and optimizations. Some functionality is still missing from the original text bot. Due to improper backup management in the past, all database functionality was lost but has since been fully remade with improved systems.

✅ **Recent Achievements**
- Updated to Python 3.12+
- Restored and improved most core functionality (components/kingpin/phone.py)
- Enhanced UI elements
- Rebuilt database infrastructure

## Screenshots

|![Shop](https://github.com/xblain/kingpin-bot/blob/main/readme-images/shop.png)|![Menu](https://github.com/xblain/kingpin-bot/blob/main/readme-images/menu.png)|![Activities](https://github.com/xblain/kingpin-bot/blob/main/readme-images/activities.png)|
|     :---:      |     :---:      |     :---:      |
|![Crib](https://github.com/xblain/kingpin-bot/blob/main/readme-images/crib.png)|![Itemview](https://github.com/xblain/kingpin-bot/blob/main/readme-images/itemview.png)|![Beg](https://github.com/xblain/kingpin-bot/blob/main/readme-images/beg.png)|
|![Upgrade1](https://github.com/xblain/kingpin-bot/blob/main/readme-images/upgradeplant.png)|![Upgrade2](https://github.com/xblain/kingpin-bot/blob/main/readme-images/upgradesafe.png)|![Fishing](https://github.com/xblain/kingpin-bot/blob/main/readme-images/fishing.png)|

## Development Roadmap

🔧 **Optimization Phase**
- [ ] Streamline and optimize main phone component
- [ ] Migrate from psycopg2 to asyncpg
- [ ] Implement database connection pooling
- [ ] Optimize and refactor database
- [ ] Optimize image generation system
- [ ] Implement caching for Discord API and image generation

🎮 **New Features**
- [ ] Enhanced quest system
- [ ] Implement per server customization (network name, currency emoji's, server specific items)
- [ ] Custom emoji's
- [ ] Improve user onboarding
- [ ] Combat equipment system
- [ ] Enterprise management
- [ ] Job system
- [ ] World exploration and territory control

🖥️ **Dashboard**
- [ ] Streamline Django views and templates
- [ ] Enhance user interface

## Community

Join our Discord community to follow the development progress:
https://discord.gg/6pjZQfwzf7

## Author

[@xblain](https://github.com/xblain)

