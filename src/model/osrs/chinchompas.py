import random
import time

from utilities import ocr
import utilities.api.item_ids as ids
import utilities.color as clr
from utilities.geometry import Rectangle
import utilities.random_util as rd
import utilities.imagesearch as imsearch
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class Chinchompas(OSRSBot):
    def __init__(self):
        self.CHINCHOMPA_HUNTER_IMAGES = imsearch.BOT_IMAGES.joinpath("for_scripts", "Chinchompa_Hunter")
        bot_title = "Chinchompas"
        description = "For hunting chinchompas"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 1

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

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # -- Perform bot actions here --
            # animation id = 5208, how many ticks to wait?

            self.check_dropped_box()
            self.check_box(clr.BLUE, 4)
            self.check_box(clr.RED, 3)
                
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def check_box(self, color_highlight, max_counter):
        counter = 0
        is_waiting = True
        while self.get_nearest_tag(color=color_highlight) and counter < max_counter:
            # Should include a wait in here for how long we should wait until we move on to the next
            self.check_dropped_box()
            box_with_chin = self.get_nearest_tag(color_highlight)
            self.mouse.move_to(box_with_chin.random_point())
            timer = 0
            while is_waiting:
                if self.mouseover_text("Reset", color=clr.WHITE) is False:
                    box_with_chin = self.get_nearest_tag(color_highlight)
                    if box_with_chin != None:
                        self.mouse.move_to(box_with_chin.random_point())
                timer += .25
                time.sleep(.01)
                if timer >= 1:
                    is_waiting = False
            self.mouse.click()
            self.random_mouse_movement(self.win.game_view)
            self.wait_for_animation()
            counter+=1
    
    def wait_for_animation(self):
        is_waiting = True
        start_time = time.time()  # Record the start time
        timeout = 5  # Set the timeout duration in seconds
        time.sleep(0.6)
        while is_waiting:
            if ocr.find_text("08", self.win.game_view, ocr.PLAIN_11, clr.WHITE):
                time.sleep(random.uniform(2.029048520, 2.22394870))
                is_waiting = False
            elif time.time() - start_time > timeout:
                # If more than 5 seconds have passed, exit the loop
                is_waiting = False
            else:
                time.sleep(0.01)  # Optional: add a short sleep to prevent CPU overuse

    def check_dropped_box(self):
        is_waiting = True
        image_path = self.CHINCHOMPA_HUNTER_IMAGES.joinpath("dropped_box.png")
        if imsearch.search_img_in_rect(image_path, self.win.game_view, confidence=.05) is not None:
            dropped_box = imsearch.search_img_in_rect(image_path, self.win.game_view)
            self.mouse.move_to(dropped_box.random_point())
            timer = 0
            while is_waiting:
                if self.mouseover_text("Lay", color=clr.WHITE) is False:
                    dropped_box = imsearch.search_img_in_rect(image_path, self.win.game_view)
                    if dropped_box != None:
                        self.mouse.move_to(dropped_box.random_point())
                timer += .25
                time.sleep(.01)
                if timer >= 1:
                    is_waiting = False
            self.mouse.click()
            self.random_mouse_movement(self.win.game_view)
            self.wait_for_animation()

    def random_mouse_movement(self, rect: Rectangle):
        """
        Randomly moves the mouse in one of the specified ways:
        - move_around_center (most likely)
        - no movement (second most likely)
        - move_to_left_side (least likely)
        """
        choices = ['move_around_center', 'no_move', 'move_to_left_side']
        weights = [0.85, 0.10, 0.05] 
        choice = random.choices(choices, weights=weights, k=1)[0]

        if choice == 'move_around_center':
            self.mouse.move_to(rect.point_around_center())
        elif choice == 'move_to_left_side':
            self.mouse.move_to(rect.point_to_left_side())
            time.sleep(random.uniform(1.2, 3.8))
        else:
            pass