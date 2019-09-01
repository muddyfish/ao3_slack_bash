import asyncio
import re
import subprocess

from aiohttp import ClientSession
import slack
from slack.events import Message
from slack.io.aiohttp import SlackAPI

from config import Config

mention = re.compile(r"<@([A-Za-z0-9]+)>")


class SlackBot:
    def __init__(self, loop, config_file: str = "config.yaml"):
        self.loop = loop
        self.config = Config.from_file(config_file)

        self.session = ClientSession()
        self.slack_client = SlackAPI(token=self.config.bot_token, session=self.session)
        self.waiters = []

        self.commands = self.config.commands
        self.prefix = self.config.prefix
        self.command_types = {
            "get_id": self.get_id,
            "read_web": self.read_web,
            "run_cmd": self.run_cmd
        }

    async def run(self):
        print("Running")
        await self.rtm()

    async def get_id(self, command, message: Message):
        text = message["text"]
        mentioned_ids = re.findall(mention, text)
        await self.send_message(message["channel"], " ".join(mentioned_ids))

    async def read_web(self, command, message: Message):
        async with self.session.get(command["url"]) as resp:
            resp = await resp.text()
        await self.send_message(message["channel"], resp)

    async def run_cmd(self, command, message: Message):
        output = subprocess.run(command["cmd"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if command["display_output"]:
            resp = (f"```\n{output.stdout.decode().strip()}\n```" if output.stdout else "") + \
                   (f"```\n{output.stderr.decode().strip()}\n```" if output.stderr else "")
            await self.send_message(message["channel"], resp)

    async def run_command(self, command, message: Message):
        channel = message["channel"]
        if "acl1" in command:
            if not command["acl1"] or message["user"] not in command["acl1"]:
                return await self.send_message(channel, "You are not in the acl list for this command.")
        if "reply1" in command:
            await self.send_message(channel, command["reply1"])
        if "acl2" in command and command["acl2"]:
            message2 = await self.wait_for_message(f"{self.prefix}{command['trigger2']}", timeout=command["timeout"])
            if message2 is None:
                return await self.send_message(channel, "Timed out.")
            if message2["user"] not in command["acl2"]:
                return await self.send_message(channel, "You are not in the acl list for this command.")
            if message2["user"] == message["user"]:
                return await self.send_message(channel, "The authorising user cannot be the initiating user.")
            if "reply2" in command:
                await self.send_message(channel, command["reply2"])

        await self.command_types[command["type"]](command, message)

        if "complete" in command:
            await self.send_message(channel, command["complete"])

    async def wait_for_message(self, text: str, timeout: int) -> Message:
        future = loop.create_future()
        check = lambda event: event.event["text"] == text
        self.waiters.append((future, check))
        try:
            event = await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            return None
        return event

    async def send_message(self, channel: str, response: str):
        await self.slack_client.query(
            slack.methods.CHAT_POST_MESSAGE,
            data={
                "channel": channel,
                "text": response,
            })

    async def rtm(self):
        async for event in self.slack_client.rtm():
            if isinstance(event, Message):
                for future, check in self.waiters:
                    if check(event):
                        future.set_result(event)

                if not event.event["text"].startswith(self.prefix):
                    continue
                command = event.event["text"].replace(self.prefix, "", 1).split(" ", 1)[0]
                if command in self.commands:
                    asyncio.ensure_future(self.run_command(self.commands[command], event.event))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    bot = SlackBot(loop)
    loop.run_until_complete(bot.run())
