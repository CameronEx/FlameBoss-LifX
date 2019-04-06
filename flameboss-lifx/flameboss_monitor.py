import requests
import logging

"""
FlameBossMon
A general class to interact with the FlameBoss Controller API.
Although specifically created for FlameBoss-LifX, modules were constructed
in a general nature, to allow for reuse in other projects.

Repository: https://github.com/CameronEx/FlameBoss-LifX/
Code, documentation, isses and license info here.
"""


class FlameBossMon:
    def __init__(self, controller_id=None):
        self.API_BASE: str = "https://myflameboss.com/api/v1"
        self.headers: str = {"X-API-VERSION": "3"}
        self.controller_id: str = controller_id
        self.cook_id: int = None
        self.target_temp: int = None
        self.temp_drift: int = None
        self.last_dp: int = 0
        self.current_temp: int = None

        # Logging congig
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.ch.setFormatter(self.formatter)
        self.logger.addHandler(self.ch)

    def get_device_info(self):
        """
        Builds payload to obtain controller info. Parses, then saves to self.
        return: None
        """
        # Build, then send, payload
        uri: str = f"/devices/{self.controller_id}"
        logging.debug(f"get_device_info: built URI: {uri}")
        response: dict = self.poll_api(uri)

        # Make sure our controller is online
        logging.debug("get_device_info: Checking controller status.")
        logging.debug(f"get_device_info: status is {response['online']}")
        if not response["online"]:
            self.logger.critical("Controller is not online.")
            raise StopIteration

        logging.debug("get_device_info: Controller is online.")

        # Collect interesting information
        try:
            logging.debug("get_device_info: Setting info")
            logging.debug(f"get_device_info: last cook ID is {response['most_recent_cook']['id']}")
            self.cook_id = response["most_recent_cook"]["id"]
            logging.debug(f"get_device_info: Temp drift is {response['config']['Pit_Alarm_Range_tdc']}")
            self.temp_drift = int(response["config"]["Pit_Alarm_Range_tdc"]/10)
        except KeyError as e:
            logging.critical(f"A unexpected response was received from the FlameBoss API and we did not"
                             f"receive some critical information.\nSpecifically, the issue was:\n\n{e}\n"
                             f"Please log this as an issue here: https://github.com/CameronEx/FlameBoss-LifX/issues"
                             )
            raise

    def get_cook(self):
        """
        Builds payload to collect cook information from API.
        """
        # Build, then send, payload
        uri: str = f"/cooks/{self.cook_id}?skip_cnt={self.last_dp}"
        logging.debug(f"get_cook: built URI: {uri}")
        response: dict = self.poll_api(uri)

        # Set skip count to last data point, we don't need all data points every single time
        self.last_dp = response["data_cnt"]
        logging.debug(f"get_cook: Last datapoint was {self.last_dp}")

        # Pull the latest data point out and collect interesting information
        if len(response["data"]) > 0:
            dp = response["data"][-1]
            logging.debug(f"get_cook: Last datapoint was:\n{dp}")
            self.current_temp = int(dp["pit_temp"]/10)
            if dp["set_temp"] is not self.target_temp:
                logging.debug(f"get_cook: Target temp has changed from {self.target_temp}. Updating.")
                self.target_temp = int(dp["set_temp"]/10)
        else:
            logger.debug("No new DP. Either controller is offline or polling too fast.")

    def poll_api(self, target_uri):
        """
        Requests information from API, as instructed by calling function
        return: dict
        """
        # Build full URL target, nake API call
        target: str = self.API_BASE + target_uri
        logging.debug(f"poll_api: built URL {target}, making request.")
        request = requests.get(target, headers=self.headers)

        # Ensure we received an expected response
        try:
            request.raise_for_status()
            logging.debug(f"poll_api: response code was expected: {request.status_code}")
        except Exception as e:
            self.logger.critical(f"Received {request.status_code} code from API")
            self.logger.exception(e)

        # Return the data as a dictionary
        logging.debug(f"poll_api: returning data:\n{request.json}")
        return request.json()


if __name__ == "__main__":
    # Logger config

    self.logger = logging.getLogger(__name__)
    self.logger.setLevel(logging.debug)
    ch = logging.StreamHandler()
    ch.setLevel(logging.debug)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    self.logger.addHandler(ch)

    controller_id = "26362"
    fb_mon = FlameBossMon(controller_id)
