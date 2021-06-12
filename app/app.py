import os

from flask import Flask, request
from flask_discord_interactions import DiscordInteractions
from apig_wsgi import make_lambda_handler

import botocore

from server_startup import Server
import params

app = Flask(__name__)
discord = DiscordInteractions(app)


app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]

server = Server(params.ec2_params)


@discord.command()
def ping(ctx):
    "Respond with a friendly 'pong'!"
    return "Pong!"


@discord.command()
def hello(ctx, name: str = "Aaron"):
    "Have the bot say hello!"
    return f"Hello, {name}"


@discord.command()
def start(self, ctx):
    """
    Starts minecraft server (if one isn't yet running).
    - Will print ip in chat.
    - Requires discord role mc_auth (ask dint)
    """
    if "mc_auth" in [role.name for role in ctx.author.roles]:
        if (
            server.instance
        ):  # this won't work: let's convert that to a property that checks the aws api for a matching instance
            await ctx.send(
                "Server already running at {ip}".format(
                    ip=self.server.instance.public_ip_address
                )
            )
        else:
            await ctx.send("Starting server")
            try:
                self.server.start_instance()
            except botocore.exceptions.ClientError as e:
                await ctx.send(
                    "Problem with Amazon. Bug aaron with this error message: \n > {} \n Server startup canceled.".format(
                        str(e)
                    )
                )
                self.server.instance.terminate()
                raise e
            await ctx.send(
                "Server running at {ip}".format(
                    ip=self.server.instance.public_ip_address
                )
            )


@discord.command()
def stop(self, ctx):
    """
    Stops minecraft server (if running).
    - Requires discord role mc_auth (ask dint)
    """

    # todo: gracefully stop server. ie run save-all & stop in
    # mc
    if "mc_auth" in [role.name for role in ctx.author.roles]:
        if not self.server.instance:
            await ctx.send("No server running.")
        else:
            await ctx.send("Stopping server")
            self.server.instance.terminate()
            await ctx.send("Server stopped")


discord.set_route("/interactions")

discord.update_slash_commands(guild_id=os.environ["GUILD_ID"])

handler = make_lambda_handler(app)

if __name__ == "__main__":
    app.run()
