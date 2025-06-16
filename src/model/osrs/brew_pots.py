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



class Brew_Pot(OSRSBot):
    def __init__(self):
        bot_title = "Brew Pot"
        description = "Brew Pot"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 1
        self.end_timer = 0
        self.api_m = MorgHTTPSocket()
        self.primary = ids.RANARR_POTION_UNF
        self.secondary = ids.SNAPE_GRASS
        self.pot_brewed = ids.PRAYER_POTION3
        self.BREW_POT_IMAGES = imsearch.BOT_IMAGES.joinpath("for_scripts", "brew_pot")


    def create_options(self):
        """
        Use the OptionsBuilder to define the options for the bot. For each function call below,
        we define the type of option we want to create, its key, a label for the option that the user will
        see, and the possible values the user can select. The key is used in the save_options function to
        unpack the dictionary of options after the user has selected them.
        """
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 700)
        self.options_builder.add_dropdown_option("brew_choice", "Select Brew Choice", ["Prayer"])

    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False.
        """
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "brew_choice":
                self.brew_choice = options[option]
                self.log_msg(f"Log Choice: {self.brew_choice}")
                if self.brew_choice == "Prayer":
                    self.primary = ids.RANARR_POTION_UNF
                    self.secondary = ids.SNAPE_GRASS
                    self.pot_brewed = ids.PRAYER_POTION3
                else:
                    self.log_msg(f"Unknown choice: {self.pot_brewed}")
                    self.options_set = False
                    return
            else:
                self.log_msg(f"Unkown option: {option}")
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
        self.end_timer = time.time() + (random.uniform(90, 120) * 60)
        while time.time() - start_time < end_time:
            # -- Perform bot actions here --
            # Code within this block will LOOP until the bot is stopped.
            self.brew_pot()
            time.sleep(random.uniform(0.0, 9))
            self.bank()

            if time.time() >= self.end_timer:
                self.logout_break(45, 65)
                self.end_timer = time.time() + (random.uniform(90, 120) * 60)

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def brew_pot(self):
        probability = random.uniform(0.75, 0.85) 
        if random.random() < probability:
            self.verify_mouse_position(self.win.inventory_slots[13], "Ran")
            self.mouse.click()
            time.sleep(random.uniform(0.3, 0.8))
            self.verify_mouse_position(self.win.inventory_slots[14], "Snap")
            self.mouse.click()
            time.sleep(random.uniform(0.3, 0.8))
            image_path = self.BREW_POT_IMAGES.joinpath("brew.png")
            chat_prompt = imsearch.search_img_in_rect(image_path, self.win.chat, confidence=0.5)
        else:
            self.verify_mouse_position(self.win.inventory_slots[14], "Snap")
            self.mouse.click()
            time.sleep(random.uniform(0.3, 0.8))
            self.verify_mouse_position(self.win.inventory_slots[13], "Ran")
            self.mouse.click()
            time.sleep(random.uniform(0.3, 0.8))
            image_path = self.BREW_POT_IMAGES.joinpath("brew.png")
            chat_prompt = imsearch.search_img_in_rect(image_path, self.win.chat, confidence=0.5)

        while chat_prompt is None:
            chat_prompt = imsearch.search_img_in_rect(image_path, self.win.chat, confidence=0.5)
            time.sleep(0.1)
        
        time.sleep(random.uniform(0.5, 0.6))

        pyautogui.press('space')

        if random.random() < .50:
            self.mouse.move_to(self.win.game_view.point_to_left_side())
        else:
            self.mouse.move_to(self.win.chat.point_to_left_side())

        counter = 0
        still_crafting = True
        ing_left = self.api_m.get_non_stackable_item_count(self.primary)
        while self.api_m.get_if_item_in_inv(self.primary) and still_crafting:
            if ing_left == self.api_m.get_non_stackable_item_count(self.primary):
                counter += 1
            else:
                ing_left = self.api_m.get_non_stackable_item_count(self.primary)
                counter = 0

            if counter == 5:
                still_crafting = False
            time.sleep(1)
        
        if still_crafting == False:
            prim_position = self.api_m.get_inv_item_indices(self.primary)
            sec_position = self.api_m.get_inv_item_indices(self.secondary)

            self.verify_mouse_position(self.win.inventory_slots[random.choice(prim_position)], "Ran")
            self.mouse.click()
            time.sleep(random.uniform(.3, .6))
            self.verify_mouse_position(self.win.inventory_slots[random.choice(sec_position)], "Snap")
            self.mouse.click()
            time.sleep(random.uniform(.3, .6))
            while chat_prompt is None:
                chat_prompt = imsearch.search_img_in_rect(image_path, self.win.chat, confidence=0.5)
                time.sleep(0.1)
        
            time.sleep(random.uniform(4, 6))

            pyautogui.press('space')

            while self.api_m.get_if_item_in_inv(self.primary):
                time.sleep(.1)

    def bank(self):
        self.verify_mouse_position(self.get_nearest_tag(clr.YELLOW), "Bank")
        self.mouse.click()
        while ocr.find_text("Bank", self.win.game_view, ocr.PLAIN_12, clr.ORANGE) is False:
            time.sleep(.1)
        time.sleep(random.uniform(0.6, 0.8))

        pots = self.api_m.get_inv_item_indices(self.pot_brewed)
        probability = random.uniform(0.85, 0.95) 
        if random.random() < probability:
            self.verify_mouse_position(self.win.inventory_slots[0], "Pray")
        else:
            self.verify_mouse_position(self.win.inventory_slots[random.choice(pots)], "Pray")

        self.mouse.click()
        while self.api_m.get_if_item_in_inv(self.pot_brewed):
            time.sleep(.1)
        if random.random() < random.uniform(.75, 85):
            self.verify_mouse_position(self.win.bank_slots[0], "Ran")
            self.mouse.click()
            while self.api_m.get_if_item_in_inv(self.primary) is False:
                time.sleep(.1)
            self.verify_mouse_position(self.win.bank_slots[8], "Snap")
            self.mouse.click()
            while self.api_m.get_if_item_in_inv(self.secondary) is False:
                time.sleep(.1)
        else:
            self.verify_mouse_position(self.win.bank_slots[8], "Snap")
            self.mouse.click()
            while self.api_m.get_if_item_in_inv(self.secondary) is False:
                time.sleep(.1)
            self.verify_mouse_position(self.win.bank_slots[0], "Pray")
            self.mouse.click()
            while self.api_m.get_if_item_in_inv(self.primary) is False:
                time.sleep(.1)

        self.verify_mouse_position(self.win.close_bank_button, "Close")
        self.mouse.click()
        while ocr.find_text("Bank", self.win.game_view, ocr.PLAIN_12, clr.ORANGE):
            time.sleep(.1)


    def verify_mouse_position(self, rectangle, overtext):
        while self.mouseover_text(overtext) is False:
            self.mouse.move_to(rectangle.random_point())