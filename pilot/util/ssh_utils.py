import os, sys
import time
import subprocess


def execute_ssh_command(host, user=None, command="/bin/date", arguments=None, working_directory=os.getcwd(),
                        job_output=None, job_error=None, keyfile=None) -> object:
    """
    Execute SSH Command
    :param host:
    :param user:
    :param command:
    :param arguments:
    :param working_directory:
    :param job_output:
    :param job_error:
    :return: True/False - Success or Failure
    """

    user_parameter = ""
    if user is not None:
        user_parameter = "-l {}".format(user)

    key_parameter = ""
    if keyfile is not None:
        key_parameter = "-i {}".format(keyfile)

    arguments_parameter = ""
    if arguments is not None:
        arguments_parameter = " ".join(arguments)
    #     ssh_command = "ssh -o 'StrictHostKeyChecking=no' -l %s %s -t \"bash -ic '%s'\"" % (user, host, command)
    # else:
    #     ssh_command = "ssh -o 'StrictHostKeyChecking=no' %s -t \"bash -ic '%s'\"" % (host, command)

    ssh_command = f"ssh -o 'StrictHostKeyChecking=no' {key_parameter} {user_parameter} {host} -t \"bash -ic '{command} {arguments_parameter}'\""
    print("Execute SSH : {0}".format(ssh_command))
    # status = subprocess.call(command, shell=True)
    for i in range(3):
        ssh_process = subprocess.Popen(ssh_command, shell=True,
                                       cwd=working_directory,
                                       stdout=job_output,
                                       stderr=job_error,
                                       close_fds=True)
        time.sleep(10)
    if ssh_process.poll is not None:
        return True
    return False
