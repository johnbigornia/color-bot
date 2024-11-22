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


class Fletching(OSRSBot):
    def __init__(self):
        bot_title = "Fletching"
        description = "Fletch items"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 1
        self.log_id = ids.YEW_LOGS
        self.bow_id = ids.YEW_LONGBOW
        self.api_m = MorgHTTPSocket()
        self.end_timer = 0

    def create_options(self):
        """
        Use the OptionsBuilder to define the options for the bot. For each function call below,
        we define the type of option we want to create, its key, a label for the option that the user will
        see, and the possible values the user can select. The key is used in the save_options function to
        unpack the dictionary of options after the user has selected them.
        """
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_dropdown_option("log_choice", "Select Log Choice", ["Yew Logs", "Magic Logs"])

    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False.
        """
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "log_choice":
                self.log_choice = options[option]
                self.log_msg(f"Log Choice: {self.log_choice}")
                if self.log_choice == "Yew Logs":
                    self.log_id = ids.YEW_LOGS
                    self.bow_id = ids.YEW_LONGBOW
                elif self.log_choice == "Magic Logs":
                    self.log_id = ids.MAGIC_LOGS
                    self.bow_id = ids.MAGIC_LONGBOW
                else:
                    self.log_msg(f"Unknown log choice: {self.log_choice}")
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
        # api_s = StatusSocket()

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        self.end_timer = time.time() + (random.uniform(90, 120) * 60)
        while time.time() - start_time < end_time:
            # -- Perform bot actions here --
            # Code within this block will LOOP until the bot is stopped.
            if self.api_m.get_non_stackable_item_count(self.log_id) != 0:
                self.fletch_bow()

            counter = 0
            still_crafting = True
            #checks logs that's left
            logs_left = self.api_m.get_non_stackable_item_count(self.log_id)

            while self.api_m.get_if_item_in_inv(self.log_id) is True and still_crafting:
                print('in Loop')
                if logs_left == self.api_m.get_non_stackable_item_count(self.log_id):
                    counter += 1
                else: 
                    logs_left = self.api_m.get_non_stackable_item_count(self.log_id)
                
                if counter == 4:
                    if self.api_m.get_non_stackable_item_count(self.log_id) != 0:
                        self.fletch_bow()
                    still_crafting = False 
                time.sleep(2)
            
            self.random_break(2, 5)

            if self.api_m.get_if_item_in_inv(self.log_id) is False:
                self.bank()
                if random.random() < .01:
                    self.random_break(2, 5)

            if time.time() >= self.end_timer:
                self.logout_break(45, 65)
                self.end_timer = time.time() + (random.uniform(90, 120) * 60)

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def bank(self):
        self.mouse.move_to(self.get_nearest_tag(clr.YELLOW).random_point())
        self.mouse.click()
        while ocr.find_text("Bank", self.win.game_view, ocr.PLAIN_12, clr.ORANGE) is False:
            time.sleep(.1)
        time.sleep(random.uniform(0.8, 1.2))
        self.mouse.move_to(self.win.inventory_slots[self.select_number()].random_point())
        self.mouse.click()
        while self.api_m.get_if_item_in_inv(self.bow_id):
            time.sleep(.1)
        self.mouse.move_to(self.win.bank_slots[0].random_point())
        self.mouse.click()
        while self.api_m.get_if_item_in_inv(self.log_id) is False:
            time.sleep(.1)
        self.mouse.move_to(self.win.close_bank_button.random_point())
        self.mouse.click()
        while ocr.find_text("Bank", self.win.game_view, ocr.PLAIN_12, clr.ORANGE):
            time.sleep(.1)
        time.sleep(random.uniform(0.6, 1.2))

    def fletch_bow(self):
        self.mouse.move_to(self.win.inventory_slots[0].random_point())
        self.mouse.click()

        log = self.api_m.get_inv_item_indices(self.log_id)
        if log.__contains__(1):
            probability = .95
            if random.random() < probability:
                self.mouse.move_to(self.win.inventory_slots[1].random_point())
            else:
                self.mouse.move_to(self.win.inventory_slots[random.choice(log)].random_point())
        else:
            self.mouse.move_to(self.win.inventory_slots[random.choice(log)].random_point())
        
        self.mouse.click()

        # Wait for a short random duration
        time.sleep(random.uniform(1.0, 1.4))

        # Press '3' to complete the action
        pyautogui.press('3')
        self.mouse.move_to(self.win.game_view.point_to_left_side())

    def select_number(self):
        """
        Selects the number 1 with high probability, otherwise selects a random number from 2 to 27.

        Returns:
            An integer between 1 and 27.
        """
        probability_of_one = 0.95  # 95% chance to select 1
        if random.random() < probability_of_one:
            return 1
        else:
            return random.randint(2, 27)
        
