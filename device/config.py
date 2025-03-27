import configparser

config = None


def load_config(config_file="config.ini"):
    global config
    config = configparser.ConfigParser()
    config.read(config_file)


def get_config():
    global config
    if config is None:
        load_config()
    return config


def set_config(_config):
    global config
    config = config
    with open("config.ini", "w") as f:
        config.write(f)
