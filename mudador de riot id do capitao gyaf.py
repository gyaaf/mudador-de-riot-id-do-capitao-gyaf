from lcu_driver import Connector
import json
import sys
import msvcrt


def get_single_char():
    """
    Captura um único caractere do terminal sem esperar por uma nova linha.
    """
    return msvcrt.getch().decode('utf-8')


def get_limited_input(prompt, limit):
    """
    Solicita ao usuário uma entrada de no máximo 'limit' caracteres.
    """
    print(prompt, end='', flush=True)
    user_input = []
    while True:
        char = get_single_char()
        if char == '\r' or char == '\n':  # Enter key
            print()
            break
        elif char == '\x08' or char == '\x7f':  # Backspace key
            if user_input:
                user_input.pop()
                sys.stdout.write('\b \b')
                sys.stdout.flush()
        elif len(user_input) < limit:
            user_input.append(char)
            sys.stdout.write(char)
            sys.stdout.flush()
    
    return ''.join(user_input)


connector = Connector()

async def change(connection):

    limitName = 16
    limitTag = 5


    name = get_limited_input('Digite o nick:\n', limitName)
    tag = get_limited_input('Digite a #:\n', limitTag)
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
