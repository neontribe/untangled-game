import random
from uuid import UUID

import bson
import zmq

from pyre import Pyre
from pygame.time import Clock

from level import SaveLevel, Place
from tile import TileType

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
        self.node.join("ctf:scores")
        self.node.join("ctf:status")

        self.poller = zmq.Poller()
        self.poller.register(self.node.socket(), zmq.POLLIN)

        self.players = AuthorityPlayerManager()

        self.teams = {
            "blue": [],
            "red": []
        }
  
        self.level = SaveLevel('./assets/maps/CAPFLAG MAP NAT')
        red_spawn_pos = self.level.get_place(Place.RED_SPAWN)
        blue_spawn_pos = self.level.get_place(Place.BLUE_SPAWN)

        self.flags = {
            "blue": {
                "x": blue_spawn_pos[0],
                "y": blue_spawn_pos[1],
                "owner": '',
            }, 
            "red": {
                "x": red_spawn_pos[0],
                "y": red_spawn_pos[1],
                "owner":'',
            }
        }

        self.scores = {
            "red": 0,
            "blue": 0
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

    def get_team_from_uuid(self, uuid):
        place = None

        if str(uuid) in self.teams['red']:
            place = Place.RED_SPAWN
        elif str(uuid) in self.teams['blue']:
            place = Place.BLUE_SPAWN

        return place

    def serve(self):
        clock = Clock()
        while True:
            clock.tick(60)

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
                                place = self.get_team_from_uuid(event.peer_uuid)
                                pos = self.level.get_place(place)
                                self.node.whisper(event.peer_uuid, bson.dumps({
                                    'type': 'teleport',
                                    'x': pos[0],
                                    'y': pos[1]
                                }));
                            elif event.group == 'ctf:scores':
                                self.node.shout('ctf:scores', bson.dumps(self.scores))
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

                                # check if flag has been captured
                                for team, flag in self.flags.items():
                                    if flag['owner'] != str(event.peer_uuid):
                                        continue
                                    tile = self.level.get_tile(new_position['x'], new_position['y'])
                                    if tile == TileType.RED_BLOCK and team == 'blue':
                                        self.scores['red'] += 1
                                        spawn = Place.BLUE_SPAWN
                                    elif tile == TileType.BLUE_BLOCK and team == 'red':
                                        self.scores['blue'] += 1
                                        spawn = Place.RED_SPAWN
                                    else:
                                        continue

                                    # reset the flag back to spawn
                                    position = self.level.get_place(spawn)
                                    flag['x'] = position[0]
                                    flag['y'] = position[1]
                                    flag['owner'] = ''
                                    self.node.shout('ctf:dropflag', bson.dumps({
                                        'x': flag['x'],
                                        'y': flag['y'],
                                        'team': team
                                    }))

                                    # broadcast the update scores
                                    self.node.shout('ctf:scores', bson.dumps(self.scores))

                                    for winning_team, score in self.scores.items():
                                        if score < 10:
                                            continue
                                        self.node.shout('ctf:status', bson.dumps({
                                            'status': winning_team.title() + ' wins!'
                                        }))

                                        for team, uuids in self.teams.items():
                                            # reset scores
                                            self.scores[team] = 0
                                            spawn = Place.RED_SPAWN if team == 'red' else Place.BLUE_SPAWN
                                            pos = self.level.get_place(spawn)

                                            # reset flag
                                            self.flags[team]['x'], self.flags[team]['y'] = pos
                                            self.flags[team]['owner'] = ''
                                            self.node.shout('ctf:dropflag', bson.dumps({
                                                'x': self.flags[team]['x'],
                                                'y': self.flags[team]['y'],
                                                'team': team
                                            }))

                                            # reset players to spawn
                                            for uuid in uuids:
                                                self.node.whisper(UUID(uuid), bson.dumps({
                                                    'type': 'die'
                                                }))

                                        self.node.shout('ctf:scores', bson.dumps(self.scores))


                            if event.group == 'ctf:gotflags':
                                flag_info = bson.loads(event.msg[0])
                                self.set_flags(flag_info)
                        elif event.type == 'WHISPER':
                            msg = bson.loads(event.msg[0])
                            network_player = self.players.get(event.peer_uuid)
                            if msg['type'] == 'death_report':
                                player = self.players.get(event.peer_uuid)
                                previously_owned_flag = None
                                if self.flags['blue']['owner'] == str(event.peer_uuid):
                                    previously_owned_flag = 'blue'
                                elif self.flags['red']['owner'] == str(event.peer_uuid):
                                    previously_owned_flag = 'red'

                                if previously_owned_flag:
                                    flag = self.flags[previously_owned_flag]
                                    flag['owner'] = ''
                                    flag['x'] = player.x
                                    flag['y'] = player.y
                                    self.node.shout('ctf:dropflag', bson.dumps({
                                        'x': player.x,
                                        'y': player.y,
                                        'team': previously_owned_flag
                                    }))

                                place = self.get_team_from_uuid(event.peer_uuid)
                                pos = self.level.get_place(place)
                                self.node.whisper(event.peer_uuid, bson.dumps({
                                    'type': 'teleport',
                                    'x': pos[0],
                                    'y': pos[1]
                                }))
                                player.x = pos[0]
                                player.y = pos[1]

                except Exception as e:
                    print(e)
                    import traceback
                    print(traceback.format_exc())
                    pass

            for team, flag in self.flags.items():
                if flag["owner"] != '': continue
                for uuid, player in self.players.players.items():
                    if flag['x'] == player.x and flag['y'] == player.y:
                        team_place = self.get_team_from_uuid(uuid)
                        pos = self.level.get_place(team_place)
                        if team == 'red' and team_place == Place.RED_SPAWN or team == 'blue' and team_place == Place.BLUE_SPAWN:
                            if player.x == pos[0] and player.y == pos[1]:
                                continue
                            self.flags[team]['x'] = pos[0]
                            self.flags[team]['y'] = pos[1]
                            self.node.shout('ctf:dropflag', bson.dumps({
                                'x': pos[0],
                                'y': pos[1],
                                'team': team
                            }));
                        else:
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
