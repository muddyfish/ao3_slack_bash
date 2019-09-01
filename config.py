import yaml


class Config:
    def __init__(self, config):
        self.config = config

    @classmethod
    def from_file(cls, config_name="config.yaml"):
        with open(config_name) as conf_file:
            return Config(yaml.load(conf_file, Loader=yaml.SafeLoader))

    @property
    def bot_token(self):
        return self.config["bot"]

    @property
    def commands(self):
        return self.config["commands"]

    @property
    def prefix(self):
        return self.config["prefix"]
