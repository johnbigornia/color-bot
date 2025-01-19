import random
import time

from utilities import ocr
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class Tithe_Farm(OSRSBot):
    def __init__(self):
        bot_title = "Tithe Farm"
        description = "Tithe bot"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 1
        self.api_m = MorgHTTPSocket()
        self.plant_loc = [
            clr.COLOR_1,
            clr.COLOR_2,
            clr.COLOR_3,
            clr.COLOR_4,
            clr.COLOR_5,
            clr.COLOR_6,
            clr.COLOR_7,
            clr.COLOR_8,
            clr.COLOR_9,
            clr.COLOR_10,
            clr.COLOR_11,
            clr.COLOR_12,
            clr.COLOR_13,
            clr.COLOR_14,
            clr.COLOR_15,
            clr.COLOR_16,
            clr.COLOR_17,
            clr.COLOR_18,
            clr.COLOR_19,
            clr.COLOR_20,
        ]

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
            # -- Perform bot actions here -- 2291 for seed ani and 2293 for water ani
            # Code within this block will LOOP until the bot is stopped.
            self.plant_seeds()
            self.water_plants()
            self.water_plants()
            self.harvest()
            self.refill()
            
            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()


    def plant_seeds(self):
        seed_index = self.api_m.get_inv_item_indices(ids.LOGAVANO_SEED)
        seed_loc = self.win.inventory_slots[seed_index[0]]
        for loc in self.plant_loc:
            self.verify_mouse_position(seed_loc, "Use")
            self.mouse.click()
            self.find_object_and_click(loc, "Use")
            fruit_seed = self.api_m.get_inv_item_stack_amount(ids.LOGAVANO_SEED)
            while self.api_m.get_inv_item_stack_amount(ids.LOGAVANO_SEED) == fruit_seed:
                time.sleep(.01)

            water_can = self.find_most_water_in_can()
            self.verify_mouse_position(water_can[0], "Use")
            self.mouse.click()
            self.find_object_and_click(loc, "Use")
            while self.api_m.is_item_in_slot(water_can[1], water_can[2]):
                time.sleep(0.5)
            

    def water_plants(self):
        for loc in self.plant_loc:
            water_can = self.find_most_water_in_can()
            self.verify_mouse_position(water_can[0], "Use")
            self.mouse.click()
            self.find_object_and_click(loc, "ter")
            while self.api_m.is_item_in_slot(water_can[1], water_can[2]):
                time.sleep(0.5)

    def harvest(self):
        time.sleep(.6)
        for loc in self.plant_loc:
            self.find_object_and_click(loc, "Harvest")
            fruit = self.api_m.get_inv_item_stack_amount(ids.LOGAVANO_FRUIT)
            counter = 0
            while self.api_m.get_inv_item_stack_amount(ids.LOGAVANO_FRUIT) == fruit:
                if self.api_m.get_inv_item_stack_amount(ids.LOGAVANO_FRUIT) == fruit:
                    counter += 1
                print(counter)
                if counter >= 250:
                    self.mouse.move_to(self.win.control_panel.random_point())
                    self.find_object_and_click(loc, "Harvest")
                    counter = 0
                time.sleep(.01)

    def refill(self):
        self.verify_mouse_position(self.win.inventory_slots[0], "Use")
        self.mouse.click()

        barrel = self.get_nearest_tag(clr.BLUE)

        while barrel is None:
            barrel = self.get_nearest_tag(clr.BLUE)

        self.verify_mouse_position(barrel, "Use")
        self.mouse.click()

        if random.random() < .5:
            self.mouse.move_to(self.win.game_view.point_to_left_side())
        else:
            self.mouse.move_to(self.win.chat.point_to_left_side())

        while len(self.api_m.get_inv_item_indices(ids.WATERING_CAN8)) < 8:
            time.sleep(.1)

        if random.random() < .95:
            time.sleep(random.uniform(1.2, 15))



    def find_most_water_in_can(self):
        # Define a list of watering can IDs in descending order of water amount
        watering_can_ids = [
            ids.WATERING_CAN8,
            ids.WATERING_CAN7,
            ids.WATERING_CAN6,
            ids.WATERING_CAN5,
            ids.WATERING_CAN4,
            ids.WATERING_CAN3,
            ids.WATERING_CAN2,
            ids.WATERING_CAN1
        ]
        
        # Iterate over the watering can IDs to find the one with the highest water level
        for watering_can_id in watering_can_ids:
            if self.api_m.get_if_item_in_inv(watering_can_id):
                # Get the inventory location of the watering can
                watering_can_loc = self.win.inventory_slots[self.api_m.get_first_occurrence(watering_can_id)]
                return [watering_can_loc, self.api_m.get_first_occurrence(watering_can_id), watering_can_id]
        
        # Return None if no watering can is found
        return None

    def find_object_and_click(self, color: clr, over_text="", timeout=5):
        obj = self.get_nearest_tag(color)
        start_time = time.time()

        # Wait for the object to be found
        while obj is None:
            self.mouse.move_to(self.win.chat.random_point())
            obj = self.get_nearest_tag(color)
            if time.time() - start_time > timeout:
                self.log_msg("Timeout reached while waiting for object. Proceeding without finding object.")
                break
            time.sleep(0.1)

        if obj is not None:
            self.mouse.move_to(obj.random_point())

        # Handle text checking
        if over_text != "" and over_text != "ignore":
            start_time = time.time()
            while self.mouseover_text(over_text) is False:
                obj = self.get_nearest_tag(color)
                if obj is None:
                    self.mouse.move_to(self.win.chat.random_point())

                if time.time() - start_time > timeout:
                    self.log_msg("Timeout reached while checking text. Clicking anyway.")
                    break
                if obj is not None:
                    self.mouse.move_to(obj.random_point())
                time.sleep(0.1)

        # Perform the click
        if self.mouse.click(check_red_click=True) is False and over_text != "ignore":
            self.find_object_and_click(color, over_text)

    def find_text_and_click(self, text, text_action):
        text_area = ocr.find_text(text, self.win.game_view, ocr.PLAIN_11, clr.YELLOW)

        while not text_area:
            self.mouse.move_to(self.win.control_panel.random_point())
            text_area = ocr.find_text(text, self.win.game_view, ocr.PLAIN_11, clr.YELLOW)
            time.sleep(.1)

        self.mouse.move_to(text_area[0].random_point())
        while self.mouseover_text(text_action) is False:
            self.mouse.move_to(text_area[0].random_point())
            time.sleep(.1)
        self.mouse.click()

    def verify_mouse_position(self, rectangle, overtext):
        self.mouse.move_to(rectangle.random_point())
        while self.mouseover_text(overtext) is False:
            self.mouse.move_to(rectangle.random_point())