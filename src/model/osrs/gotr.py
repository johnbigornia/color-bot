import random
import threading
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
from enum import Enum, auto


class State(Enum):
    IDLE = auto()
    STARTING = auto()
    CRAFTING_ESS = auto()
    ENTERING_PILLAR = auto()
    CRAFTING_RUNES = auto()
    GIVING_GUARDIANS = auto()
    REPAIRING_BARRIER = auto()
    DEPOSITING_RUNES = auto()
    REPAIRING_POUCH = auto()
    STUCK_IN_ALTAR = auto()
    FINISHED = auto()

class Gotr(OSRSBot):
    def __init__(self):
        bot_title = "Guardians of the Rift"
        description = "Bot for GOTR"
        self.GOTR_IMAGES = imsearch.BOT_IMAGES.joinpath("for_scripts", "Gotr")
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 1
        self.api_m = MorgHTTPSocket()

        self.restart = False #mChecked in a seperate thread, count as restarted or starting
        self.active_portal = False # Checks for portal, seperate thread
        self.game_finished = False  # Checks if game finished, seperate thread
        self.start = False
        self.reset = True
        self.current_pillar = None
        self.pillar_timer = 0.0
        self.defeated = False
        self.out_of_ess = False
        self.finding_pillar = False
        self.in_altar = False
        self.find_obj_func_count = 0
        self.state = None
            
        self.runes = {
                0: clr.AIR_PILLAR,
                1: clr.MIND_PILLAR,
                2: clr.WATER_PILLAR,
                3: clr.EARTH_PILLAR,
                4: clr.FIRE_PILLAR,
                5: clr.BODY_PILLAR,
                6: clr.COSMIC_PILLAR,
                7: clr.CHAOS_PILLAR,
                8: clr.NATURE_PILLAR,
                9: clr.LAW_PILLAR,
                10: clr.DEATH_PILLAR
            }
        
        self.portal_id = {
            0: clr.EAST,
            1: clr.SOUTHEAST,
            2: clr.SOUTH,
            3: clr.SOUTHWEST
        }
        self.first_run = True

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

        check_restart_thread = threading.Thread(target=self.check_for_restart_image)
        check_restart_thread.daemon = True
        check_restart_thread.start()

        check_pillar_thread = threading.Thread(target=self.check_current_pillar)
        check_pillar_thread.daemon = True
        check_pillar_thread.start()

        check_defeated_thread = threading.Thread(target=self.check_defeated_guardian)
        check_defeated_thread.daemon = True
        check_defeated_thread.start()

        check_if_in_altar = threading.Thread(target=self.check_location)
        check_if_in_altar.daemon = True
        check_if_in_altar.start()

        check_state = threading.Thread(target=self.state_tracker)
        check_state.daemon = True
        check_state.start()

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60

        while time.time() - start_time < end_time:
            print(f"self reset is: {self.reset}")
            if self.reset:
                self.starting()
                self.first_run = False
            start_timer = time.time()
            print(f"current restart status: {self.restart}")
            while self.restart:
                if time.time() - start_timer > 10:
                    print("Timeout reached while waiting for object. Proceeding without finding object.")
                    break
                time.sleep(.1)
            if self.restart:
                self.defeated = False
                print(f"Waiting for start: current state: {self.state}")
                self.state_handler()
                self.reset = True
                self.find_object_and_click(clr.STARTING, "ignore")
                print("Finished Handler")
                while self.start is False:
                    print(self.start)
                    start_area = self.get_nearest_tag(clr.STARTING)
                    if start_area is None:
                        try: 
                            self.mouse.move_to(self.get_nearest_tag(clr.START).random_point())
                            self.mouse.click()
                            time.sleep(4)
                            self.mouse.move_to(self.get_nearest_tag(clr.STARTING).random_point())
                            self.mouse.click()
                            time.sleep(6)
                        except:
                            print("Couldn't find start")
                    time.sleep(.1)
                self.first_run = True
                print("out of loop")
            else:
                self.main_tasks()

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()

    def state_handler(self):
        if self.in_altar:
            while self.in_altar:
                try:
                    portal = self.get_nearest_tag(clr.YELLOW)
                    if portal is None:
                        self.find_object_and_click(clr.PINK, "ignore")
                    else:
                        self.find_object_and_click(clr.YELLOW, "Enter")
                except:
                    print("Objects were none")
                
                print(f"location in altar: {self.in_altar}")
                time.sleep(1)
        
        print(f"in handler current state: {self.state}")
        if self.state == State.GIVING_GUARDIANS or self.state == State.REPAIRING_BARRIER:
            if self.runes_in_inv():
                self.deposit_runes()
        elif self.state == State.CRAFTING_RUNES:
            self.craft_runes()
            self.deposit_runes()
        print("Done handler")

    def starting(self): 
        self.reset = False
        if self.api_m.get_inv_item_stack_amount(ids.UNCHARGED_CELL) < 10:
            cell_table = self.get_nearest_tag(clr.YELLOW)
            while cell_table is None:
                self.find_object_and_click(clr.START, "ignore")
                time.sleep(2)
                cell_table = self.get_nearest_tag(clr.YELLOW)
            print("Checking uncharged cell")
            self.find_object_and_click(clr.YELLOW, "char")
        print("Clicked table")

        start_time = time.time()
        while self.api_m.get_inv_item_stack_amount(ids.UNCHARGED_CELL) < 10:
            if time.time() - start_time >= 5:
                self.find_object_and_click(clr.YELLOW, "char")
                start_time = time.time()
            time.sleep(.1)
        
        print("got uncharged cell")
        climb_area = self.get_all_tagged_in_rect(self.win.minimap, clr.GREEN)
        print("heading to mine")
        while not climb_area:
            climb_area = self.get_all_tagged_in_rect(self.win.minimap, clr.GREEN)
            time.sleep(.1)

        self.mouse.move_to(climb_area[0].random_point())
        self.mouse.click()
        time.sleep(random.uniform(8, 10))

        self.find_object_and_click(clr.CLIMB, "Rubble")

        image_path = self.GOTR_IMAGES.joinpath("start.png")
        img = imsearch.search_img_in_rect(image_path, self.win.game_view, confidence=0.10)
        while img is None:
            img = imsearch.search_img_in_rect(image_path, self.win.game_view, confidence=0.10)
            time.sleep(.1)
        time.sleep(2)
        self.find_object_and_click(clr.GREEN, "ignore")
        mine_xp_start = self.api_m.get_skill_xp("Mining")
        time.sleep(6)
        while mine_xp_start == self.api_m.get_skill_xp("Mining"):
            self.find_object_and_click(clr.GREEN, "ignore")
            time.sleep(2)
        time.sleep(random.uniform(100, 110))
        self.find_object_and_click(clr.BLUE, "b")    
        time.sleep(6)
        craft = self.get_all_tagged_in_rect(self.win.minimap, clr.BLUE)
        while not craft:
            craft = self.get_all_tagged_in_rect(self.win.minimap, clr.BLUE)
            time.sleep(.1)
        self.mouse.move_to(craft[0].random_point())
        self.mouse.click()

        time.sleep(4)

        bench = self.get_nearest_tag(clr.GREEN)
        while bench is None:
            bench = self.get_nearest_tag(clr.GREEN)
            time.sleep(.1)

        self.find_object_and_click(clr.GREEN, "Work")
        starting_xp = self.api_m.get_skill_xp("Crafting")
        counter = 0
        while self.api_m.get_is_inv_full() is False:
            if self.api_m.get_skill_xp("Crafting") == starting_xp:
                counter += 1
            else:
                counter = 0

            if counter >= 20:
                self.find_object_and_click(clr.GREEN, "Work")
                counter = 0
                starting_xp = self.api_m.get_skill_xp("Crafting")

            time.sleep(.1)

        self.out_of_ess = False

        print("1here")
        self.enter_pillar()
        print("2here")
        self.craft_runes()
        print("3here")
        self.give_guardians()
        print("4here")
        self.repair_barrier()
        print("5here")
        self.deposit_runes()

    def main_tasks(self):
        # each method will check if the game is done/theres a reset(except craft runes) then will update reset to True
        # craft ess, checks for portal

        print(f"Out of ess? {self.out_of_ess}")
        if not self.out_of_ess: 
            print("before check")
            self.check_restart()
            print("after")
            print(f"Current state:{self.state} is restart: {self.restart}")
            if not self.restart and self.state == State.CRAFTING_ESS:
                while self.state == State.CRAFTING_ESS:
                    if self.restart:
                        break
                    self.craft_ess()
            elif not self.restart and not self.out_of_ess and (self.state == State.ENTERING_PILLAR or self.state == State.CRAFTING_RUNES):
                while self.state == State.ENTERING_PILLAR:
                    if self.restart:
                        break
                    self.enter_pillar()
                    time.sleep(1)
                while self.state == State.CRAFTING_RUNES:
                    if self.restart:
                        break
                    self.craft_runes()
                    time.sleep(1)
            elif not self.restart and not self.out_of_ess and self.state == State.GIVING_GUARDIANS:
                while self.state == State.GIVING_GUARDIANS:
                    if self.restart or self.state == State.STUCK_IN_ALTAR:
                        break
                    self.give_guardians()
                    time.sleep(1)
            elif not self.restart and self.state == State.REPAIRING_BARRIER:
                while self.state == State.REPAIRING_BARRIER:
                    if self.restart:
                        break
                    self.repair_barrier()
                    time.sleep(1)
            elif not self.restart and self.runes_in_inv() and self.state == State.DEPOSITING_RUNES:
                while self.state == State.DEPOSITING_RUNES:
                    if self.restart:
                        break
                    self.deposit_runes()
                    time.sleep(.1)
            elif self.state == State.STUCK_IN_ALTAR:
                port = self.get_nearest_tag(clr.YELLOW)
                if port is None:
                    self.find_object_and_click(clr.PINK, "ignore")
                    time.sleep(1)
                self.find_object_and_click(clr.YELLOW, "Enter")

    def cell_in_inventory(self):
        list_cells = [ids.WEAK_CELL, ids.MEDIUM_CELL, ids.STRONG_CELL, ids.OVERCHARGED_CELL]
        for cell in list_cells:
            if self.api_m.get_if_item_in_inv(cell):
                return True
        return False


    def check_restart(self):
        start_timer = time.time()
        while self.restart:
            if time.time() - start_timer > 5:
                print("Timeout reached while waiting for object. Proceeding without finding object.")
                break
            time.sleep(.1)

    def craft_ess(self):
        workbench = self.get_nearest_tag(clr.GREEN)
        
        while workbench is None and self.restart is False:
            self.find_object_and_click(clr.START, "ignore")
            time.sleep(2)
            workbench = self.get_nearest_tag(clr.GREEN)
            

        self.find_object_and_click(clr.GREEN, "Work")
        starting_xp = self.api_m.get_skill_xp("Crafting")
        counter = 0
        while self.api_m.get_is_inv_full() is False and self.restart is False:
            if self.api_m.get_skill_xp("Crafting") == starting_xp:
                counter += 1
            else:
                counter = 0

            if self.out_of_ess:
                break
            
            if counter >= 20:
                self.find_object_and_click(clr.GREEN, "Work")
                counter = 0
                starting_xp = self.api_m.get_skill_xp("Crafting")

            time.sleep(.1)

        crafting = True
        while crafting:
            if self.api_m.get_is_inv_full() is True or self.api_m.get_if_item_in_inv(ids.GUARDIAN_FRAGMENTS) is False:
                crafting = False
                break
                
            if self.restart:
                crafting = False
                break

            time.sleep(.1)

        if self.api_m.get_if_item_in_inv(ids.GUARDIAN_FRAGMENTS) is False:
            self.out_of_ess = True
    

        self.check_restart()
        if self.out_of_ess is False and self.restart is False:
            self.find_inv_and_click(self.api_m.get_inv_item_indices(ids.COLOSSAL_POUCH)[0], "Fill")
                
            if self.api_m.get_if_item_in_inv(ids.GUARDIAN_FRAGMENTS) is True:
                self.find_object_and_click(clr.GREEN, "Work")
                starting_xp = self.api_m.get_skill_xp("Crafting")
                counter = 0
                start = time.time()
                while self.api_m.get_is_inv_full() is False and self.restart is False:
                    if time.time() - start >= 4 and self.out_of_ess is False:
                        self.find_inv_and_click(self.api_m.get_inv_item_indices(ids.COLOSSAL_POUCH)[0], "Fill")
                        self.find_object_and_click(clr.GREEN, "Work")

                    if self.api_m.get_skill_xp("Crafting") == starting_xp:
                        counter += 1
                    else:
                        counter = 0

                    if counter >= 20:
                        self.find_object_and_click(clr.GREEN, "Work")
                        counter = 0
                        starting_xp = self.api_m.get_skill_xp("Crafting")

                    time.sleep(.1)


                crafting = True
                while crafting:
                    if self.api_m.get_is_inv_full() is True or self.api_m.get_if_item_in_inv(ids.GUARDIAN_FRAGMENTS) is False:
                        crafting = False
                        break
                    if self.restart:
                        crafting = False
                        break
                    time.sleep(.1)

                if self.api_m.get_if_item_in_inv(ids.GUARDIAN_ESSENCE) is False:
                    self.out_of_ess = True
        time.sleep(1)
                
    def enter_pillar(self):
        while self.current_pillar is None:
            time.sleep(.1)
        if self.current_pillar is not None:
            pill = self.get_nearest_tag(self.current_pillar)
        while pill is None:
            time.sleep(3)

            if self.current_pillar is not None:
                pill = self.get_nearest_tag(self.current_pillar)
            print("In second loop of enter pillar")
            if pill is None:
                print("Cant find pillar")
                self.find_object_and_click(clr.START, "ignore")
            self.mouse.move_to(self.win.control_panel.random_point())
            if self.in_altar is True:
                break
            time.sleep(.1)
        
        print("Found pillar, clicking")
        self.find_object_and_click(self.current_pillar, "G")
        time.sleep(3)
        print("clicked pillar")
        start_time = time.time()
        img = self.GOTR_IMAGES.joinpath("dormant_check.PNG")
        while self.in_altar is False:
            check_if_dormant = imsearch.search_img_in_rect(img, self.win.chat, confidence=0.05)
            if time.time() - start_time >= 15:
                self.find_object_and_click(clr.START, "ignore")
                time.sleep(3)
                if self.current_pillar is not None:
                    self.find_object_and_click(self.current_pillar, "G")
                start_time = time.time()
            elif check_if_dormant:
                print("dormant")
                self.find_object_and_click(clr.START, "ignore")
                time.sleep(3)
                self.find_object_and_click(self.current_pillar, "G")
            

    def craft_runes(self):
        colossal_pouch = self.api_m.get_inv_item_indices(ids.COLOSSAL_POUCH)
        altar = self.get_nearest_tag(clr.BLUE)
        print("Finding Altar")
        if altar is None:
            self.find_object_and_click(clr.PINK, "ignore")
        print("Altar Found")
        self.find_object_and_click(clr.BLUE, "Altar")
        self.api_m.wait_til_gained_xp("Runecraft")
        print("Crafted Runes")
        if self.first_run is False and self.out_of_ess is False:
            self.find_inv_and_click(colossal_pouch[0], "Empty")
            self.find_object_and_click(clr.BLUE, "Altar")
            self.api_m.wait_til_gained_xp("Runecraft")

        if self.first_run is False and self.out_of_ess is False:
            self.find_inv_and_click(colossal_pouch[0], "Empty")
            self.find_object_and_click(clr.BLUE, "Altar")
            self.api_m.wait_til_gained_xp("Runecraft")
        
        if self.api_m.get_if_item_in_inv(ids.DEATH_RUNE):
            self.find_object_and_click(clr.PINK, "ignore")
            time.sleep(1)
        portal = self.get_nearest_tag(clr.YELLOW)
        print(f"Finding Portal, in altar? {self.in_altar}")
        while portal is None:
            if self.in_altar:
                print("Clicking proxy")
                self.find_object_and_click(clr.PINK, "ignore")
                portal = self.get_nearest_tag(clr.YELLOW)
                time.sleep(2)
            else:
                break
        print(f"Finding Portal, in altar check two? {self.in_altar}")
        if self.in_altar is True:
            print("Portal Found")
            self.find_object_and_click(clr.YELLOW, "Portal")
            print("Waiting for transition")
            dep = self.get_nearest_tag(clr.POOL)
            start_time = time.time()
            while dep is None:
                if time.time() - start_time >= 10:
                    start_time = time.time()
                    if dep is None:
                        self.find_object_and_click(clr.YELLOW, "Portal")
                dep = self.get_nearest_tag(clr.POOL)
                time.sleep(.1)
            
        
    def give_guardians(self):
        portal = self.get_nearest_tag(clr.YELLOW)
        while portal is None:
            if self.in_altar:
                print("Clicking proxy")
                self.find_object_and_click(clr.PINK, "ignore")
                portal = self.get_nearest_tag(clr.YELLOW)
                time.sleep(2)
            else:
                break
        print(f"Finding Portal, in altar check two? {self.in_altar}")
        if self.in_altar is True:
            print("Portal Found")
            self.find_object_and_click(clr.YELLOW, "Portal")
            print("Waiting for transition")
            dep = self.get_nearest_tag(clr.POOL)
            start_time = time.time()
            while dep is None:
                if time.time() - start_time >= 10:
                    start_time = time.time()
                    if dep is None:
                        self.find_object_and_click(clr.YELLOW, "Portal")
                dep = self.get_nearest_tag(clr.POOL)
                time.sleep(.1)
        guardian = self.get_nearest_tag(clr.CYAN)
        if guardian is not None:
            self.mouse.move_to(guardian.random_point())
            while self.mouse.click(check_red_click=True) is False:
                guardian = self.get_nearest_tag(clr.CYAN)
                if guardian is None:
                    self.mouse.move_to(self.win.control_panel.random_point())
                    guardian = self.get_nearest_tag(clr.CYAN)
                else:
                    self.mouse.move_to(guardian.random_point())
            curr_runecraft_xp = self.api_m.get_skill_xp("runecraft")
            while curr_runecraft_xp == self.api_m.get_skill_xp("runecraft"):
                time.sleep(.1)
        
            
    def repair_barrier(self):
        barrier = self.get_nearest_tag(clr.BARRIER)

        while barrier is None:
            if self.in_altar:
                break
            print("barrier")
            barrier = self.get_nearest_tag(clr.BARRIER)
            self.find_object_and_click(clr.START, "ignore")

        if self.in_altar is False:
            self.find_object_and_click(clr.BARRIER, "cell")

            curr_runecraft_xp = self.api_m.get_skill_xp("runecraft")
            start = time.time()
            while curr_runecraft_xp == self.api_m.get_skill_xp("runecraft"):
                if time.time() - start == 15:
                    self.find_object_and_click(clr.BARRIER, "cell")
                time.sleep(.1)


    def find_inv_and_click(self, inv_slot, over_text, wrong_text="filler"):
        self.mouse.move_to(self.win.inventory_slots[inv_slot].random_point())
        if self.mouseover_text(wrong_text) is False:
            while self.mouseover_text(over_text) is False:
                self.mouse.move_to(self.win.inventory_slots[inv_slot].random_point())
                time.sleep(.1)
            self.mouse.click()
        else: 
            print("Wrong text")

    def deposit_runes(self):
        time.sleep(3)
        print("In deposit runes")
        pool = self.get_nearest_tag(clr.POOL)
        while pool is None:
            print("In deposit runes: first loop")
            start = self.get_nearest_tag(clr.START)

            while not start and self.in_altar is False:
                print("In deposit runes: second loop")
                self.mouse.move_to(self.win.control_panel.random_point())
                start = self.get_nearest_tag(clr.START)
                time.sleep(.1)

            self.find_object_and_click(clr.START, "ignore")
            time.sleep(2)

            pool = self.get_nearest_tag(clr.POOL)

        if self.find_object_and_click(clr.POOL, "Dep") is False:
            self.find_object_and_click(clr.START, "ignore")
            time.sleep(2)
            self.find_object_and_click(clr.POOL, "Dep")

        counter = 0

        while self.runes_in_inv():
            if self.in_altar:
                break
            print("In deposit runes: second loop")
            print(counter)
            if counter > 100:
                self.mouse.move_to(self.win.control_panel.random_point())
                if self.find_object_and_click(clr.POOL, "Dep") is False:
                    self.find_object_and_click(clr.START, "ignore")
                    time.sleep(2)
                counter=0
            else:
                counter += 1
            time.sleep(.1)

    def runes_in_inv(self):
        list_runes = [ids.AIR_RUNE, ids.WATER_RUNE, ids.EARTH_RUNE, ids.FIRE_RUNE, ids.BODY_RUNE, ids.MIND_RUNE, ids.COSMIC_RUNE, ids.LAW_RUNE, ids.CHAOS_RUNE, ids.NATURE_RUNE, ids.DEATH_RUNE]
        for rune in list_runes:
            if self.api_m.get_if_item_in_inv(rune):
                return True
        
        return False

    def find_text_and_click(self, text, text_action=""):             
        text_area = ocr.find_text(text, self.win.game_view, ocr.PLAIN_11, clr.YELLOW)

        while not text_area:
            text_area = ocr.find_text(text, self.win.game_view, ocr.PLAIN_11, clr.YELLOW)
            time.sleep(.1)
        if text_action != "ignore":
            self.mouse.move_to(text_area[0].random_point())
            while self.mouseover_text(text_action) is False:
                text_area = ocr.find_text(text, self.win.game_view, ocr.PLAIN_11, clr.YELLOW)
                while not text_area:
                    text_area = ocr.find_text(text, self.win.game_view, ocr.PLAIN_11, clr.YELLOW)
                    time.sleep(.1)
                self.mouse.move_to(text_area[0].random_point())
                time.sleep(.1)
            while self.mouse.click(check_red_click=True) is False:
                text_area = ocr.find_text(text, self.win.game_view, ocr.PLAIN_11, clr.YELLOW)
                while not text_area:
                    self.mouse.move_to(self.win.control_panel.random_point())
                    text_area = ocr.find_text(text, self.win.game_view, ocr.PLAIN_11, clr.YELLOW)
                    time.sleep(.1)
                
                self.mouse.move_to(text_area[0].random_point())   
        else:
            self.mouse.move_to(text_area[0].random_point())
            if text_action != "ignore":
                while self.mouse.click(check_red_click=True) is False:
                    text_area = ocr.find_text(text, self.win.game_view, ocr.PLAIN_11, clr.YELLOW)
                    while not text_area:
                        text_area = ocr.find_text(text, self.win.game_view, ocr.PLAIN_11, clr.YELLOW)
                        self.mouse.move_to(self.win.game_view.point_to_left_side())
                        time.sleep(.1)
                    self.mouse.move_to(text_area[0].point_around_center())
                    time.sleep(.1)
            else:
                self.mouse.move_to(text_area[0].random_point())
                self.mouse.click()
        
        
    def find_object_and_click(self, color: clr, over_text="", timeout=3):
        try:
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
                print("mouse working??")

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

                print(f"is defeatee {self.defeated} is restarting: {self.restart}")

                if over_text == "ignore":
                    start_time = time.time()
                    while self.mouseover_text("Enter"):
                        if time.time() - start_time > timeout:
                            print("timeout ignore")
                            break
                        self.mouse.move_to(obj.random_point())
                        time.sleep(.1)
                    if self.mouseover_text("Switch") == False:
                        self.mouse.click()
                # Perform the click
                else:
                    if self.mouseover_text("Switch") == False:
                        self.mouse.click()
            else:
                print("No object")
                return False
            
            return True
        except:
            print("failed to find and click")
            return False


    def check_for_restart_image(self):
        success = self.GOTR_IMAGES.joinpath("game_success.PNG")
        restart = self.GOTR_IMAGES.joinpath("game_restart.PNG")
        start = self.GOTR_IMAGES.joinpath("still_starting.png")

        while True:
            succ = imsearch.search_img_in_rect(success, self.win.game_view, confidence=0.1)
            rest = imsearch.search_img_in_rect(restart, self.win.game_view, confidence=0.1)
            still_starting = imsearch.search_img_in_rect(start, self.win.game_view, confidence=0.1)
            
            if still_starting is not None:
                # If 'still_starting' is detected, prioritize this condition
                self.start = True
                self.restart = False
            elif succ is not None or rest is not None or self.out_of_ess or self.defeated:
                if succ is not None: 
                    print("succeded with minigame")
                elif self.out_of_ess:
                    print("Ran out of ess")
                elif self.defeated:
                    print("Guardian Defeated!")
                # If 'succ' or 'rest' is detected and 'still_starting' is not, restart
                self.restart = True
                self.start = False
            elif self.current_pillar is not None:
                self.restart = False
                self.start = False
            else:
                # If none of the images are detected
                
                self.restart = True
                self.start = False
            
            time.sleep(.5)

    def check_current_pillar(self):
        pillars_string = ["air.png", "mind.png", "water.png", "earth.png", "fire.png", "body.png", "cosmic.png", "chaos.png", "nature.png", "law.png", "death.png"]
        start = self.GOTR_IMAGES.joinpath("still_starting.png")
        one_time_circuit_on = False
        while True:
            still_starting = imsearch.search_img_in_rect(start, self.win.game_view, confidence=0.10)
            if still_starting is None:
                current_pillars = []
                if not one_time_circuit_on:
                    one_time_circuit_on = True
                for index, pillar in enumerate(pillars_string):
                    image_path = self.GOTR_IMAGES.joinpath(pillar)
                    pillar_rect = imsearch.search_img_in_rect(image_path, self.win.game_view,confidence=.10)
                    if pillar_rect is not None:
                        current_pillars.append(index)
                    
                    if len(current_pillars) == 2:
                        if current_pillars[1] == 11 or current_pillars[1] == 12:
                            self.current_pillar = self.runes[current_pillars[1]]
                        else:
                            self.current_pillar = self.runes[current_pillars[1]]
                        break
                
                if len(current_pillars) == 1:
                    self.current_pillar = self.runes[current_pillars[0]]

                if len(current_pillars) == 0:
                    self.current_pillar = None
            else:
                if self.restart:
                    self.current_pillar = None
                if one_time_circuit_on:
                    one_time_circuit_on = False
        
    def check_defeated_guardian(self):
        img = self.GOTR_IMAGES.joinpath("defeated_guardian.png")
        while True:
            is_defeated = imsearch.search_img_in_rect(img, self.win.chat, confidence=0.05)
            if is_defeated is not None:
                self.defeated = True
                time.sleep(40)

            time.sleep(.5)

    def check_location(self):
        altar = self.get_nearest_tag(clr.PINK)
        while True:
            altar = self.get_nearest_tag(clr.PINK)

            if altar is not None:
                self.in_altar = True
            else:
                self.in_altar = False
            time.sleep(.5)

    def state_tracker(self):
        while True:
            # ENTERING_PILLAR, should check if inventory is full and if not in altar
            if self.api_m.get_is_inv_full() and self.in_altar is False: 
                self.state = State.ENTERING_PILLAR
            # CRAFTING_RUNES, should check if invetory is full and if in altar
            elif self.api_m.get_is_inv_full() and self.in_altar:
                self.state = State.CRAFTING_RUNES
            # GIVING_GUARDIANS, should check if inventory contains stones
            elif self.in_altar is False and (self.api_m.get_if_item_in_inv(ids.ELEMENTAL_GUARDIAN_STONE) or self.api_m.get_if_item_in_inv(ids.CATALYTIC_GUARDIAN_STONE)):
                self.state = State.GIVING_GUARDIANS
            # REPAIRING_BARRIER
            elif self.in_altar is False and (self.api_m.get_if_item_in_inv(ids.WEAK_CELL) or self.api_m.get_if_item_in_inv(ids.MEDIUM_CELL) or self.api_m.get_if_item_in_inv(ids.STRONG_CELL) or self.api_m.get_if_item_in_inv(ids.OVERCHARGED_CELL)):
                self.state = State.REPAIRING_BARRIER
            # DEPOSITING_RUNES, if runes in inventory
            elif self.runes_in_inv() and self.in_altar is False:
                self.state = State.DEPOSITING_RUNES
            # STUCK_IN_ALTAR, if stuck in altar
            elif self.in_altar and self.runes_in_inv():
                self.state = State.STUCK_IN_ALTAR
            elif not self.api_m.get_if_item_in_inv(ids.ELEMENTAL_GUARDIAN_STONE) and not self.api_m.get_if_item_in_inv(ids.CATALYTIC_GUARDIAN_STONE) and not self.api_m.get_if_item_in_inv(ids.WEAK_CELL) or not self.api_m.get_if_item_in_inv(ids.MEDIUM_CELL) and not self.api_m.get_if_item_in_inv(ids.STRONG_CELL) and not self.api_m.get_if_item_in_inv(ids.OVERCHARGED_CELL) and not self.runes_in_inv:
                self.state = State.CRAFTING_ESS
            else:
                print('unsure state')
            time.sleep(.1)