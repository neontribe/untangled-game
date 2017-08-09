import random

import bson
import zmq

from pyre import Pyre
from level import SaveLevel, Place

RESETTIME = 5
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
        self.x, self.y = (None, None)

    def set_position(self, position):
        self.x = position['x']
        self.y = position['y']

class Authority():
    def __init__(self):
        self.node = Pyre("GAME_AUTH")
        self.node.set_header("AUTHORITY", "TRUE")
        self.node.start()
        self.node.join("world:position")
        self.node.join("ctf:teams")
        self.node.join("ctf:dropflag")
        self.node.join("ctf:gotflag")

        self.poller = zmq.Poller()
        self.poller.register(self.node.socket(), zmq.POLLIN)

        self.players = AuthorityPlayerManager()

        self.teams = {
            "blue": [],
            "red": []
        }
  
        self.level = SaveLevel('./assets/maps/CAPFLAG MAP')
        red_spawn_pos = self.level.get_place(Place.RED_SPAWN)
        blue_spawn_pos = self.level.get_place(Place.BLUE_SPAWN)

        self.flags = {
            "blue": {
                "x": blue_spawn_pos[0],
                "y": blue_spawn_pos[1],
                "owner": '',
                "timer":0
            }, 
            "red": {
                "x": red_spawn_pos[0],
                "y": red_spawn_pos[1],
                "owner":'',
                "timer":0
            }
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
    
    def set_flags(self, flag_info):
        return
        
    def update_flags(self):
        self.node.shout("ctf:flags", bson.dumps(self.flags))

    def serve(self):
        while True:
            # check network
            events = self.get_events()
            if events:
                try:
                    for event in events:
                        # Update the teams on JOIN and EXIT
                        if event.type == 'JOIN':
                            if event.group == 'ctf:dropflag':
                                for team, flag in self.flags.items():
                                    if flag['owner'] == '':
                                        self.node.shout('ctf:dropflag', bson.dumps({
                                            'x': flag['x'],
                                            'y': flag['y'],
                                            'team': team
                                        }));
                            elif event.group == 'ctf:gotflag':
                                for team, flag in self.flags.items():
                                    if flag['owner'] != '':
                                        self.node.shout('ctf:gotflag', bson.dumps({
                                            'uuid': flag['owner'],
                                            'team': team
                                        }));
                            elif event.group == 'ctf:teams':
                                self.players.set(self.node.peers())
                                self.set_teams()
                        elif event.type == 'EXIT':
                            for team, flag in self.flags.items():
                                if flag['owner'] == str(event.peer_uuid):
                                    # flag owner is leaving, drop
                                    player = self.players.get(event.peer_uuid)
                                    flag['x'] = player.x
                                    flag['y'] = player.y
                                    flag['owner'] =  ''
                                    self.node.shout('ctf:dropflag', bson.dumps({
                                        'x': flag['x'],
                                        'y': flag['y'],
                                        'team': team
                                    }));
                            self.players.set(self.node.peers())
                            self.set_teams()
                        elif event.type == 'SHOUT':
                            if event.group == "world:position":
                                new_position = bson.loads(event.msg[0])
                                network_player = self.players.get(event.peer_uuid)
                                network_player.set_position(new_position)
                            if event.group == 'ctf:gotflags':
                                flag_info = bson.loads(event.msg[0])
                                self.set_flags(flag_info)

                except Exception as e:
                    print(e)
                    import traceback
                    print(traceback.format_exc())
                    pass

            for team, flag in self.flags.items():
                if flag["owner"] != '': continue
                for uuid, player in self.players.players.items():
                    if flag['x'] == player.x and flag['y'] == player.y:
                        flag["owner"] = uuid
                        self.node.shout('ctf:gotflag', bson.dumps({
                            'uuid': uuid,
                            'team': team
                        }))
                        break

            

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
