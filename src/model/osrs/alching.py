import random
import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
import utilities.imagesearch as imsearch



class Alching(OSRSBot):
    def __init__(self):
        bot_title = "Alching"
        description = "Alch item"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 1
        self.api_m = MorgHTTPSocket()
        self.ALCH_IMAGES = imsearch.BOT_IMAGES.joinpath("for_scripts", "alching")


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
        start_before_break = time.time()
        end_time = self.running_time * 60
        image_path = self.ALCH_IMAGES.joinpath("high_alch.png")
        high_alch = imsearch.search_img_in_rect(image_path, self.win.control_panel, confidence=0.10)
        while time.time() - start_time < end_time:
            # -- Perform bot actions here --
            # Code within this block will LOOP until the bot is stopped. slot 18

            counter = random.randint(1, 8)
            index = 0
            point_alch = high_alch.random_point()

            while index < counter:
                image_path2 = self.ALCH_IMAGES.joinpath("in_mage.png")    
                in_mage = imsearch.search_img_in_rect(image_path2, self.win.control_panel, confidence=0.10)
                while in_mage is None:
                    print("waiting for in mage book")
                    in_mage = imsearch.search_img_in_rect(image_path2, self.win.control_panel, confidence=.10)
                    time.sleep(.1)
                
                self.mouse.move_to(point_alch) 
                self.mouse.click()
                image_path3 = self.ALCH_IMAGES.joinpath("in_inv.png")      
                in_inv = imsearch.search_img_in_rect(image_path3, self.win.control_panel, confidence=.10)
                while in_inv is None:
                    print("waiting for in inventory")
                    in_inv = imsearch.search_img_in_rect(image_path3, self.win.control_panel, confidence=.10)
                    time.sleep(.1)
                
                time.sleep(.3)
                
                self.mouse.click()
                index += 1
                print(index)

            self.update_progress((time.time() - start_time) / end_time)

            if time.time() - start_before_break > random.uniform(4500, 5500):
                time.sleep(random.uniform(450, 750))
                start_before_break = time.time()

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()
