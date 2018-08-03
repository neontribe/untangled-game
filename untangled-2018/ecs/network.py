import bson
import sys
import uuid
import zmq
from pyre import Pyre
from typing import List, Union

import ecs.components.component as components


class Network:
    def __init__(self):
        # peer-to-peer node
        self.node = Pyre()
        self.node.start()
        self.node.join('untangled2018')

        # used to get our messages
        self.poller = zmq.Poller()
        self.poller.register(self.node.socket(), zmq.POLLIN)

        self.hosting = False

    def get_all_groups(self) -> List[str]:
        """Get the names of groups that can be joined."""
        groups = []
        for peer in self.node.peers():
            group = self.node.peer_header_value(peer, 'hosting')
            if group != None and len(group) > 0:
                groups.append(group)
        return groups

    def get_our_group(self) -> Union[str, None]:
        """What is the name of the group we're in or hosting?"""
        our_groups = self.node.own_groups()
        our_groups.remove('untangled2018')
        if len(our_groups) == 0:
            return None
        return our_groups[0]

    def is_in_group(self) -> bool:
        """Are we in or hosting a group?"""
        return self.get_our_group() != None

    def is_hosting(self) -> bool:
        """Are we hosting?"""
        return self.hosting

    def join_group(self, group: str) -> None:
        """Join a group of given name (assumes you are not in a group already)."""
        if group not in self.get_all_groups():
            raise ValueError('Group named "%s" does not exist'.format(group))

        if self.is_in_group():
            raise ValueError('You must leave the previous group before you join another')

        self.node.join(group)

    def leave_group(self) -> None:
        """Leave any joined group or stop hosting."""
        self.hosting = False

        if not self.is_in_group():
            raise ValueError('You are not in a group')

        for group in self.node.own_groups():
            self.node.leave(group)

    def host_group(self, name: str) -> None:
        """Host a group of given name."""
        if name in self.get_all_groups():
            raise ValueError('A group of the given name already exists')

        if self.is_in_group():
            raise ValueError('Cannot host whilst in a group')

        self.node.set_header('hosting', name)
        self.hosting = True
        self.node.join(name)

    def get_id(self) -> str:
        """Get our id, as a unique node on the network."""
        return self.node.uuid()

    def is_me(self, player_id) -> bool:
        """See if a given id is ours."""
        return self.get_id() == player_id

    def close(self) -> None:
        """Disconnect from everything"""
        self.node.stop()

    def get_messages(self):
        """See what has been sent to us: who has joined, what have people said, etc"""
        # what has changed
        changes = dict(self.poller.poll(0))

        # are these the changes we subscribed for
        if self.node.socket() in changes and changes[self.node.socket()] == zmq.POLLIN:
            msgs = self.node.recent_events()
            return msgs

        # nothing to return
        return []

    def pull_game(self, game):
        """Update our game state based on what other people tell us."""
        for msg in self.get_messages():
            # is it relevant to us?
            if msg.group != self.get_our_group():
                continue
            if msg.type == 'SHOUT':
                entities = bson.loads(msg.msg[0])
                for key, changed_comps in entities.items():
                    key = uuid.UUID(key)
                    if key not in game.entities:
                        game.entities[key] = {}
                    entity = game.entities[key]
                    for compname, component in changed_comps.items():
                        try:
                            clas = components.__dict__[compname]
                            if clas in entity:
                                entity[clas] = entity[clas].replace(**component)
                            else:
                                entity[clas] = clas(**component)
                            entity[clas].observed_changes()
                        except Exception:
                            print('Error updating component, is everyone in the group on the same version?', file=sys.stdout)
            elif self.is_hosting():
                if msg.type == 'JOIN':
                    game.on_player_join(msg.peer_uuid)
                    self.push_game(game, initial=True)
                elif msg.type == 'LEAVE':
                    game.on_player_quit(msg.peer_uuid)

    def push_game(self, game, initial=False):
        """Tell others how we've changed the game state."""
        entities = {}
        for key, entity in game.entities.items():
            changed_comps = {}
            for component in entity.values():
                if component.is_networked() and (initial or component.has_changed()):
                    changed_comps[component.get_name()] = component.as_dict()
                    component.observed_changes()
            entities[str(key)] = changed_comps
        self.node.shout(self.get_our_group(), bson.dumps(entities))
