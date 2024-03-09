import subprocess
import abc

class JobManager(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def submit_job(self, script_content):
        """Submit a job and return the job ID."""
        pass

    @abc.abstractmethod
    def get_job_status(self, job_id):
        """Get the status of a submitted job."""
        pass

    def run_script(self, script_content):
        job_id = self.submit_job(script_content)
        print(f"Job submitted with ID: {job_id}")

        while True:
            status = self.get_job_status(job_id)
            print(f"Job Status: {status}")

            if status in ['COMPLETED', 'FAILED', 'CANCELLED']:
                break

    @staticmethod
    def execute_command(command):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        return {'output': output.decode('utf-8'), 'error': error.decode('utf-8'), 'return_code': process.returncode}
