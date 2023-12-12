# -*- coding: utf-8 -*-
import socket
import json
import time
import re
from threading import Thread
import logging
import os

host = '127.0.0.1'
port = 7777

global lobby_server
global lobby_address
global uid_address
uid_address = {}
global address_connect
address_connect = {}
register_command = ''
player_command = []
to_lobby_command = []
to_social_command = []
to_both_command = []

def accept():
    while True:
        connect, address = server.accept()
        thread = Thread(target=handle,args=(connect, address))
        thread.setDaemon(True)
        thread.start()

def handle(connect, address):
    bIsConnect = checkAddress(connect, address)
    pattern = None
    receive_data = ''
    if bIsConnect == True:
        global address_connect
        address_connect[address] = connect
        print(address)
        logger.info('connect : ' + str(address))
    while bIsConnect:
        try:
            data = connect.recv(65535)
        except Exception as e:
            logger.info(e)
            print(e)
            break
        if len(data) == 0:
            address_connect.pop(address)
            global lobby_server
            if lobby_address == address :
                lobby_server = None
            connect.close()
            bIsConnect = False
        if len(data) > 0:
            receive = data.decode('utf-8')
            print(receive)
            receive_data += receive
            result = []
            found = receive_data.find('##')
            while found != -1:
                temp = receive_data[0:found]
                result.append(temp)
                receive_data = receive_data.replace(temp + '##', '')
                found = receive_data.find('##')
            for each in result:
                switchCommand(connect, each, address)
    print('close thread')

def checkAddress(connect, address):
    if address[0] != '127.0.0.1':
        connect.close()
        return False
    return True

def switchCommand(connect, message, address):
    message = message.replace('#', '')
    json_object = json.loads(message)
    command = json_object['command']
    if command == register_command:
        register(connect, json_object, address)
    elif command in player_command:
        switchPlayerCommand(command, json_object, address)
    elif command in to_lobby_command:
        switchToLobbyCommand(command, json_object, address)
    elif command in to_social_command:
        switchToSocialCommand(command, json_object, address)
    elif command in to_both_command:
        switchToBothCommand(command, json_object, address)
    else:
        print("Can't find this command " + command)

def switchPlayerCommand(command, json_object, address):
    if command == player_command[0]:
        addPlayer(json_object, address)
    elif command == player_command[1]:
        removePlayer(json_object, address)
    else:
        print("Can't find this command " + command + " in Player Command")

def switchToLobbyCommand(command, json_object, address):
    if command == to_lobby_command[0]:
        createGroup(json_object, address)
    elif command == to_lobby_command[1]:
        requestMatch(json_object, address)
    elif command == to_lobby_command[2]:
        cancelMatch(json_object, address)
    elif command == to_lobby_command[3]:
        requestJoinGroup(json_object, address)
    elif command == to_lobby_command[4]:
        requestLeaveGroup(json_object, address)
    elif command == to_lobby_command[5]:
        requestUpdateRoomData(json_object, address)
    else:
        print("Can't find this command " + command + " in To Lobby Command")

def switchToSocialCommand(command, json_object, address):
    if command == to_social_command[0]:
        respondCreateGroup(json_object, address)
    elif command == to_social_command[1]:
        respondUpdateRoomData(json_object, address)
    elif command == to_social_command[2]:
        respondMatch(json_object, address)
    elif command == to_social_command[3]:
        matchFinishAws(json_object, address)
    elif command == to_social_command[4]:
        respondCancelMatch(json_object, address)
    elif command == to_social_command[5]:
        respondJoinGroup(json_object, address)
    elif command == to_social_command[6]:
        respondLeaveGroup(json_object, address)
    else:
        print("Can't find this command " + command + " in To Social Command")

def switchToBothCommand(command, json_object, address):
    if command == to_both_command[0]:
        respondFinishMatch(json_object, address)
    elif command == to_both_command[1]:
        respondGameServer(json_object, address)
    elif command == to_both_command[2]:
        respondFriendJoinRoom(json_object, address)
    elif command == to_both_command[3]:
        respondMatchMaking(json_object, address)
    elif command == to_both_command[4]:
        respondCancelMatchMaking(json_object, address)
    else:
        print("Can't find this command " + command + " in To Both Command")

def register(connect, json_object, address):
    if json_object['server'] == 'lobby':
        global lobby_server
        lobby_server = connect
        global lobby_address
        lobby_address = address
        respone = {"command" : "register", "message" : "register success"}
        lobby_server.sendall((str(respone) + '##').encode('utf-8'))

def addPlayer(json_object, address):
    uid = json_object['uid']
    global uid_address
    uid_address[uid] = address

def removePlayer(json_object, address):
    uid = json_object['uid']
    global uid_address
    try:
        uid_address.pop(uid)
    except KeyError:
        logger.info('remove player error')

def createGroup(json_object, address):
    uid = json_object['uid']
    global uid_address
    uid_address[uid] = address
    sendDataToLobby(json_object, address)

def respondCreateGroup(json_object, address):
    sendDataByUID(json_object, address)

def respondUpdateRoomData(json_object, address):
    sendDataByUID(json_object, address)

def requestMatch(json_object, address):
    sendDataToLobby(json_object, address)

def matchFinishAws(json_object, address):
    sendDataByUID(json_object, address)

def respondFinishMatch(json_object, address):
    sendDataToUncertainServer(json_object, address)

def respondGameServer(json_object, address):
    sendDataToUncertainServer(json_object, address)

def cancelMatch(json_object, address):
    sendDataToLobby(json_object, address)

def respondCancelMatch(json_object, address):
    sendDataByUID(json_object, address)

def respondMatch(json_object, address):
    sendDataByUID(json_object, address)

def requestJoinGroup(json_object, address):
    uid = json_object['uid']
    global uid_address
    uid_address[uid] = address
    sendDataToLobby(json_object, address)

def respondJoinGroup(json_object, address):
    sendDataByUID(json_object, address)

def requestLeaveGroup(json_object, address):
    sendDataToLobby(json_object, address)

def requestUpdateRoomData(json_object, address):
    sendDataToLobby(json_object, address)

def respondLeaveGroup(json_object, address):
    sendDataByUID(json_object, address)

def respondFriendJoinRoom(json_object, address):
    sendDataToUncertainServer(json_object, address)

def respondMatchMaking(json_object, address):
    sendDataToUncertainServer(json_object, address)

def respondCancelMatchMaking(json_object, address):
    sendDataToUncertainServer(json_object, address)

def sendDataToLobby(json_object, address):
    if lobby_server != None:
        try:
            lobby_server.sendall((str(json_object) + '##').encode('utf-8'))
        except Exception as e:
            logger.info(e)
            print(e)

def sendDataByUID(json_object, address):
    uid = json_object['uid']
    get_address = uid_address.get(uid)
    if get_address != None:
        get_connect = address_connect.get(get_address)
        if get_connect != None:
            try:
                get_connect.sendall((str(json_object) + '##').encode('utf-8'))
            except Exception as e:
                logger.info(e)
                print(e)

def sendDataToUncertainServer(json_object, address):
    uid = json_object['uid']
    if uid in uid_address:
        sendDataByUID(json_object, address)
    else:
        sendDataToLobby(json_object, address)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('TCPServer.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger = logging.getLogger('')
logger.addHandler(file_handler)

print(os.getcwd())

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))
server.listen(128)

print('Start Listening on ' + host + ' ' + str(port))
accept()
