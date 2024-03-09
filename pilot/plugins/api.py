import logging
import os
import time
import uuid
from enum import Enum
from urllib.parse import urlparse

from pilot.pilot_compute_service import PilotAPIException


class PilotStatus(Enum):
    PENDING = 1
    RUNNING = 2
    ERROR = 3


class PilotManager:
    def __init__(self, pilot_description):
        self.working_directory = pilot_description["working_directory"]
        self.job_id = uuid.uuid1().__str__()
        self.pilot_working_directory = os.path.join(self.working_directory, self.job_id)
        os.makedirs(self.pilot_working_directory)
        self.agent_output_log = os.path.join(self.pilot_working_directory, "agent.out")
        self.agent_error_log = os.path.join(self.pilot_working_directory, "agent.err")
        self.PILOT_STATUS_FILE = os.path.join(self.pilot_working_directory, "status")
        resource_url = pilot_description["resource"]
        self.url_scheme = urlparse(resource_url).scheme
        self.host = urlparse(resource_url).hostname
        self.dask_settings = pilot_description.get("dask_settings", None)
        self.ray_settings = pilot_description.get("ray_options", None)

        self.pilot_job_id = None

    def submit_pilot(self):
        pass

    def wait(self):
        status = self.get_pilot_status()
        while status not in [PilotStatus.RUNNING, PilotStatus.ERROR]:
            logging.info(f"Pilot status: {status}")
            time.sleep(10)
            status = self.get_pilot_status()

        logging.info(f"Waiting for Pilot completed: {status}")

    def get_pilot_status(self):
        if not os.path.exists(self.PILOT_STATUS_FILE):
            return PilotStatus.PENDING

        with open(self.PILOT_STATUS_FILE, "r") as fh:
            status = PilotStatus(int(fh.read().strip()))
            if status in [PilotStatus.PENDING, PilotStatus.RUNNING, PilotStatus.ERROR]:
                return status

        raise PilotAPIException("Invalid Pilot Status")

    def cancel_pilot(self):
        pass

    def submit_batch_pilot(self, startup_command):
        pass

