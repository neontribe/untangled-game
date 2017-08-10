import pygame
import pygame.locals
import socket
import select
import random
import time
import logging
import zmq
import pdb
import bson
import uuid
import webbrowser
from pyre import Pyre, pyre_event
from pyre import zhelper
from collections import namedtuple
from enum import Enum

from map import *
from network import Network
from player import *
from sprite import *
from screen import MainMenu
from level import SaveLevel
from tile import Tileset
from music import LevelMusic

white = (255,255,255)
black = (0,0,0)
red = (255, 0, 0)

width = 1024
height = 1024

font = 'assets/fonts/alterebro-pixel-font.ttf'
level_tileset_path = 'assets/tilesets/main.png'
player_animation_tileset_path = 'assets/tilesets/player.png'
red_flag = "assets/tilesets/Red Flag.png"
blue_flag = "assets/tilesets/Blue Flag.png"

projectile_paths = [
                    'assets/images/arrow.png',
                    'assets/images/fireball.png',
                    'assets/images/frostbolt.png',
                    'assets/images/icicle.png',
                    'assets/images/lightning_bolt.png',
                    'assets/images/poisonball.png'
                    ]

#buttons = {"A":1, "B":2, "X":0, "Y":3, "L":4, "R":5, "Start":9, "Select":8} #Use these for the PiHut SNES controller
buttons = {"A":0, "B":1, "X":2, "Y":3, "L":4, "R":5, "Start":7, "Select":6} #Use these for the iBuffalo SNES controller

error_message = "Everything is lava"

class GameState(Enum):
    MENU = 0
    PLAY = 1
    HELP = 2
    CHARACTER = 3
    QUIT = 4
    MUTE = 5

