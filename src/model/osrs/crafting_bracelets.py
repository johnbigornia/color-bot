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



class Crafting_Bracelets(OSRSBot):
    def __init__(self):
        bot_title = "Craft Bracelets"
        description = "Craft diamond bracelets"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 1
        self.api_m = MorgHTTPSocket()
        self.CRAFT_BRACELET_IMAGES = imsearch.BOT_IMAGES.joinpath("for_scripts", "craft_bracelet")


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
            elif option == "text_edit_example":
                self.log_msg(f"Text edit example: {options[option]}")
            elif option == "multi_select_example":
                self.log_msg(f"Multi-select example: {options[option]}")
            elif option == "menu_example":
                self.log_msg(f"Menu example: {options[option]}")
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
            self.craft_bracelet()
            self.bank()
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()
        self.logout()

    def craft_bracelet(self):
        print("Looking for smith")
        self.verify_mouse_position(self.get_nearest_tag(clr.BLUE), "Smelt")
        while self.mouse.click(check_red_click=True) == False:
            self.verify_mouse_position(self.get_nearest_tag(clr.BLUE), "Smelt")
            time.sleep(.1)

        print("found smith")
        image_path = self.CRAFT_BRACELET_IMAGES.joinpath("craft_menu.png")
        chat_prompt = imsearch.search_img_in_rect(image_path, self.win.game_view, confidence=0.10)


        while chat_prompt is None:
            chat_prompt = imsearch.search_img_in_rect(image_path, self.win.game_view, confidence=0.10)
            time.sleep(0.1)

        print("chat prompt up")
        
        time.sleep(random.uniform(0.7, 0.99))

        pyautogui.press('space')

        if random.random() < .50:
            self.mouse.move_to(self.win.game_view.point_to_left_side())
        else:
            self.mouse.move_to(self.win.chat.point_to_left_side())

        counter = 0
        diamonds_left = self.api_m.get_non_stackable_item_count(ids.DIAMOND)
        while self.api_m.get_if_item_in_inv(ids.DIAMOND):
            if diamonds_left == self.api_m.get_non_stackable_item_count(ids.DIAMOND):
                counter += 1
            else:
                diamonds_left = self.api_m.get_non_stackable_item_count(ids.DIAMOND)
                counter = 0

            if counter == 5:
                counter = 0
                self.verify_mouse_position(self.get_nearest_tag(clr.BLUE), "Smelt")
                while self.mouse.click(check_red_click=True) == False:
                    self.verify_mouse_position(self.get_nearest_tag(clr.BLUE), "Smelt")
                    time.sleep(.1)
                image_path = self.CRAFT_BRACELET_IMAGES.joinpath("craft_menu.png")
                chat_prompt = imsearch.search_img_in_rect(image_path, self.win.game_view, confidence=0.10)


                while chat_prompt is None:
                    chat_prompt = imsearch.search_img_in_rect(image_path, self.win.game_view, confidence=0.10)
                    time.sleep(0.1)
                
                time.sleep(random.uniform(0.5, 0.6))

                pyautogui.press('space')

                if random.random() < .50:
                    self.mouse.move_to(self.win.game_view.point_to_left_side())
                else:
                    self.mouse.move_to(self.win.chat.point_to_left_side())

            time.sleep(1)
        
        print("Done Crafting")
        time.sleep(random.uniform(4, 13))

    def bank(self):
        self.verify_mouse_position(self.get_nearest_tag(clr.YELLOW), "Bank")
        
        while self.mouse.click(check_red_click=True) is False:
            self.verify_mouse_position(self.get_nearest_tag(clr.YELLOW), "Bank")
            time.sleep(1)
        time.sleep(1)
        while ocr.find_text("Giel", self.win.game_view, ocr.PLAIN_12, clr.ORANGE) is False:
            time.sleep(.1)

        bracelet = self.api_m.get_inv_item_indices(ids.DIAMOND_BRACELET)
        time.sleep(4)
        probability = random.uniform(0.85, 0.95) 
        if random.random() < probability:
            self.verify_mouse_position(self.win.inventory_slots[1], "Diamond")
        else:
            self.verify_mouse_position(self.win.inventory_slots[random.choice(bracelet)], "Diamond")

        self.mouse.click()
        while self.api_m.get_if_item_in_inv(ids.DIAMOND_BRACELET):
            time.sleep(.1)
        print("Banked bracelets")
        if random.random() < random.uniform(.75, 85):
            self.verify_mouse_position(self.win.bank_slots[0], "Gold")
            self.mouse.click()
            while self.api_m.get_if_item_in_inv(ids.GOLD_BAR) is False:
                time.sleep(.1)
            self.verify_mouse_position(self.win.bank_slots[8], "Diamond")
            self.mouse.click()
            while self.api_m.get_if_item_in_inv(ids.DIAMOND) is False:
                time.sleep(.1)
        else:
            self.verify_mouse_position(self.win.bank_slots[8], "Diamond")
            self.mouse.click()
            while self.api_m.get_if_item_in_inv(ids.DIAMOND) is False:
                time.sleep(.1)
            self.verify_mouse_position(self.win.bank_slots[0], "Gold")
            self.mouse.click()
            while self.api_m.get_if_item_in_inv(ids.GOLD_BAR) is False:
                time.sleep(.1)

        self.verify_mouse_position(self.win.close_bank_button, "Close")
        self.mouse.click()
        while ocr.find_text("Bank", self.win.game_view, ocr.PLAIN_12, clr.ORANGE):
            time.sleep(.1)

        print("done banking")

    def verify_mouse_position(self, rectangle, overtext):
        while self.mouseover_text(overtext) is False:
            self.mouse.move_to(rectangle.random_point())
            time.sleep(.1)