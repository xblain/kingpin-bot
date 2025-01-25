# -*- coding: utf-8 -*-
# cython: language_level=3
import tanjun
import time

component = tanjun.Component()


@component.with_command
@tanjun.with_owner_check()
@tanjun.as_message_command("ping")
async def ping(ctx: tanjun.abc.Context, /) -> None:
    start_time = time.perf_counter()
    await ctx.respond(content="PING")
    time_taken = (time.perf_counter() - start_time) * 1_000
    heartbeat_latency = ctx.shards.heartbeat_latency * 1_000 if ctx.shards else float("NAN")
    await ctx.edit_last_response(f"PONG\n - REST: {time_taken:.0f}ms\n - Gateway: {heartbeat_latency:.0f}ms")

@component.with_command
@tanjun.with_owner_check()
@tanjun.with_argument("module_name", converters=str)
@tanjun.as_message_command("reload_module", "Reloads a module.")
async def reload_module(ctx: tanjun.abc.SlashContext, module_name: str, client: tanjun.Client = tanjun.injected(type=tanjun.Client)):
    try:
        client.reload_modules('components.kingpin.'+module_name)
    except ValueError:
        client.load_modules('components.kingpin.'+module_name)

    await client.declare_global_commands()
    await ctx.respond("Reloaded!")


@component.with_command
@tanjun.with_owner_check()
@tanjun.with_argument("module_name", converters=str)
@tanjun.as_message_command("unload_module", "Removes a module.")
async def unload_module(ctx: tanjun.abc.SlashContext, module_name: str, client: tanjun.Client = tanjun.injected(type=tanjun.Client)):
    try:
        client.unload_modules('components.kingpin.'+module_name)
    except ValueError:
        await ctx.respond("Couldn't unload module...")
        return

    await client.declare_global_commands()
    await ctx.respond("Unloaded!")

@component.with_command
@tanjun.with_owner_check()
@tanjun.with_argument("module_name", converters=str)
@tanjun.as_message_command("load_module", "Loads a module.")
async def load_module(ctx: tanjun.abc.SlashContext, module_name: str, client: tanjun.Client = tanjun.injected(type=tanjun.Client)):
    try:
        client.load_modules('components.kingpin.'+module_name)
    except ValueError:
        await ctx.respond("Can't find that module!")
        return

    await client.declare_global_commands()
    await ctx.respond("Loaded!")

@tanjun.as_loader
def load_examples(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
