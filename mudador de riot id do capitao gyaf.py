import requests
import json
import webbrowser
import psutil
import base64
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def find_league_client_credentials():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if proc.info['name'] == 'LeagueClientUx.exe':
            cmdline = proc.info['cmdline']
            port = None
            token = None
            for arg in cmdline:
                if arg.startswith('--app-port='):
                    port = arg.split('=')[1]
                elif arg.startswith('--remoting-auth-token='):
                    token = arg.split('=')[1]
            if port and token:
                #print(f"Found credentials: port={port}, token={token}")
                return port, token
    return None, None

def find_riot_client_credentials():
    port = None
    token = None
    for process in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
        if 'Riot Client.exe' in process.info['name']:
            for arg in process.info['cmdline']:
                if '--remoting-auth-token=' in arg:
                    token = arg.split('=')[1]
                if '--app-port=' in arg:
                    port = arg.split('=')[1]
            if token and port:
                break
    #print (port, token)
    return port, token

def get_base_url(port):
    return f'https://127.0.0.1:{port}'

def multi_search(website, base_url, headers):
    try:
        champ_select_url = f'{base_url}/lol-champ-select/v1/session'
        #print(f"Requesting {champ_select_url}")
        champ_select = requests.get(champ_select_url, headers=headers, verify=False).text
        #print(f"champ_select response: {champ_select}")

        if champ_select and "RPC_ERROR" not in champ_select:
            champ_select_data = json.loads(champ_select)
            summ_names = []
            is_ranked = True

            if is_ranked:

                port, token = find_riot_client_credentials()
                base_url = get_base_url(port)
                auth = base64.b64encode(f'riot:{token}'.encode('utf-8')).decode('utf-8')
                headers = {
                    'Authorization': f'Basic {auth}',
                    'Content-Type': 'application/json'
                }
                summ_names = []
                riot_info_url = f'{base_url}/chat/v5/participants'
                #print(f"Requesting {riot_info_url}")
                riot_info = requests.get(riot_info_url, headers=headers, verify=False).text
                #print(f"Riot info response: {riot_info}")
                participants_data = json.loads(riot_info)

                if "participants" in participants_data:
                    for participant in participants_data["participants"]:
                        #print(participant)
                        if "champ-select" not in participant["cid"]:
                            continue
                        game_name = participant["game_name"]
                        game_tag = participant["game_tag"]
                        summ_names.append(f"{game_name}%23{game_tag}")

                region = ""
                if website == "U.GG":
                    auth_info_url = f'{base_url}/lol-rso-auth/v1/authorization'
                    #print(f"Requesting {auth_info_url}")
                    auth_info = requests.get(auth_info_url, headers=headers, verify=False).text
                    #print(f"Auth info response: {auth_info}")
                    region_data = json.loads(auth_info)
                    region = region_data["currentPlatformId"]
                else:
                    region_info_url = f'{base_url}/riotclient/region-locale'
                    #print(f"Requesting {region_info_url}")
                    region_info = requests.get(region_info_url, headers=headers, verify=False).text
                    #print(f"Region info response: {region_info}")
                    region_data = json.loads(region_info)
                    region = region_data["webRegion"]

                if region:
                    summ_names_str = ",".join(summ_names)
                    #print(f"Summoner names: {summ_names_str}")
                    if not summ_names_str:
                        return "Failed to get summoner names"

                    url = ""
                    if website == "OP.GG":
                        url = f"https://{region}.op.gg/multi/query={summ_names_str}"
                    elif website == "U.GG":
                        url = f"https://u.gg/multisearch?summoners={summ_names_str}&region={region.lower()}"
                    elif website == "PORO.GG":
                        url = f"https://poro.gg/multi?region={region.upper()}&q={summ_names_str}"
                    elif website == "Porofessor.gg":
                        url = f"https://porofessor.gg/pregame/{region.lower()}/{summ_names_str}"

                    webbrowser.open(url)
                    return url
                return "Failed to get region"
    except Exception as e:
        return str(e)
    return "Champion select not found"

def main():
    port, token = find_league_client_credentials()
    if not port or not token:
        print('Client está fechado.')
        return

    base_url = get_base_url(port)
    auth = base64.b64encode(f'riot:{token}'.encode('utf-8')).decode('utf-8')
    headers = {
        'Authorization': f'Basic {auth}',
        'Content-Type': 'application/json'
    }

    result = multi_search("Porofessor.gg", base_url, headers)
    print(result)

if __name__ == "__main__":
    print('''


  ▄████▓██   ██▓ ▄▄▄        █████▒▄▄▄       ▒█████
 ██▒ ▀█▒▒██  ██▒▒████▄    ▓██   ▒▒████▄    ▒██▒  ██▒
▒██░▄▄▄░ ▒██ ██░▒██  ▀█▄  ▒████ ░▒██  ▀█▄  ▒██░  ██▒
░▓█  ██▓ ░ ▐██▓░░██▄▄▄▄██ ░▓█▒  ░░██▄▄▄▄██ ▒██   ██░
░▒▓███▀▒ ░ ██▒▓░ ▓█   ▓██▒░▒█░    ▓█   ▓██▒░ ████▓▒░
 ░▒   ▒   ██▒▒▒  ▒▒   ▓▒█░ ▒ ░    ▒▒   ▓▒█░░ ▒░▒░▒░
  ░   ░ ▓██ ░▒░   ▒   ▒▒ ░ ░       ▒   ▒▒ ░  ░ ▒ ▒░
░ ░   ░ ▒ ▒ ░░    ░   ▒    ░ ░     ░   ▒   ░ ░ ░ ▒
      ░ ░ ░           ░  ░             ░  ░    ░ ░
        ░ ░


        ''')
    main()

input('aperte enter para sair.')