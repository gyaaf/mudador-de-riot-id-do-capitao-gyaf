from lcu_driver import Connector
import json

connector = Connector()

async def change(connection):
    name = input('Digite o nick:\n')
    tag = input('Digite a #:\n')
    data = {"gameName": name, "tagLine": tag}
    request = await connection.request('post', '/lol-summoner/v1/save-alias', json=data)
    response = await request.json()
    print(response)

@connector.ready
async def connect(connection):
    print('mudador de riot id do capitao gyaf')
    await change(connection)

connector.start()

input()