class GameClient():
    game_state = GameState.MENU

    def __init__(self):
        self.network = Network()
        self.setup_pygame()
        me = Player(self.screen, self.map, self.network)
        self.players = PlayerManager(me, self.network)

        self.network.node.shout('players:whois', bson.dumps({}))

        red = Sprite(self.screen, self.map, red_flag)
        blue = Sprite(self.screen, self.map, blue_flag)
        self.flags = {
            'red': red,
            'blue': blue
        }
        self.map.set_centre_player(self.players.me)
        self.menu = MainMenu(self.screen, self.players)

    def setup_pygame(self):
        # Initialise screen/display
        self.screen = pygame.display.set_mode((width, height), pygame.HWSURFACE)

        # Initialise fonts.
        pygame.font.init()

        # Initialise music
        pygame.mixer.init()

        # Initialise the joystick.
        pygame.joystick.init()
        joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for joystick in joysticks:
            joystick.init()

        pygame.event.set_allowed(None)
        pygame.event.set_allowed([pygame.locals.QUIT,
            pygame.locals.JOYAXISMOTION,
            pygame.locals.KEYDOWN, pygame.locals.MOUSEBUTTONDOWN,  pygame.locals.JOYBUTTONDOWN])

        self.levels = {
            "main": SaveLevel('./assets/maps/CAPFLAG MAP NAT')
        }

        self.map = Map(
            self.screen,
            self.levels.get("main"),
            Tileset(level_tileset_path, (16, 16), (32, 32)),
            LevelMusic('assets/music/mario.mp3')
        )
        self.map.music.load_music()

    def set_state(self, new_state):
        if(new_state and new_state != self.game_state):
            self.game_state = new_state

            if(self.game_state.value == GameState.PLAY.value):
                pygame.key.set_repeat(50, 50)
            else:
                pygame.key.set_repeat(0, 0)

    def run(self):
        running = True
        clock = pygame.time.Clock()
        tickspeed = 60
        last_direction = None
        self.toMove = False # Flag for when player moves - reduces network stress
        self.cast = False # Flag for when player casts spell.
        me = self.players.me

        if me.mute == "False":
            LevelMusic.play_music_repeat()

        try:
            while running:
                self.screen.fill((white))
                clock.tick(tickspeed)

                if(self.game_state.value == GameState.MENU.value):
                    self.menu.render((self.map.screen.get_width() * 0.45, self.map.screen.get_height()*0.4))
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT or event.type == pygame.locals.QUIT:
                            running = False
                            break

                        self.set_state(self.menu.update(event))
                elif(self.game_state.value == GameState.QUIT.value):
                    running = False
                    break
                elif(self.game_state.value == GameState.HELP.value):
                    webbrowser.open_new_tab("https://github.com/neontribe/untangled-2017/wiki")
                    self.game_state = GameState.MENU
                elif(self.game_state.value == GameState.MUTE.value):
                    if me.mute == "False":
                        me.set_mute("True", True)
                        LevelMusic.stop_music()
                    elif me.mute == "True":
                        me.set_mute("False", True)
                        LevelMusic.play_music_repeat()
                    self.game_state = GameState.MENU
                else:
                    # handle inputs
                    if last_direction == None:
                        last_direction = Movement.DOWN
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT or event.type == pygame.locals.QUIT:
                            running = False
                            break
                        elif event.type == pygame.locals.KEYDOWN and event.key == pygame.locals.K_ESCAPE:
                            self.set_state(GameState.MENU)
                        elif event.type == pygame.locals.KEYDOWN:
                            if event.key == pygame.locals.K_UP or event.key == pygame.locals.K_w:
                                me.move(Movement.UP)
                                last_direction = Movement.UP
                                self.toMove = True
                            elif event.key == pygame.locals.K_DOWN or event.key == pygame.locals.K_s:
                                me.move(Movement.DOWN)
                                last_direction = Movement.DOWN
                                self.toMove = True
                            elif event.key == pygame.locals.K_LEFT or event.key == pygame.locals.K_a:
                                me.move(Movement.LEFT)
                                last_direction = Movement.LEFT
                                self.toMove = True
                            elif event.key == pygame.locals.K_RIGHT or event.key == pygame.locals.K_d:
                                me.move(Movement.RIGHT)
                                last_direction = Movement.RIGHT
                                self.toMove = True
                            elif event.key == pygame.locals.K_e:
                                me.change_spell()
                            elif event.key == pygame.locals.K_RETURN or event.key == pygame.locals.K_SPACE :
                                if me.can_fire_ability:
                                    self.cast = me.attack(last_direction)

                            if event.key == pygame.locals.K_r and me.can_step_ability:
                                me.step = 2
                                me.steptime = time.time()
                                me.can_step_ability = False

                            if event.key == pygame.locals.K_q:
                                if me.can_switch_spell:
                                    me.change_spell()
                                    me.switch_time = time.time()
                                    me.can_switch_spell = False

                            pygame.event.clear(pygame.locals.KEYDOWN)

                    if event.type == pygame.locals.MOUSEBUTTONDOWN:
                        if event.button == 0:
                            if me.can_fire_ability:
                                self.cast = me.attack(last_direction)
                            pygame.event.clear(pygame.locals.MOUSEBUTTONDOWN)
                        if event.button == 4 or event.button == 5:
                            if me.can_switch_spell:
                                me.change_spell()
                                me.switch_time = time.time()
                                me.can_switch_spell = False
                                pygame.event.clear(pygame.locals.MOUSEBUTTONDOWN)

                    # https://stackoverflow.com/a/15596758/3954432
                    # Handle controller input by setting flags (move, neutral)
                    # and using timers (delay, pressed).
                    # Move if pressed timer is greater than delay.
                    if(pygame.joystick.get_count() > 0 and not me.name.startswith("windows") and not self.toMove):
                        joystick = pygame.joystick.Joystick(0)
                        move = False
                        delay = 100
                        neutral = True
                        pressed = 0
                        last_update = pygame.time.get_ticks()
                        y_axis = joystick.get_axis(1)
                        x_axis = joystick.get_axis(0)

                        if y_axis == 0 and x_axis == 0: #Indicates no motion.
                            neutral = True
                            pressed = 0
                        else:
                            if neutral:
                                move = True
                                neutral = False
                            else:
                                pressed += pygame.time.get_ticks() - last_update
                        if pressed > delay:
                            move = True
                            pressed -= delay
                        if move:
                            # up/down
                            if y_axis > 0.5:
                                me.move(Movement.DOWN)
                                last_direction = Movement.DOWN
                                self.toMove = True
                            if y_axis < -0.5:
                                me.move(Movement.UP)
                                last_direction = Movement.UP
                                self.toMove = True
                            # left/right
                            if x_axis > 0.5:
                                me.move(Movement.RIGHT)
                                last_direction = Movement.RIGHT
                                self.toMove = True
                            if x_axis < -0.5:
                                me.move(Movement.LEFT)
                                last_direction = Movement.LEFT
                                self.toMove = True

                        #Shoot
                        if joystick.get_button(buttons["R"]) or joystick.get_button(buttons["A"]):
                            if me.can_fire_ability:
                                self.cast = me.attack(last_direction)
                        #Menu
                        if joystick.get_button(buttons["Start"]) or joystick.get_button(buttons["Select"]):
                            self.set_state(GameState.MENU)
                        #Speed boost
                        if joystick.get_button(buttons["X"]) and me.can_step_ability:
                            me.step = 2
                            me.steptime = time.time()
                            me.can_step_ability = False
                        #Change spell
                        if joystick.get_button(buttons["L"]):
                            if me.can_switch_spell:
                                me.change_spell()
                                me.switch_time = time.time()
                                me.can_switch_spell = False

                        last_update = pygame.time.get_ticks()

                    if self.cast == True:
                        me.can_fire_ability = False
                        me.firetime = time.time()
                    elif time.time() - me.firetime > 0.5:
                        me.can_fire_ability = True

                    if time.time() - me.steptime >30:
                        me.can_step_ability = True
                    elif time.time() - me.steptime >3:
                        me.step = 1

                    if time.time() - me.switch_time > 0.1:
                        me.can_switch_spell = True

                    if time.time() - me.swim_timer > 0.3:
                        me.can_swim = True
                    if time.time() - me.sand_timer > 0.1:
                        me.can_sand = True

                    self.map.render()
                    for flag in self.flags.values():
                        flag.render()

                    me.render(True)

                    for spell in me.cast_spells:
                        spell.render()

                    self.players.set(self.network.node.peers())

                    # check network
                    events = self.network.get_events()
                    if events:
                        try:
                            for event in self.network.get_events():
                                if event.type == 'ENTER':
                                    # Force update on first join.
                                    self.toMove = True

                                    auth_status = event.headers.get('AUTHORITY')
                                    if auth_status == 'TRUE':
                                        self.players.authority_uuid = str(event.peer_uuid)
                                        self.network.authority_uuid = str(event.peer_uuid)
                                        self.players.remove(event.peer_uuid)
                                elif event.type == "SHOUT":
                                    if event.group == "player:name":
                                        new_name = bson.loads(event.msg[0])
                                        player = self.players.get(event.peer_uuid)
                                        if new_name['name']:
                                            player.set_name(new_name['name'])
                                    elif event.group == "world:position":
                                        new_position = bson.loads(event.msg[0])
                                        network_player = self.players.get(event.peer_uuid)
                                        network_player.set_position(Position(**new_position))
                                    elif event.group == "world:combat":
                                        new_spell_properties = bson.loads(event.msg[0])
                                        network_spell_caster = self.players.get(event.peer_uuid)
                                        network_spell_caster.current_spell = new_spell_properties.get('current_spell')
                                        network_spell_caster.cast_spells.append(Spell(network_spell_caster, (0, 0), projectile_paths[network_spell_caster.current_spell]))
                                        network_spell_caster.cast_spells[-1].set_properties(SpellProperties(**new_spell_properties))
                                    elif event.group == "ctf:teams":
                                        team_defs = bson.loads(event.msg[0])
                                        self.players.set_teams(team_defs)
                                    elif event.group == "ctf:gotflag":
                                        flag_info = bson.loads(event.msg[0])
                                        team = flag_info["team"]
                                        uuid = flag_info["uuid"]
                                        flag = self.flags[team]
                                        if uuid == str(self.network.node.uuid()):
                                            flag.set_player(self.players.me)
                                        else:
                                            network_player = self.players.get(uuid)
                                            flag.set_player(network_player)
                                    elif event.group == 'ctf:dropflag':
                                        flag_info = bson.loads(event.msg[0])
                                        flag = self.flags[flag_info['team']]
                                        flag.set_player(None)
                                        flag.set_position((flag_info['x'], flag_info['y']))
                                    elif event.group == "players:whois":
                                        self.network.node.shout("player:name", bson.dumps(
                                            {
                                                "name": self.players.me.name
                                            }
                                        ))
                                elif event.type == 'WHISPER':
                                    msg = bson.loads(event.msg[0])
                                    if self.players.authority_uuid == str(event.peer_uuid):
                                        if msg['type'] == 'teleport':
                                            me.set_position((msg['x'], msg['y']))
                                            self.toMove = True

                        except Exception as e:
                            import traceback
                            # traceback.print_exc()
                            pass

                    # if there are other peers we can start sending to groups.
                    if self.toMove == True:
                        self.network.node.shout("world:position", bson.dumps(me.get_position()._asdict()))
                        self.toMove = False
                    if self.cast == True:
                        self.network.node.shout("world:combat", bson.dumps(me.cast_spells[-1].get_properties()._asdict()))
                        self.cast = False

                    for playerUUID, player in self.players.others.items():
                        try:
                            player.render()
                            for spell in player.cast_spells:
                                spell.render()
                                hit_me = spell.hit_target_player(me)
                                if hit_me:
                                    player.cast_spells.remove(spell)
                                    me.deplete_health(spell.damage)

                        except PlayerException as e:
                            # PlayerException due to no initial position being set for that player
                            pass

                pygame.display.update()
        finally:
            self.network.stop()

if __name__ == '__main__':
    logger = logging.getLogger("pyre")
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    logger.propagate = False

    g = GameClient()
    g.run()
