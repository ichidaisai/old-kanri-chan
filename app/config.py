import yaml

def getToken():
    with open('config.yml') as file:
        obj = yaml_safe_load(file)
        token = obj['DISCORD_TOKEN']
    return token