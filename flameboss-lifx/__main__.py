from flameboss_monitor import FlameBossMon
from lifx_controller import LifxController
from configparser import ConfigParser
import sys
import os

class FBLifX:
    """
    Runs the logic for this project. Uses two classes, one to monitor the flameboss controller,
    another to manage the light(s)
    """

    def __init__(self):
        fb = flameboss_monitor()
        lc = LifxController()
        self.config = ConfigParser()
        self.config_dir: str = os.path.expanduser("~/.config/FlameBoss-LifX/")
        self.config_file: str = config_dir + "config.ini"
        self.controller_id: str = None
        elf.poll_interval: srt = None
        self.bulb_mac: str = None
        self.bulb_ip: str = None

    def load_config(self):
        """
        Check for config, load if exists.
        """

        if not os.path.exists(self.config_dir):
            logger.DEBUG(f"load_config: {self.config_dir} doesn't exist. Calling self.intial_config")
            self.intial_config()
        else:
            logger.DEBUG(f"Config directory {self.config_dir} already exists.")

        logging.DEBUG("Attempting to read config file.")
        if not config.read(self.config_file):
            logging.WARNING("Configuration file doesn't exist or is malformed.")
            self.initial_config()
        else:
            self.controller_id = config["LAST_USED"]["controller_id"]
            self.poll_interval = config["LAST_USED"]["poll_interval"]
            self.bulb_mac = config["LAST_USED"]["bulb_mac"]
            self.bulb_ip = config["LAST_USED"][["bulb_ip"]
            bulb_label = config["LAST_USED"]["bulb_label"]

            print(f"Last saved configuration:\n"
                  "FlameBoss Controller: {self.controller_id}\n"
                  "LifX Bulb Name: {bulb_label}\n"
                  "Note: if the IP address of the bulb has changed, we will need to perform discovery again."
                  )
            valid_answer: bool = False
            count: int = 0
            while not valid_answer:
                use_existing_config = input("Would you like to use the above configuration? [Y/N]")
                if use_existing_config.to_lower() = "y":
                    # load config
                    valid_answer = True
                elif use_existing_config = "n":
                    self.initial_config()
                    valid_answer = True
                else:
                    count += 1
                    if count >= 4:
                        print("Giving up on you...")
                        sys.exit(1)
                    else:
                        print("Invalid answer, try again.")


    def intial_config(self):
        """
        Set up, or overwrite configuration file.
        TODO: test me under different scenarios (will this overwrite existing config?)
        """
        # Discover bulbs available on the local LAN
        logging.info("Starting Setup.\nDiscovering bulbs...")
        lc.discover_bulbs()
        self.lc.select_target()
        bulb_config = lc.save_config()
        logging.DEBUG(f"Selected bulb MAC: {bulb_mac}, IP: {bulb_ip}")

        # Obtain the controller ID.
        logging.INFO("Enter the ID of your Flame Boss controller.")
        logging.INFO("This is displayed on the LCD of your controller (if you have one)")
        logging.INFO("or can be found at https://myflameboss.com/en/users/edit")
        controller_id = input("Enter the ID of your FlameBoss controller: ")

        # Create the directory
        os.makedirs(config_dir)
        logging.DEBUG(f"intial_config: Created {self.config_dir}")

        # Create the configuration to be written
        setup_config = {
                         "controller_id": controller_id,
                         "poll_interval": 300,
                         "bulb_mac": bulb_config["mac_addr"],
                         "bulb_ip": bulb_config["ip_addr"],
                         "bulb_label": bulb_config["label"]
                        }
        # Write the config
        logging.DEBUG(f"Saving config:\n{setup_config}")
        config['LAST_USED'] = setup_config
        with open(config_file, "w") as file:
            config.write(file)
            logging.DEBUG("initial_config: Wrote config successfully.")

    def run(self):
        """
        Runs this program.
        """
        # Load the configuration, if no config exists this module will call the initial setup
        self.load_config()
        
