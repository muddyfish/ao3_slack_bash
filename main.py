import asyncio
import re

from aiohttp import ClientSession
import slack
from slack.events import Message
from slack.io.aiohttp import SlackAPI

from config import Config

mention = re.compile(r"<@([A-Za-z0-9]+)>")


class SlackBot:
    def __init__(self, config_file: str = "config.yaml"):
        self.config = Config.from_file(config_file)

        session = ClientSession()
        self.slack_client = SlackAPI(token=self.config.bot_token, session=session)

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
        pass

    async def run_cmd(self, command, message: Message):
        pass

    async def run_command(self, command, message: Message):
        await self.command_types[command["type"]](command, message)

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
                if not event.event["text"].startswith(self.prefix):
                    continue
                command = event.event["text"].replace(self.prefix, "", 1).split(" ", 1)[0]
                if command in self.commands:
                    await self.run_command(self.commands[command], event.event)


if __name__ == "__main__":
    bot = SlackBot()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.run())
