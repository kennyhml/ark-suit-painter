import random
from threading import Thread
from pynput import keyboard
import time

import screen
from ark import Ark, BotTerminated
import pyautogui as pg



REGION_1 = 240, 266
REGION_2 = 240, 327
REGION_3 = 240, 387
REGION_4 = 530, 266
REGION_5 = 530, 327
REGION_6 = 530, 387


PAINTABLE = {
    "tek_boots": [REGION_1, REGION_2, REGION_3, REGION_5, REGION_6],
    "tek_chest": [REGION_1, REGION_2, REGION_3, REGION_4, REGION_5, REGION_6],
    "tek_gauntlets": [REGION_1, REGION_2, REGION_3, REGION_5, REGION_6],
    "tek_leggings": [REGION_1, REGION_3, REGION_4, REGION_5, REGION_6],
    "tek_helmet": [REGION_1, REGION_2, REGION_3, REGION_5, REGION_6],
}


COLOR_LOCATIONS = [(x, y) for x in range(163, 614, 89) for y in range(537, 624, 86)]


class TekSuitPainter(Ark):
    """Main Suit Painter handle"""

    def __init__(self) -> None:
        super().__init__()
        self.suit_pieces = [
            "tek_boots",
            "tek_chest",
            "tek_gauntlets",
            "tek_leggings",
            "tek_helmet",
        ]

    def turn_to_vault(self, vault):
        """Turn to a vault, vault should be either `to paint` or
        `painted`. If this is not the case, an AssertionError will
        be raised.
        """
        assert vault in ["painted", "to paint"]

        if vault == "painted":
            print("Turning to the 'painted' vault...")
            while not screen.painted_vault_visible():
                self.turn_right()
        else:
            print("Turning to the 'to paint' vault...")
            while not screen.to_paint_vault_visible():
                self.turn_right()

        print("Now facing the vault!")

    def take_pieces(self, piece):
        """Takes as many pieces of a certain armor type as configurated by the user,
        comparing the previous amount in inventory to the new amount to avoid lag problems.
        """
        while not screen.get_amount_of_pieces(piece) == self.config["suits_per_grab"]:

            # set previous amount
            amount = screen.get_amount_of_pieces(piece)
            pg.moveTo(1296, 278)
            pg.click(button="left")
            self.press("t")

            # wait for the new amount to not match the previous amount
            while screen.get_amount_of_pieces(piece) == amount:
                pass

    def take_suit_pieces(self):
        """Turns to the fresh suit vault, opens it and takes x pieces of each
        suit piece where x is defined by the user.
        """
        self.turn_to_vault("to paint")
        self.open_vault()

        # repeat for every piece
        for piece in self.suit_pieces:
            self.search_in_vault(piece.split("_")[1])
            self.take_pieces(piece)

    def take_fresh_suits(self):
        """Takes fresh suits and opens the painted vault"""
        self.take_suit_pieces()
        self.close_vault()
        self.turn_to_vault("painted")
        self.open_vault()

    def get_all_targets(self):
        """Locates all armor pieces in the inventory and stores them in a hashmap"""
        return {piece: screen.get_piece_positions(piece) for piece in self.suit_pieces}

    def enter_paint_menu(self, piece_position):
        """Opens the paint menu by moving random color to the piece to be painted.
        This is achieved by matching for a grayscale image of the color.
        """
        random_paint = screen.find_random_color()
        pg.moveTo(random_paint)
        self.sleep(0.1)
        pg.dragTo(piece_position, button="left", duration=0.2)
        self.sleep(1)

    def paint_random(self, piece):
        """Paints a piece randomly, for each region the piece owns it will
        randomly choose a color field to select and apply.
        """
        # repeat for each region the piece supports
        for region in PAINTABLE[piece]:
            color = random.choice(COLOR_LOCATIONS)  # get a random color
            pg.moveTo(color)
            pg.click(button="left")

            # using double clicks instead of moving down to *apply paint*
            pg.moveTo(region)
            pg.click(button="left", clicks=3, interval=0.3)

    def paint_all_pieces(self, pieces):
        """Accepts a hashmap containing the positions of all pieces of
        a certain type. It will go over each piece applying random color
        to the available regions.
        """
        for suit_piece in pieces:

            # access the hashed list by piece key to get points
            for position in pieces[suit_piece]:
                self.enter_paint_menu(position)
                self.paint_random(suit_piece)
                self.press("esc")
                self.sleep(1)

    def run(self):
        while self.running:
            self.take_fresh_suits()
            pieces_to_paint = self.get_all_targets()
            self.paint_all_pieces(pieces_to_paint)
            self.search_in_inventory("tek")
            self.put_away_all()
            self.close_vault()

def on__key_press(key):
    """Connets inputs from listener thread to their corresponding function"""

    if key == keyboard.Key.f1:  # started
        # make sure bot is not already active
        if not (Ark.paused or Ark.running):
            Ark.running = True  # set active
            print("**Bot has been started!**")

            bot = Thread(target=main, daemon=True, name="Main bot Thread")
            bot.start()

    elif key == keyboard.Key.f3:  # terminated
        if Ark.running:
            Ark.paused = False
            Ark.running = False  # stop the bot
            print("Bot terminated!")

    elif key == keyboard.Key.f5:  # terminated
        if Ark.running and not Ark.paused:
            Ark.paused = True
            print("Bot paused!")

        elif Ark.paused:
            Ark.paused = False
            print("Bot unpaused!")


def main():

    try:
        painter = TekSuitPainter()
        painter.run()    

    except BotTerminated:
        pass

    except Exception as e:
        print(f"Unhandled exception in main bot thread!\n{e}")

if __name__ == "__main__":
    listener = keyboard.Listener(on_press=on__key_press)
    listener.start()  # start listener thread

    while True:
        time.sleep(100)
