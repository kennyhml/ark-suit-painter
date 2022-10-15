
import pydirectinput
import json
import screen
import time
import os
import pyautogui as pg

VAULT_SEARCH = 1311, 180
INVENTORY_SEARCH = 179, 184

class BotTerminated(Exception):
    """Raised when the bot has been terminated"""


class Ark:
    """Main handle for movement and ark related methods"""

    __version__ = "0.0.1"
    running = False
    paused = False

    def __init__(self) -> None:
        with open("config/config.json", "r") as f:
            self.config = json.load(f)

    def check_state(self) -> None:
        """Checks if the bot has been terminated or paused"""
        if not self.running:
            raise BotTerminated

        while self.paused:
            time.sleep(0.1)
            if not self.running:
                raise BotTerminated

    def sleep(self, t: int | float) -> None:
        """Custom sleep method to invoke a state check"""
        self.check_state()
        time.sleep(t)

    def press(self, key: str) -> None:
        """Custom press method to invoke a state check"""
        self.check_state()
        pg.press(key)

    def turn_right(self) -> None:
        """Turn right by the configurated rel move"""
        self.check_state()
        pydirectinput.moveRel(self.config["rel_move_per_tick"], 0, 0, None, False, False, True)

    def set_clipboard(self, text):
        """Sets the clickboard to the passed text"""
        command = "echo | set /p nul=" + text.strip() + "| clip"
        os.system(command)

    def open_inventory(self) -> None:
        """Opens the inventory"""
        while not screen.inventory_is_open():
            self.press(self.config["inventory"])
            self.sleep(1)

    def open_vault(self) -> None:
        """Opens a vault"""
        while not screen.vault_is_open():
            self.press(self.config["access_vault"])
            c = 0
            while not screen.vault_is_open():
                self.sleep(0.1)
                c += 1
                if c > 100:
                    break

    def close_vault(self) -> None:
        """Closes a vault"""
        pg.moveTo(1816, 35)
        pg.click(button="left")

        while screen.vault_is_open():
            pg.click(button="left")
            c = 0
            while screen.vault_is_open():
                self.sleep(0.1)
                c += 1
                if c > 100:
                    break
                    
    def put_away_all(self) -> None:
        """Hits the transfer all button"""
        pg.moveTo(354, 185)
        pg.click(button="left")
        self.sleep(3)

    def search_in_vault(self, term) -> None:
        """Searches for the given term in a vault"""
        pg.moveTo(VAULT_SEARCH)
        pg.click(button="left", clicks=2)

        self.set_clipboard(term)
        with pg.hold("ctrl"):
            self.press("v")

    def search_in_inventory(self, term) -> None:
        """Searches for a given term in the inventory"""
        pg.moveTo(INVENTORY_SEARCH)
        pg.click(button="left", clicks=2)

        self.set_clipboard(term)
        with pg.hold("ctrl"):
            self.press("v")
    