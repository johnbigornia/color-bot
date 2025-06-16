import time

import cv2

import utilities.api.item_ids as ids
import utilities.color as clr
from utilities.geometry import Rectangle
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
import utilities.imagesearch as imsearch
from utilities import ocr


class Mixology(OSRSBot):
    def __init__(self):
        bot_title = "Mixology"
        description = "Mixology bot"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 1
        self.api_m = MorgHTTPSocket()
        self.base_potion_full_text = ["Alco-augmentator", "Mammoth-might mix", "Liplack liquor", "Mystic mana amalgam", "Marley's moonlight", "Azure aura mix", "Aqualux amalgam", "Megalite liquid", "Anti-leech lotion", "Mixalot"]
        self.base_potion = {"AAA": [30014, 30024], "MMM": [30011, 30021], "LLL": [30017, 30027], "MMA": [30012, 30022], "MML": [30013, 30023], "AAM": [30016, 30026], "ALA": [30015, 30025], "MLL": [30019, 30029], "ALL": [30018, 30028], "MAL": [30020, 30030]}
        self.mixology_corner = None
        self.MIXOLOGY_IMAGES = imsearch.BOT_IMAGES.joinpath("for_scripts", "mixology")
        self.pots_queue = []
        self.pots_to_brew = []
        self.mixology_pots = Rectangle(9, 46, 204, 129)

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
            self.determine_potions()
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def determine_potions(self):
        self.pots_queue = []  # Use a list to collect potion entries

        # Get the keys in order from the base_potion dictionary
        potion_keys = list(self.base_potion.keys())

        for index, potion_text in enumerate(self.base_potion_full_text):
            temp = ocr.find_text(potion_text, self.mixology_pots, ocr.PLAIN_12, clr.WHITE)
            if not temp:
                print(f"No text found for: {potion_text}")
            else:
                key = potion_keys[index]   # Get the corresponding key (e.g., "AAA")
                value = self.base_potion[key]  # Get the associated potion IDs
                # For each occurrence found, add the key and value to the queue
                for _ in range(len(temp)):
                    # You can choose how to store it. Here we're storing as a tuple:
                    self.pots_queue.append((key, value))

        count_AAA = sum(1 for entry in self.pots_queue if entry[0] == "AAA")

        total_weight = self.calculate_total_weight(self.pots_queue)

        self.pots_to_brew = []

        if any(entry[0] == "MAL" for entry in self.pots_queue):
            self.pots_to_brew = self.pots_queue.copy()
        elif count_AAA == 3:
            self.pots_to_brew.append[self.pots_queue[0]]
        elif count_AAA == 2:
            non_AAA = [entry for entry in self.pots_queue if entry[0] != "AAA"]
            if non_AAA:  # should be exactly one
                self.pots_to_brew.append(non_AAA[0])
        elif count_AAA == 1:
            if total_weight >= 14:
                self.pots_to_brew = self.pots_queue.copy()
            else:
                for entry in self.pots_queue:
                    if entry[0] != "AAA":
                        self.pots_to_brew.append(entry)
        else:
            self.pots_to_brew = self.pots_queue.copy()
        
        print(self.pots_to_brew)
        time.sleep(40)
        
    def calculate_total_weight(self, pots: list):
        # Define the weights for each character
        weights = {'L': 3, 'M': 2, 'A': 1}

        # Example pots_queue with three tuples; each key is a 3-letter string.
        # For instance, pots_queue might be:
        # pots_queue = [("MAL", [30020, 30030]), ("AAA", [30014, 30024]), ("LLL", [30017, 30027])]

        total_weight = 0

        for entry in pots:
            key = entry[0]  # get the key string (e.g., "MAL")
            # Calculate the weight for the current key
            key_weight = sum(weights[char] for char in key)
            print(f"Weight of {key} is: {key_weight}")
            total_weight += key_weight
        return total_weight