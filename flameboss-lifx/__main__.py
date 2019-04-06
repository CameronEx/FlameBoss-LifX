from .flameboss_monitor import FlameBossMon
from .lifx_controller import LifxController
from configparser import ConfigParser
import logging
import time
import sys
import os


class FBLifX:
    """
    Runs the logic for this project. Uses two classes, one to monitor the flameboss controller,
    another to manage the light(s)
    """

    def __init__(self):
        """
        Program entry point.
        TODO: Change debugging to informational messages only
        """
        self.fb = None
        self.lc = None
        self.config = ConfigParser()
        self.config_dir: str = os.path.expanduser("~/.config/FlameBoss-LifX/")
        self.config_file: str = self.config_dir + "config.ini"
        self.controller_id: str = None
        self.poll_interval: int = None
        self.bulb_mac: str = None
        self.bulb_ip: str = None
        self.bulb_label: str = None

        # Logger config
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.ch.setFormatter(self.formatter)
        self.logger.addHandler(self.ch)

        # Start the program
        self.run()

    def load_config(self):
        """
        Check for config, load if exists.
        """

        if not os.path.exists(self.config_dir):
            self.logger.debug(f"load_config: {self.config_dir} doesn't exist. Calling self.intial_config")
            self.initial_config()
        else:
            self.logger.debug(f"Config directory {self.config_dir} already exists.")

        logging.debug("Attempting to read config file.")
        if not self.config.read(self.config_file):
            logging.WARNING("Configuration file doesn't exist or is malformed.")
            self.initial_config()

        self.controller_id = self.config["LAST_USED"]["controller_id"]
        self.poll_interval = int(self.config["LAST_USED"]["poll_interval"])
        self.bulb_mac = self.config["LAST_USED"]["bulb_mac"]
        self.bulb_ip = self.config["LAST_USED"]["bulb_ip"]
        self.bulb_label = self.config["LAST_USED"]["bulb_label"]

        print(f"\033[1mConfiguration\033[0m\n\n"
              f"FlameBoss Controller: {self.controller_id}\n"
              f"LifX Bulb Name: {self.bulb_label}\n"
              "Note: if the IP address of the bulb has changed, we will need to perform discovery again."
              )
        valid_answer: bool = False
        count: int = 0
        while not valid_answer:
            use_existing_config = input("Would you like to use the above configuration? [Y/N]")
            if use_existing_config.lower() == "y":
                # load config
                valid_answer = True
            elif use_existing_config == "n":
                self.initial_config()
                valid_answer = True
            else:
                count += 1
                if count >= 4:
                    print("Giving up on you...")
                    sys.exit(1)
                else:
                    print("Invalid answer, try again.")

        self.fb = FlameBossMon(controller_id=self.controller_id)
        self.lc = LifxController(self.bulb_mac, self.bulb_ip)

    def initial_config(self):
        """
        Set up, or overwrite configuration file.
        TODO: test me under different scenarios (will this overwrite existing config?)
        """
        # Discover bulbs available on the local LAN
        logging.info("Starting Setup.\nDiscovering bulbs...")
        self.lc = LifxController()
        self.lc.discover_bulbs()
        self.lc.select_target()
        bulb_config = self.lc.get_config()
        logging.debug(f"Selected bulb MAC: {self.bulb_mac}, IP: {self.bulb_ip}")

        # Obtain the controller ID.
        logging.info("Enter the ID of your Flame Boss controller.")
        logging.info("This is displayed on the LCD of your controller (if you have one)")
        logging.info("or can be found at https://myflameboss.com/en/users/edit")
        controller_id = input("Controller ID: ")

        # Create the directory
        os.makedirs(self.config_dir)
        logging.debug(f"intial_config: Created {self.config_dir}")

        # Create the configuration to be written
        setup_config: dict = {
                         "controller_id": controller_id,
                         "poll_interval": 300,
                         "bulb_mac": bulb_config["mac_addr"],
                         "bulb_ip": bulb_config["ip_addr"],
                         "bulb_label": bulb_config["label"]
                        }
        # Write the config
        logging.debug(f"Saving config:\n{setup_config}")
        self.config['LAST_USED'] = setup_config
        with open(self.config_file, "w") as file:
            self.config.write(file)
            logging.debug("initial_config: Wrote config successfully.")

    def update(self):
        """
        Requests all information to be updated, from both LifX and FlameBoss APIs
        :return: None
        """
        # Start with the controller info
        try:
            self.fb.get_device_info()
        except StopIteration:
            # Raised when device is no longer online
            sys.exit("The controller is no longer available.")
        except KeyError:
            # Raised when eht API returned a funky response
            sys.exit(1)

        # Collect the cook info
        self.fb.get_cook()

        # Calculate our new colour
        new_colour = self.calc_drift()

        # Set the light's colour, preserving the existing brightness
        brightness = self.lc.get_colour()[2]
        self.lc.set_colour([new_colour, 65535, brightness, 3500])

    def calc_drift(self):
        """
        Calculates the drift between the set temperature and the current temperature
        :return: None
        """
        drift: int = (self.fb.target_temp - self.fb.current_temp)/self.fb.temp_drift

        # Calculate, and return, a new colour for the bulb. 24500 is green, we're going to drift either side of that

        out = (self.fb.target_temp - self.fb.current_temp) / self.fb.temp_drift * 24500 + 24500
        if out > 49000:
            out = 49000
        if out < 0:
            out = 0

        self.logger.debug(f"{self.fb.target_temp} - {self.fb.current_temp} / {self.fb.temp_drift}"
                     f" * 24500 + 24500 = out {out}")

        return out

    def run(self):
        """
        Runs this program.
        """
        # Load the configuration, if no config exists this module will call the initial setup
        self.load_config()

        # Begin the loop
        logging.debug("run: Starting loop.")
        while True:
            logging.debug("Updating.")
            print("ticck")
            self.update()
            time.sleep(self.poll_interval)


if __name__ == "__main__":
    fblifx = FBLifX()
    fblifx.run()
