import json
import sys
from json import JSONDecodeError
from pathlib import Path

from loguru import logger
from pywebostv.connection import WebOSClient
from pywebostv.controls import InputControl, ApplicationControl, SystemControl, TvControl

creds_file = Path.home() / '.lgtv.creds'


def send_command(tv_ip: str, command_name: str):
    # 1. For the first run, pass in an empty dictionary object. Empty store leads to an Authentication prompt on TV.
    # 2. Go through the registration process. `store` gets populated in the process.
    # 3. Persist the `store` state to disk.
    # 4. For later runs, read your storage and restore the value of `store`.
    store = {}
    delete_creds = True

    if creds_file.exists():
        with creds_file.open('rt') as f:
            try:
                store = json.load(f)
            except JSONDecodeError:
                logger.warning(f"Error loading saved credentials. Attempting to reauthenticate...")

    # Scans the current network to discover TV. Avoid [0] in real code. If you already know the IP,
    # you could skip the slow scan and # instead simply say:
    client = WebOSClient(tv_ip)
    # client = WebOSClient.discover()[0]
    client.connect()
    for status in client.register(store):
        if status == WebOSClient.PROMPTED:
            print("Please accept the connect on the TV!")
        elif status == WebOSClient.REGISTERED:
            print("Registration successful!")

    # Keep the 'store' object because it contains now the access token
    # and use it next time you want to register on the TV.
    # print(store)  # {'client_key': 'ACCESS_TOKEN_FROM_TV'}

    with creds_file.open('wt') as f:
        json.dump(store, f)

    # Blocking call can throw as error:
    try:
        inp = InputControl(client)
        inp.connect_input()

        app = ApplicationControl(client)
        sys = SystemControl(client)
        tv = TvControl(client)
        apis = [inp, app, sys, tv]

        api = [a for a in apis if hasattr(a, command_name)]
        if len(api) != 1:
            logger.error(f'No command found with name: {command_name}')
        else:

            api[0].__getattr__(command_name)()  # run the command
            logger.info(f'Sent {command_name} command')
    except BaseException as e:
        logger.exception("Something went wrong.")

    inp.disconnect_input()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Usage: python send_command.py <tv_ip_address> <command>. ')
        print('See https://github.com/supersaiyanmode/PyWebOSTV for command list\n')
        print('Eg. python run 192.168.1.10 volume_up')
    else:
        tv_ip = sys.argv[1]
        command_name = sys.argv[2]
        send_command(tv_ip, command_name)
