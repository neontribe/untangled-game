import zmq
from pyre import Pyre
from typing import List


class Network:
    def __init__(self):
        self.node = Pyre()
        self.node.start()

        self.hosting = False

    def get_groups(self) -> List[str]:
        """Get the names of groups that can be joined."""
        return self.node.peer_groups()

    def is_in_group(self) -> bool:
        """Are we hosting or in a group?"""
        return len(self.node.own_groups()) > 0

    def is_hosting(self) -> bool:
        """Are we hosting?"""
        return self.hosting

    def join_group(self, group: str) -> None:
        """Join a group of given name (assumes you are not in a group already)."""
        if group not in self.get_groups():
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
            # TODO tell people that we've stopped hosting
            self.node.leave(group)

    def host_group(self, name: str) -> None:
        """Host a group of given name."""
        if name in self.get_groups():
            raise ValueError('A group of the given name already exists')

        if self.is_in_group():
            raise ValueError('Cannot host whilst in a group')

        self.hosting = True
        self.node.join(name)

    def close(self) -> None:
        """Disconnect from everything"""
        self.node.stop()

#
# class NetworkSystem(System):
#     def __init__(self):
#         self.node = Pyre("GAME_NODE")
#         self.node.set_header("GAME_HOST", "FALSE")
#         self.node.start()
#         self.node.peer_groups()
#         self.poller = zmq.Poller()
#         self.poller.register(self.node.socket(), zmq.POLLIN)
#
#     def peers(self):
#         return self.node.peers()
#
#     def stop(self):
#         self.node.stop()
#
#     def get_events(self):
#         changes = dict(self.poller.poll(0))
#         if self.node.socket() in changes and changes[self.node.socket()] == zmq.POLLIN:
#             events = self.node.recent_events()
#             return events
