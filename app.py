import os
import time
import threading
import requests

from flask import Flask, request, after_this_request, Response
from flask_discord_interactions import Context, DiscordInteractions, Role, Member
from apig_wsgi import make_lambda_handler

from zappa.asynchronous import task

import botocore

import json
import jsonpickle

from server_startup import Server
import params

app = Flask(__name__)
discord = DiscordInteractions(app)

server = Server(params.ec2_params)

app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]

import logging

logging.basicConfig


@app.route("/")
def index():
    return "Hello, world!", 200


@discord.command()
def ping(ctx):
    "Respond with a friendly 'pong'!"
    # breakpoint()
    if os.getenv("LOCAL"):
        thread = threading.Thread(target=delayed_task, args=[(jsonpickle.encode(ctx))])
        thread.start()
    else:
        delayed_task(jsonpickle.encode(ctx))
    # print("Hi")
    return "Pong!"


@task
def delayed_task(ctx_json):
    ctx = jsonpickle.decode(ctx_json)
    time.sleep(1)
    ctx.send("bonus pong!")


@discord.command()
def hello(
    ctx,
    name: str = "you dummy, you forgot to include a name for me to say back, you moron, you absolute nonce",
):
    "Have the bot say hello!"
    return f"Hello, {name}"


@discord.command()
def start(ctx):
    """
    Starts minecraft server (if one isn't yet running).
    """
    #     - Will print ip in chat.
    # - Requires discord role mc_auth (ask dint)

    # if "mc_auth" in [role.name for role in ctx.author.roles]:
    if server.instance:
        return "Server already running at {ip}".format(
            ip=server.instance.public_ip_address
        )
    else:
        if os.getenv("LOCAL"):
            thread = threading.Thread(
                target=start_server, args=[jsonpickle.encode(ctx)]
            )
            thread.start()
        else:
            start_server(jsonpickle.encode(ctx))

        return "Starting server"


@task
def start_server(ctx_json):
    ctx = jsonpickle.decode(ctx_json)
    try:
        logging.info("Starting server")
        server.start_instance()
        ctx.send(
            f"Server running at {server.instance.public_ip_address}. It'll likely take a few minutes for Minecraft to be available at that ip - just keep retrying it in ur client 🤗"
        )
    except Exception as e:
        ctx.send(
            "Problem with Amazon. Bug aaron with this error message: \n > {} \n Cancelling server startup....".format(
                str(e)
            )
        )
        try:
            server.terminate()
            ctx.send("Server startup cancelled.")
        except Exception as e:
            logging.debug(f"Couldn't terminate server:\n{e}")
            ctx.send(f"Couldn't terminate server:\n{e}")

    return {}


@discord.command()
def stop(ctx):
    """
    Stops minecraft server (if running).
    """
    # - Requires discord role mc_auth (ask dint)

    # todo: gracefully stop server. ie run save-all & stop in
    # mc

    # if "mc_auth" in [role.name for role in ctx.author.roles]:
    # todo: figure out a way to get role name :/

    if not server.instance:
        return "No server running."
    else:
        if os.getenv("LOCAL"):
            thread = threading.Thread(target=stop_server, args=[jsonpickle.encode(ctx)])
            thread.start()
        else:
            stop_server(jsonpickle.encode(ctx))
        return "Stopping server"
    # else:
    #     return "Not authorized!"


@task
def stop_server(ctx_json):
    ctx = jsonpickle.decode(ctx_json)
    print("stopping server")
    try:
        server.terminate()
        ctx.send("Server stopped")
    except Exception as e:
        ctx.send(f"Couldn't stop server:\n{e}")

    return {}


discord.set_route("/interactions")

if __name__ == "__main__":
    discord.update_slash_commands(guild_id=os.environ["GUILD_ID"])
