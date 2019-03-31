import requests
import logging

"""
FlameBossMon
A general class to interact with the FlameBoss Controller API.
Although specificly created for FlameBoss-LifX, modules were constructed
in a general nature, to allow for reuse in other projects.

Repository: https://github.com/CameronEx/FlameBoss-LifX/
Code, documentation, isses and license info here.
"""

class FlameBossMon:
    def __init__(self, controller_id=None):
        logging.DEBUG("__init__: Initialising FlameBossMon")
        self.API_BASE: str = "https://myflameboss.com/api/v1"
        self.headers: str = { "X-API-VERSION": "3" }
        self.controller_id: str = controller_id
        self.cook_id: int = None
        self.target_temp: int = None
        self.temp_drift: int = None
        self.last_dp: int = 0
        self.current_temp: int = None

    def get_device_info(self):
        """
        Builds payload to obtain controller info. Parses, then saves to self.
        return: None
        """
        # Build, then send, payload
        uri: str = f"/devices/{self.controller_id}"
        logging.DEBUG(f"get_device_info: built URI: {uri}")
        response: dict = self.poll_api(uri)

        # Make sure our controller is online
        logging.DEBUG("get_device_info: Checking controller status.")
        logging.DEBUG(f"get_device_info: status is {response["online"]}")
        try:
            response["online"]
        except:
            logger.CRITICAL("Controller is not online.")
        logging.DEBUG("get_device_info: Controller is online.")

        # Collect interesting information
        try:
            logging.DEBUG("get_device_info: Setting info")
            logging.DEBUG(f"get_device_info: last cook ID is {response["most_recent_cook"]["id"]}")
            self.cook_id = response["most_recent_cook"]["id"]
            logging.DEBUG(f"get_device_info: Temp drift is {response["config"]["Pit_Alarm_Range_tdc"]}")
            self.temp_drift = response["config"]["Pit_Alarm_Range_tdc"]
        except KeyError as e:
            logging.CRITICAL("A unexpected response was received from the FlameBoss API and we did not"
            "receive some critical information.\nSpeficially, the issue was:\n\n{e}\nPlease log this as an issue"
            "here: https://github.com/CameronEx/FlameBoss-LifX/issues")

    def get_cook(self):
        """
        Builds payload to collect cook information from API.
        """
        # Build, then send, payload
        uri: str = f"/cooks/{self.cook_id}?skip_cnt={self.last_dp}"
        logging.DEBUG(f"get_cook: built URI: {uri}")
        response: dict = self.poll_api(uri)

        # Ensire the controller hasn't gone offline
        logging.DEBUG(f"get_cook: Checking controller status.")
        if not response["online"]:
            # Quit if controller is no longer available
            logging.CRITICAL("Controller has gone offline. Exiting.")
        logging.DEBUG(f"get_cook: Controller is online.")

        # Set skip count to last data point, we don't need all data points every single time
        self.last_dp = response["data_cnt""]
        logging.DEBUG(f"get_cook: Last datapoint was {self.last_dp}")

        # Pull the latest data point out and collect interesting information
        dp = response["data"][-1]
        logging.DEBUG(f"get_cook: Last datapoint was:\n{dp}")
        self.current_temp = dp["pit_temp"]
        if dp["set_temp"] not self.target_temp:
            logging.DEBUG(f"get_cook: Target temp has changed from {self.set_temp}. Updating.")
            self.target_temp = dp["set_temp"]

    def poll_api(self, target_uri,):
        """
        Requests information from API, as instructed by calling function
        return: dict
        """
        # Build full URL target, nake API call
        target: str = self.API_BASE + uri
        logging.DEBUG(f"poll_api: built URL {target}, making request.")
        request = requests.get(target, headers=self.headers)

        # Ensure we received an expected response
        try:
            request.raise_for_status()
            logging.DEBUG(f"poll_api: response code was expected: {request.status_code}")
        except Exception as e:
            logger.CRITICAL(f"Received {request.status_code} code from API")
            logger.exception(e)

        # Return the data as a dictionary
        logging.DEBUG(f"poll_api: returning data:\n{request.json}")
        return request.json()






if __name__ == "__main__":
    # Logger config

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    controller_id = "26362"
    fb_mon = FlameBossMon(controller_id)
