# -*- coding: utf-8 -*-

import yaml
from os.path import exists

def getToken():
    with open('config.yml') as file:
        obj = yaml.safe_load(file)
        token = obj['DISCORD_TOKEN']
    return token

def checkConfig():
    flag = True

    if exists('./config.yml'):
        with open('config.yml') as file:
            obj = yaml.safe_load(file)
            
            # 型チェック
            if obj is None:
                flag = False
            else:
                # トークンが指定されているか？
                if 'DISCORD_TOKEN' not in obj:
                    flag = False
                elif obj['DISCORD_TOKEN'] == '':
                    flag = False
                else:
                    pass

    # config.yml が存在しない
    else:
        flag = False

    return flag