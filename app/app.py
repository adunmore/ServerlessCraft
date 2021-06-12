import os
import time
import threading
import multiprocessing

from flask import Flask, request
from flask_discord_interactions import DiscordInteractions, Role
from apig_wsgi import make_lambda_handler

import botocore

from server_startup import Server
import params

app = Flask(__name__)
discord = DiscordInteractions(app)


app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]


@discord.command()
def ping(ctx, role: Role):
    "Respond with a friendly 'pong'!"
    # breakpoint()

    def do_followup():
        time.sleep(5)
        ctx.send("(bonus pong)")

    thread = threading.Thread(target=do_followup)
    thread.start()
    return "Pong!"


@discord.command()
def hello(ctx, name: str = "Aaron"):
    "Have the bot say hello!"
    return f"Hello, {name}"


server = Server(params.ec2_params)


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

        def start_server():
            try:
                print("starting server!")
                server.start_instance()
                ctx.send(
                    "Server running at {ip}".format(
                        ip=server.instance.public_ip_address
                    )
                )
            except botocore.exceptions.ClientError as e:
                server.instance.terminate()
                ctx.send(
                    "Problem with Amazon. Bug aaron with this error message: \n > {} \n Server startup canceled.".format(
                        str(e)
                    )
                )

        thread = threading.Thread(target=start_server)
        thread.start()
        return "Starting server"


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

        def stop_server():
            print("stopping server")
            server.instance.terminate()
            ctx.send("Server stopped")

        thread = threading.Thread(target=stop_server)
        thread.start()

        return "Stopping server"
    # else:
    #     return "Not authorized!"


discord.set_route("/interactions")

# discord.update_slash_commands(guild_id=os.environ["GUILD_ID"])

handler = make_lambda_handler(app)

if __name__ == "__main__":
    app.run()
