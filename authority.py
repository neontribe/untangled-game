import random

import bson
import zmq
from pyre import Pyre

from player import PlayerManager


class AuthorityPlayerManager():
    def __init__(self):
        self.players = {}

    def set(self, players):
        newPlayers = {}
        for uuid in players:
            str_uuid = str(uuid)
            random.seed(str_uuid)
            newPlayers[str_uuid] = self.players.get(str_uuid, Player(uuid))
        self.players = newPlayers

    def get(self, uuid):
        return self.players[str(uuid)]


class Player():
    def __init__(self, uuid):
        self.uuid = uuid


class Authority():
    def __init__(self):
        self.node = Pyre("GAME_AUTH")
        self.node.set_header("AUTHORITY", "TRUE")
        self.node.start()
        self.node.join("ctf:teams")
        self.node.join("ctf:flags")

        self.poller = zmq.Poller()
        self.poller.register(self.node.socket(), zmq.POLLIN)

        self.players = AuthorityPlayerManager()

        self.teams = {
            "blue": [],
            "red": []
        }
        
        self.flags = {
            "blue": "", 
            "red": ""
        }

        self.serve()

    def set_teams(self):
        blue_players = self.teams["blue"]
        red_players = self.teams["red"]

        # Check for removed players in RED
        for i, playerUUID in enumerate(red_players):
            if playerUUID not in self.players.players.keys():
                red_players.pop(i)
        # Check for removed players in BLUE
        for i, playerUUID in enumerate(blue_players):
            if  playerUUID not in self.players.players.keys():
                blue_players.pop(i)

        # Add new players
        for playerUUID, player in self.players.players.items():
            if not (playerUUID in blue_players or playerUUID in red_players):
                if len(blue_players) > len(red_players):
                    red_players.append(playerUUID)
                else:
                    blue_players.append(playerUUID)

        print("Teams: " + "RED: " + ','.join(red_players) + " | BLUE: " + ','.join(blue_players))
        self.node.shout("ctf:teams", bson.dumps(self.teams))

    def serve(self):
        while True:
            # check network
            self.players.set(self.node.peers())
            events = self.get_events()
            if events:
                try:
                    for event in events:
                        # Update the teams on JOIN and EXIT
                        if event.type == 'JOIN':
                            self.set_teams()
                        elif event.type == 'EXIT':
                            self.set_teams()

                except Exception as e:
                    print(e)
                    import traceback
                    print(traceback.format_exc())
                    pass

    def poll(self):
        return dict(self.poller.poll(0))

    def peers(self):
        return self.node.peers()

    def stop(self):
        self.node.stop()

    def get_events(self):
        changes = self.poll()
        if self.node.socket() in changes and changes[self.node.socket()] == zmq.POLLIN:
            events = self.node.recent_events()
            return events


authority = Authority()
