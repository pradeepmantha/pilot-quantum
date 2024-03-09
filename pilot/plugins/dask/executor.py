import logging
import os

from distributed import SSHCluster, Client

from pilot.plugins.api import PilotManager, PilotStatus


class Executor(PilotManager):
    def __init__(self, pilot_description):
        super().__init__(pilot_description)
        self.dask_cluster = None
        self.dask_client = None

    def submit_pilot(self, startup_command=None):
        if self.url_scheme == "ssh":
            self.start_dask_ssh_cluster()
        else:
            super().submit_batch_pilot(startup_command)

        return self.pilot_job_id

    def get_client(self):
        return self.dask_client

    def start_dask_ssh_cluster(self):
        hosts = [self.host, self.host]
        if self.dask_settings:
            self.dask_cluster = SSHCluster(hosts, self.dask_settings)
        else:
            self.dask_cluster = SSHCluster(hosts)

        self.dask_client = Client(self.dask_cluster)
        logging.info(self.dask_client.scheduler_info())
        self.host = self.dask_client.scheduler_info()["address"]

        if self.host is not None:
            with open(self.PILOT_STATUS_FILE, "w") as status_file:
                status_file.write(PilotStatus.RUNNING.value.__str__())