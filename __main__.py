import hikari

import tanjun
import config

# This is the main entry point for the bot, it will load the configuration, create the bot, and run it.
def run() -> hikari.GatewayBot:
    loaded_config = config.KingConfig.load()
    bot = hikari.GatewayBot(loaded_config.bot_token,intents=hikari.Intents.ALL)

    # TODO - implement and inject the database dependency into Tanjun

    (
        tanjun.Client.from_gateway_bot(bot, declare_global_commands=801694163568951296, mention_prefix=True)
        .load_modules("components.kingpin.phone")
        .load_modules("components.kingpin.admin")
        .add_prefix(loaded_config.prefix)
        #.set_type_dependency(config.ExampleConfig, loaded_config)
        #.set_type_dependency(protos.DatabaseProto, database)
        # Here we use client callbacks to manage the database, STOPPING can also be used to stop it.
        #.add_client_callback(tanjun.ClientCallbackNames.STARTING, database.connect)
    )
    bot.run()
    



if __name__ == "__main__":
    run()
