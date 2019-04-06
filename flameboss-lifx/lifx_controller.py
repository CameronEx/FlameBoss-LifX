from lifxlan import LifxLAN
from pick import pick
import logging

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

    def __init__(self, bulb_mac=None, bulb_ip=None):
        logging.debug("Initialising LifxController.")
        self.lan = LifxLAN()
        self.bulbs = None
        self.groups = None
        self.bulb_labels: list = []
        self.group_labels: list = []
        self.bulb = None
        self.group = None
        self.bulb_mac = bulb_mac
        self.bulb_ip = bulb_ip

        # Logger config
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.ch.setFormatter(self.formatter)
        self.logger.addHandler(self.ch)

        # When loading config, we don't need to discover the bulb
        if self.bulb_mac and self.bulb_ip:
            from lifxlan import Light
            self.bulb = Light(self.bulb_mac, self.bulb_ip)

    def discover_bulbs(self):
        """
        Discovers individual bulbs, then groups
        """
        logging.debug("discover_bulbs: Discovering individual bulbs.")
        # Discover bulbs on the LAN
        self.bulbs = self.lan.get_devices()
        logging.debug(f"discover_bulbs: Discovery complete. {len(self.lan.devices)} bulbs found.")

        for bulb in self.bulbs:
            # Build a list of bulb names
            bulb_name = bulb.get_label()
            if bulb_name not in self.bulb_labels:
                self.bulb_labels.append(bulb_name)
            # Figure out what groups exist from their group_labels
            # There is no way to simply discover what groups are available
            group = bulb.get_group_label()
            if group:
                if group not in self.group_labels:
                    self.group_labels.append(group)

    def select_target(self):
        """
        Creates menu to select target bulb or group.
        """

        title = "Would you like to target a single bulb, or groups of bulbs?"
        options = ["Single", "Group"]

        _, selection = pick(options, title)
        print(type(selection), selection)
        if selection == 0:
            logging.debug("User is going to target a single bulb.")
            title = "Select the bulb to target"
            _, selection = pick(self.bulb_labels, title)
            self.bulb = self.bulbs[selection]
        elif selection == 1:
            logging.debug("User is going to target a group of bulbs.")
            title = "Select the target group"
            _, selection = pick(self.group_labels, title)
            self.group = self.groups[selection]

    def get_colour(self):
        """
        Obtains the current colour of the bulb.
        """
        if self.bulb:
            return self.bulb.get_color()
        elif self.group:
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
            return self.bulb.set_color(colour)
        if self.group:
            return self.group.set_color(colour)

    def get_config(self):
        """
        Returns bulb config, to save for later.
        return: dict
        """
        if self.bulb:
            bulb_config: dict = {
                                "mac_addr": self.bulb.get_mac_addr(),
                                "ip_addr": self.bulb.get_ip_addr(),
                                "label": self.bulb.get_label()
                                }
            return bulb_config
        else:
            logging.debug("get_config: Returning group config")


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.debug)
    ch = logging.StreamHandler()
    ch.setLevel(logging.debug)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
