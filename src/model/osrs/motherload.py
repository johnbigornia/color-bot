import random
import time
import traceback

from utilities import ocr
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
import utilities.imagesearch as imsearch


class Motherload(OSRSBot):
    def __init__(self):
        bot_title = "Motherload"
        description = "mine some shit"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 1
        self.api_m = MorgHTTPSocket()
        self.MOTHERLOAD_IMAGES = imsearch.BOT_IMAGES.joinpath("for_scripts", "motherload")


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

            for i in range(3):
                self.mine_loop()
                if i < 2:
                    self.mine()
                self.move_off_screen()
            
            self.deposit_ores()
            self.verify_mouse_position(clr.CYAN, "Climb", toLeft=True)
            self.mouse.click()
            time.sleep(random.uniform(10, 12))
            self.mine()
            self.move_off_screen()
    

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def mine(self):
        try:
            self.verify_mouse_position(clr.YELLOW, "M")
            self.mouse.click()
        except Exception as e:
            print(f"An error occured trying to mine: {e}")
            traceback.print_exc()

    
    def mine_loop(self):
        start_mining_xp = self.api_m.get_skill_xp("Mining")
        start_time = time.time()
        while self.api_m.get_is_inv_full() is False:
            if time.time() - start_time >= 15:
                if start_mining_xp == self.api_m.get_skill_xp("Mining"):
                    time.sleep(random.uniform(0, 9))
                    self.mine()
                    self.move_off_screen()
                else:
                    start_mining_xp = self.api_m.get_skill_xp("Mining")
                    print("Still mining")
                start_time = time.time()
            time.sleep(.1)
        
        ore_deposit = self.get_nearest_tag(clr.GREEN)
        if ore_deposit is None:
            self.mouse.move_to(self.win.control_panel.random_point())
            time.sleep(4)
        self.verify_mouse_position(clr.GREEN, "Dep")
        self.mouse.click()
        while self.api_m.get_is_inv_full():
            time.sleep(.1)
            

    def deposit_ores(self):
        try:
            self.verify_mouse_position(clr.CYAN, "Climb")
            self.mouse.click()
            time.sleep(random.uniform(4, 6))
            for i in range(3):
                loot = self.get_nearest_tag(clr.BLUE)
                if loot is None:
                    self.mouse.move_to(self.get_nearest_tag(clr.WEST))
                    self.mouse.click()
                    time.sleep(random.uniform(5,7))
                    
                strut = self.get_nearest_tag(clr.RED)
                if strut is not None:
                    self.repair_strut()
                self.verify_mouse_position(clr.BLUE, "Search")
                self.mouse.click()
                start_time=time.time()
                while len(self.api_m.get_inv()) < 10:
                    if time.time() - start_time >= 7:
                        bag = self.get_nearest_tag(clr.BLUE)
                        if bag is None:
                            print("Bag empty")
                        else:
                            self.verify_mouse_position(clr.BLUE, "Search")
                            self.mouse.click()

                        start_time = time.time()
                    time.sleep(.1)
                time.sleep(1)
                self.verify_mouse_position(clr.COLOR_4, "Dep")
                self.mouse.click()
                start_time = time.time()
                while ocr.find_text("Giel", self.win.game_view, ocr.PLAIN_12, clr.ORANGE) is False:
                    if time.time() - start_time > 5:
                        self.verify_mouse_position(clr.COLOR_4, "Dep")
                        self.mouse.click()
                    print("in loooop")
                    time.sleep(.1)

                image_path = self.MOTHERLOAD_IMAGES.joinpath("Deposit_all.png")
                dep_all = imsearch.search_img_in_rect(image_path, self.win.game_view, confidence=0.10)
                while dep_all is None:
                    dep_all = imsearch.search_img_in_rect(image_path, self.win.game_view, confidence=0.10)

                self.mouse.move_to(dep_all.random_point())
                self.mouse.click()
                image_path = self.MOTHERLOAD_IMAGES.joinpath("close.png")
                close = imsearch.search_img_in_rect(image_path, self.win.game_view, confidence=.10)
                time.sleep(1)
                self.mouse.move_to(close.random_point())
                self.mouse.click()
                while close is not None:
                    close = imsearch.search_img_in_rect(image_path, self.win.game_view, confidence=.10)
        except Exception as e:
            print(f"Error occured: {e}")
            traceback.print_exc()

    def repair_strut(self):
        strut = self.get_nearest_tag(clr.RED)
        while strut is not None:
            self.verify_mouse_position(clr.RED, "Ham")
            self.mouse.click()
            start_smithing_xp = self.api_m.get_skill_xp("Smithing")
            time_start = time.time()
            while start_smithing_xp == self.api_m.get_skill_xp("Smithing"):
                if time.time() - time_start >= 15:
                    strut = self.get_nearest_tag(clr.RED)
                    if strut is None:
                        break
                    else:
                        self.verify_mouse_position(clr.RED, "Ham")
                        self.mouse.click()
                        time_start = time.time()
                time.sleep(.1)
            strut = self.get_nearest_tag(clr.RED)

        time.sleep(5)


    def verify_mouse_position(self, color, overtext, toLeft=False):
        try:
            start = time.time()
            rectangle = self.get_nearest_tag(color)
            if toLeft is False:
                self.mouse.move_to(rectangle.random_point())
            else:
                self.mouse.move_to(rectangle.point_left_outside(x_offset = random.randint(1, 30)))
            while self.mouseover_text(overtext) is False:
                rectangle = self.get_nearest_tag(color)
                if time.time() - start >= 30:
                    break
                else:
                    if toLeft is False:
                        self.mouse.move_to(rectangle.random_point())
                    else:
                        self.mouse.move_to(rectangle.point_left_outside(x_offset = random.randint(1, 30)))
                time.sleep(.1)
        except Exception as e:
            print(f"verify failed for mouse position for the following highlight: {overtext} : {e}")

    def move_off_screen(self):
        if random.random() < .50:
            self.mouse.move_to(self.win.game_view.point_to_left_side())
        else:
            self.mouse.move_to(self.win.chat.point_to_left_side())