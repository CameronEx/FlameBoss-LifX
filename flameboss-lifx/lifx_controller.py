from lifxlan import LifxLan
from pick import pick

"""
Used to interact with, LifX bulbs.
A general class to interact with the LifxLan library, making it a little
more user friendly.
Although specificly created for FlameBoss-LifX, modules were constructed
in a general nature, to allow for reuse in other projects.

Repository: https://github.com/CameronEx/FlameBoss-LifX/
Code, documentation, isses and license info here.
TODO: Group interaction
"""

class LifxController:

    def __init__(self):
        logging.debug("Initialising LifxController.")
        self.lan = LifxLan()
        self.bulbs = None
        self.groups = None
        self.bulb_labels: list = []
        self.group_labels: list = []
        self.bulb = None

    def discover_bulbs(self):
        """
        Discovers individual bulbs, then groups
        """
        logging.DEBUG("discover_bulbs: Discovering individual bulbs.")
        # Discover bulbs on the LAN
        self.bulbs = self.lan(get_devices)
        logging.DEBUG(f"discover_bulbs: Discovery complete. {len(self.lan)} bulbs found.")

        for bulb in bulbs:
            # Build a list of bulb names
            bulb_name = bulb.get_group_label()
            if bul_name not in self.bulb_labels:
                self.bulb_labels.append(bulb_name)
            # Figure out what groups exist from their group_labels
            # There is no way to simply discover what groups are avaialable
            group = device.get_group_label()
            if group not in groups:
                self.group_labels.append(group)

    def select_target(self):
        """
        Creates menu to select target bulb or group.
        """
        title = "Would you like to target a single bulb, or groups of bulbs?"
        options = ["Single", "Group"]

        selection, _ = pick(options, title)
        if selection == "0":
            logging.DEBUG("User is going to target a single bulb.")
            title = "Select the bulb to target"
            selection, _ = pick(self.bulb_list, title)
            self.bulb = self.bulbs[selection]
        else:
            logging.debug("User is going to target a group of bulbs.")

    def get_colour(self):
        """
        Obtains the current colour of the bulb.
        """
        if self.bulb:
            return self.bulb.get_color()
        if self.group:
            return self.group.get_color()

    def set_colour(self, colour):
        """
        Sets colour of selected bulb to input.
        Input is HSBK format, which seems to be specific to LifX and really poorly documented
        at the time of this comment.
        https://api.developer.lifx.com/docs/colors
        input: list
        """
        if self.bulb:
            return self.bulb.set_color(color)
        if self.group:
            return self.group.set_color(color)

    def get_config(self):
        """
        Returns bulb config, to save for later.
        return: dict
        """
        bulb_config: dict = {
        "mac_addr": self.bulbs[selection].get_mac_addr(),
        "ip_addr": self.bulbs[selection].get_ip_addr(),
        "label": self.bulbs[selection].get_label()
        }

        return bulb_config
