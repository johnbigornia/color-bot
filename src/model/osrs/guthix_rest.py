import random
import time

import pyautogui

from utilities import ocr
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
import utilities.imagesearch as imsearch


class Guthix_Rest(OSRSBot):
    def __init__(self):
        bot_title = "Guthix Rest"
        description = "Brewing Guthix rest"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 1
        self.api_m = MorgHTTPSocket()
        self.GUTHIX_REST_IMAGES = imsearch.BOT_IMAGES.joinpath("for_scripts", "guthix_rest")


    def create_options(self):
        """
        Use the OptionsBuilder to define the options for the bot. For each function call below,
        we define the type of option we want to create, its key, a label for the option that the user will
        see, and the possible values the user can select. The key is used in the save_options function to
        unpack the dictionary of options after the user has selected them.
        """
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)

    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False.
        """
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        """
        When implementing this function, you have the following responsibilities:
        1. If you need to halt the bot from within this function, call `self.stop()`. You'll want to do this
           when the bot has made a mistake, gets stuck, or a condition is met that requires the bot to stop.
        2. Frequently call self.update_progress() and self.log_msg() to send information to the UI.
        3. At the end of the main loop, make sure to call `self.stop()`.

        Additional notes:
        - Make use of Bot/RuneLiteBot member functions. There are many functions to simplify various actions.
          Visit the Wiki for more.
        - Using the available APIs is highly recommended. Some of all of the API tools may be unavailable for
          select private servers. For usage, uncomment the `api_m` and/or `api_s` lines below, and use the `.`
          operator to access their functions.
        """
        # Setup APIs
        # api_m = MorgHTTPSocket()
        # api_s = StatusSocket()

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # -- Perform bot actions here --
            # Code within this block will LOOP until the bot is stopped.
            self.make_potion()
            self.bank()
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()


    def bank(self):
        self.verify_mouse_position(clr.YELLOW, "U")
        self.mouse.click()

        while ocr.find_text("Giel", self.win.game_view, ocr.PLAIN_12, clr.ORANGE) is False:
            time.sleep(.1)

        time.sleep(1)

        self.mouse.move_to(self.win.inventory_slots[random.randint(0, 3)].random_point())   

        self.mouse.click()

        while self.api_m.get_if_item_in_inv(ids.GUTHIX_REST3):
            time.sleep(.1)
        time.sleep(random.uniform(.2, .5))

        self.mouse.move_to(self.win.bank_slots[0].random_point())
        self.mouse.click()

        while self.api_m.get_if_item_in_inv(ids.CUP_OF_HOT_WATER) is False:
            time.sleep(.1)
    
        self.mouse.move_to(self.win.bank_slots[8].random_point())
        self.mouse.click()

        while self.api_m.get_if_item_in_inv(ids.GUAM_LEAF) is False:
            time.sleep(.1)
    
        self.mouse.move_to(self.win.bank_slots[16].random_point())
        self.mouse.click()

        while self.api_m.get_if_item_in_inv(ids.HARRALANDER) is False:
            time.sleep(.1)
    
        self.mouse.move_to(self.win.bank_slots[24].random_point())
        self.mouse.click()

        while self.api_m.get_if_item_in_inv(ids.MARRENTILL) is False:
            time.sleep(.1)
        
        time.sleep(random.uniform(.1, .5))
        self.mouse.move_to(self.win.close_bank_button.random_point())
        self.mouse.click()
        time.sleep(random.uniform(.4, .8))
    

    def make_potion(self):
        random_inv_slot = 0
        roll = random.uniform(0, 1)

        if roll <= .33:
            random_inv_slot = 4
        elif roll > .33 and roll <= 66:
            random_inv_slot = 1

        self.find_inv_and_click(random_inv_slot, "Cup")
        time.sleep(random.uniform(.3, .6))
        self.find_inv_and_click(5, "Guam")

        image_path = self.GUTHIX_REST_IMAGES.joinpath("guthix_tea.png")
        tea = imsearch.search_img_in_rect(image_path, self.win.chat, confidence=0.10)

        while tea is None:
            tea = imsearch.search_img_in_rect(image_path, self.win.chat, confidence=0.10)
            time.sleep(.1)

        time.sleep(1)

        pyautogui.press('space')

        if random.random() <= .50:
            pass
        else:
            self.move_off_screen()

        while self.api_m.get_if_item_in_inv(ids.GUAM_LEAF):
            time.sleep(.1)

        time.sleep(random.uniform(0, 10))

    def move_off_screen(self):
        if random.random() < .50:
            self.mouse.move_to(self.win.game_view.point_to_left_side())
        else:
            self.mouse.move_to(self.win.chat.point_to_left_side())
    
    def find_inv_and_click(self, inv_slot, over_text, wrong_text="filler"):
        self.mouse.move_to(self.win.inventory_slots[inv_slot].random_point())
        if self.mouseover_text(wrong_text) is False:
            while self.mouseover_text(over_text) is False:
                self.mouse.move_to(self.win.inventory_slots[inv_slot].random_point())
                time.sleep(.1)
            self.mouse.click()
        else: 
            print("Wrong text")

    def verify_mouse_position(self, col, overtext, toLeft=False):
        start = time.time()
        rectangle = self.get_nearest_tag(col)
        while rectangle is None:
            self.move_off_screen()
            rectangle = self.get_all_tagged_in_rect(col)
            time.sleep(.5)
        if toLeft is False:
            self.mouse.move_to(rectangle.random_point())
        else:
            self.mouse.move_to(rectangle.point_left_outside(x_offset = random.randint(1, 30)))
        while self.mouseover_text(overtext) is False:
            if time.time() - start >= 30:
                break
            else:
                if toLeft is False:

                    self.mouse.move_to(rectangle.random_point())
                else:
                    self.mouse.move_to(rectangle.point_left_outside(x_offset = random.randint(1, 30)))
            time.sleep(.1)

