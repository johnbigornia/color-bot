import time
from typing import List, Tuple, Union
import requests

class SocketError(Exception):
    def __init__(self, error_message: str, endpoint: str):
        self.__error_message = error_message
        self.__endpoint = endpoint
        super().__init__(self.get_error())

    def get_error(self):
        return f"{self.__error_message} endpoint: {self.__endpoint}"

class MorgHTTPSocket:
    def __init__(self):
        self.base_endpoint = "http://localhost:8080/"

        self.inv_endpoint = "inv"
        self.stats_endpoint = "stats"

        self.timeout = 1

    def __do_get(self, endpoint: str) -> dict:
        """
        Sends a GET request to the specified endpoint.
        Args:
            endpoint: The endpoint to send the request to.
        Returns:
            The JSON data from the response as a dictionary.
        Raises:
            SocketError: If the endpoint is not valid or the server is not running.
        """
        try:
            response = requests.get(f"{self.base_endpoint}{endpoint}", timeout=self.timeout)
        except requests.exceptions.ConnectionError as e:
            raise SocketError("Unable to reach socket", endpoint) from e

        if response.status_code != 200:
            if response.status_code == 204:
                return {}
            else:
                raise SocketError(
                    f"Unable to reach socket. Status code: {response.status_code}",
                    endpoint,
                )

        return response.json()

    # Inventory Methods

    def get_inventory_item_count(self) -> int:
        """
        Gets the total number of items in the inventory.
        Returns:
            The total count of items in the inventory.
        """
        data = self.__do_get(endpoint=self.inv_endpoint)
        total_count = sum(item["quantity"] for item in data if item["id"] != -1)
        return total_count
    
    def get_inv(self):
        """
        Gets a list of dicts representing the player's inventory.
        Returns:
            A list of dictionaries, each containing index, id, and quantity of an item.
        """
        data = self.__do_get(endpoint=self.inv_endpoint)
        inventory = []
        for index, item in enumerate(data):
            if item["quantity"] == 0 or item["id"] == -1:
                continue
            item_info = {"index": index, "id": item["id"], "quantity": item["quantity"]}
            inventory.append(item_info)
        return inventory

    def get_if_item_in_inv(self, item_id: Union[List[int], int]) -> bool:
        """
        Checks if an item is in the inventory.
        Args:
            item_id: The ID of the item to check for (single ID or list of IDs).
        Returns:
            True if the item is in the inventory, False otherwise.
        """
        data = self.__do_get(endpoint=self.inv_endpoint)
        if isinstance(item_id, int):
            return any(slot["id"] == item_id for slot in data)
        elif isinstance(item_id, list):
            return any(slot["id"] in item_id for slot in data)
        else:
            return False

    def get_is_inv_full(self) -> bool:
        """
        Checks if the player's inventory is full.
        Returns:
            True if the inventory is full, False otherwise.
        """
        data = self.__do_get(endpoint=self.inv_endpoint)
        return len([item for item in data if item["id"] != -1]) == 28

    def get_is_inv_empty(self) -> bool:
        """
        Checks if the player's inventory is empty.
        Returns:
            True if the inventory is empty, False otherwise.
        """
        data = self.__do_get(endpoint=self.inv_endpoint)
        return all(item["id"] == -1 for item in data)

    def get_inv_item_indices(self, item_id: Union[List[int], int]) -> List[int]:
        """
        Gets the indices of the specified item(s) in the inventory.
        Args:
            item_id: The ID of the item(s) to search for.
        Returns:
            A list of inventory slot indices where the item(s) are found.
        """
        data = self.__do_get(endpoint=self.inv_endpoint)
        if isinstance(item_id, int):
            return [i for i, slot in enumerate(data) if slot["id"] == item_id]
        elif isinstance(item_id, list):
            return [i for i, slot in enumerate(data) if slot["id"] in item_id]
        else:
            return []

    def get_first_occurrence(self, item_id: Union[List[int], int]) -> Union[int, List[int]]:
        """
        Gets the first inventory slot index of the specified item(s).
        Args:
            item_id: The ID of the item(s) to search for.
        Returns:
            The first inventory slot index of the item if a single ID is provided,
            or a list of indices if a list of IDs is provided.
        """
        data = self.__do_get(endpoint=self.inv_endpoint)
        if isinstance(item_id, int):
            return next((i for i, slot in enumerate(data) if slot["id"] == item_id), -1)
        elif isinstance(item_id, list):
            first_occurrences = {}
            for i, slot in enumerate(data):
                if slot["id"] in item_id and slot["id"] not in first_occurrences:
                    first_occurrences[slot["id"]] = i
            return list(first_occurrences.values())
        else:
            return []

    def get_inv_item_stack_amount(self, item_id: Union[int, List[int]]) -> int:
        """
        Gets the total quantity of the specified item(s) in the inventory.
        Args:
            item_id: The ID of the item(s) to search for.
        Returns:
            The total quantity of the item(s) in the inventory.
        """
        data = self.__do_get(endpoint=self.inv_endpoint)
        total_quantity = 0
        if isinstance(item_id, int):
            item_id = [item_id]
        for item in data:
            if item["id"] in item_id:
                total_quantity += item["quantity"]
        return total_quantity
    
    def get_non_stackable_item_count(self, item_id: Union[int, List[int]]) -> int:
        """
        Counts the total number of non-stackable items in the inventory for the specified item ID(s).
        Args:
            item_id: The ID of the item(s) to count (single ID or list of IDs).
        Returns:
            The total count of the item(s) in the inventory.
        """
        data = self.__do_get(endpoint=self.inv_endpoint)
        count = 0
        if isinstance(item_id, int):
            item_id = [item_id]
        for item in data:
            if item["id"] in item_id:
                count += 1
        return count

    # Stats Methods

    def get_skill_level(self, skill: str) -> int:
        """
        Gets the level of the specified skill.
        Args:
            skill: The name of the skill (not case-sensitive).
        Returns:
            The level of the skill, or -1 if not found.
        """
        data = self.__do_get(endpoint=self.stats_endpoint)
        try:
            level = next(int(i["level"]) for i in data if i["stat"].lower() == skill.lower())
        except StopIteration:
            print(f"Invalid stat name: {skill}.")
            return -1
        return level

    def get_skill_xp(self, skill: str) -> int:
        """
        Gets the total XP of the specified skill.
        Args:
            skill: The name of the skill (not case-sensitive).
        Returns:
            The total XP of the skill, or -1 if not found.
        """
        data = self.__do_get(endpoint=self.stats_endpoint)
        try:
            total_xp = next(int(i["xp"]) for i in data if i["stat"].lower() == skill.lower())
        except StopIteration:
            print(f"Invalid stat name: {skill}.")
            return -1
        return total_xp

    def wait_til_gained_xp(self, skill: str, timeout: int = 10) -> int:
        """
        Waits until XP is gained in the specified skill.
        Args:
            skill: The name of the skill (not case-sensitive).
            timeout: The maximum time to wait in seconds.
        Returns:
            The amount of XP gained, or -1 if no XP was gained within the timeout.
        """
        starting_xp = self.get_skill_xp(skill)
        if starting_xp == -1:
            print("Failed to get starting XP.")
            return False

        stop_time = time.time() + timeout
        while time.time() < stop_time:
            current_xp = self.get_skill_xp(skill)
            if current_xp == -1:
                print("Failed to get current XP.")
                return False
            if current_xp > starting_xp:
                return True
        return False

    # Note: Methods requiring endpoints not available have been omitted.

    def is_item_in_slot(self, slot_index: int, item_id: int) -> bool:
        """
        Checks if a specific item ID exists in a specific inventory slot.
        Args:
            slot_index: The inventory slot index to check.
            item_id: The ID of the item to check for.
        Returns:
            True if the item with the specified ID exists in the given slot, False otherwise.
        """
        data = self.__do_get(endpoint=self.inv_endpoint)
        if 0 <= slot_index < len(data):
            return data[slot_index]["id"] == item_id
        else:
            raise IndexError(f"Slot index {slot_index} is out of bounds for inventory size {len(data)}.")

if __name__ == "__main__":
    api = MorgHTTPSocket()

    # Example usage:

    # Inventory Data
    print("Inventory Items:")
    inventory = api.get_inv()
    for item in inventory:
        print(f"Index: {item['index']}, ID: {item['id']}, Quantity: {item['quantity']}")

    # Check if specific item is in inventory
    item_id = 946  # Example item ID
    is_in_inventory = api.get_if_item_in_inv(item_id)
    print(f"Is item ID {item_id} in inventory? {is_in_inventory}")

    # Get skill level
    skill_name = "Attack"
    level = api.get_skill_level(skill_name)
    print(f"{skill_name} Level: {level}")

    # Get skill XP
    xp = api.get_skill_xp(skill_name)
    print(f"{skill_name} XP: {xp}")

    # Wait until XP is gained in a skill
    print(f"Waiting for XP gain in {skill_name}...")
    xp_gained = api.wait_til_gained_xp(skill_name, timeout=30)
    if xp_gained != -1:
        print(f"Gained {xp_gained} XP in {skill_name}!")
    else:
        print(f"No XP gained in {skill_name} within the timeout.")

