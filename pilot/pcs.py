import logging

from pilot.plugins.dask import executor as dask_cluster_executor

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PilotComputeService:
    """PilotComputeService (PCS) for creating and managing PilotComputes."""

    def __init__(self):
        self.pilot_job_id = None
        self.pilot_compute_description = None

    def cancel(self):
        pass

    def create_pilot(self, pilot_compute_description):
        self.pilot_compute_description = pilot_compute_description

        manager = self.__get_cluster_manager()

        self.pilot_job_id = manager.submit_pilot()

        pilot = PilotCompute(self.pilot_job_id, cluster_manager=manager)
        return pilot

    def __get_cluster_manager(self):
        framework_type = self.pilot_compute_description.get("type")

        if framework_type.startswith("dask"):
            return dask_cluster_executor.Executor(self.pilot_compute_description)  # Replace with appropriate manager

        raise PilotAPIException(f"Invalid framework type {framework_type}")


class PilotAPIException(Exception):
    pass


class PilotCompute(object):
    def __init__(self, saga_job=None, cluster_manager=None):
        self.saga_job = saga_job
        self.cluster_manager = cluster_manager

    def cancel(self):
        self.cluster_manager.cancel()

        if self.saga_job:
            self.saga_job.cancel()

    def submit(self, function_name):
        self.cluster_manager.submit_compute_unit(function_name)

    def get_state(self):
        if self.saga_job:
            return self.saga_job.get_state()

    def get_id(self):
        return self.cluster_manager.get_jobid()

    def get_details(self):
        return self.cluster_manager.get_config_data()

    def get_client(self):
        return self.cluster_manager.get_client()

    def wait(self):
        self.cluster_manager.wait()

    def get_context(self, configuration=None):
        return self.cluster_manager.get_context(configuration)
