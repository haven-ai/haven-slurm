from haven import haven_utils as hu
from haven import haven_chk as hc
import os

import time
import copy
import pandas as pd
import numpy as np
import getpass
import pprint
import requests


# Job submission
# ==============
def submit_job(api, account_id, command, job_config, workdir, savedir_logs=None):
    # read slurm setting
    lines = "#! /bin/bash \n"
    lines += "#SBATCH --account=%s \n" % account_id
    for key in list(job_config.JOB_CONFIG.keys()):
        lines += "#SBATCH --%s=%s \n" % (key, job_config.JOB_CONFIG[key])
    path_log = os.path.join(savedir_logs, "logs.txt")
    path_err = os.path.join(savedir_logs, "err.txt")
    lines += "#SBATCH --output=%s \n" % path_log
    lines += "#SBATCH --error=%s \n" % path_err

    lines += command

    file_name = os.path.join(savedir_logs, "bash.sh")
    hu.save_txt(file_name, lines)

    # launch the exp
    submit_command = "sbatch %s" % file_name
    while True:
        try:
            job_id = hu.subprocess_call(submit_command).split()[-1]
        except Exception as e:
            if "Socket timed out" in str(e):
                print("slurm time out and retry now")
                time.sleep(1)
                continue
        break

    # delete the bash.sh
    os.remove(file_name)

    return job_id


# Job status
# ===========
def get_job(api, job_id):
    """Get job information."""
    job_info = get_jobs_dict(None, [job_id])[job_id]
    job_info["job_id"] = job_id

    return job_info


def get_jobs(api, account_id):
    ''' get all jobs launched by the current user'''
    # todo: cannot get command! fix it!
    command = "squeue --user=%s" % getpass.getuser()
    while True:
        try:
            job_list = hu.subprocess_call(command)
            job_list = job_list.split('\n')
            job_list = [v.lstrip().split(" ")[0] for v in job_list[1:]]
            result = []
            for job_id in job_list:
                result.append(get_job(None, job_id))
        except Exception as e:
            if "Socket timed out" in str(e):
                print("squeue time out and retry now")
                time.sleep(1)
                continue
        break
    return result


def get_jobs_dict(api, job_id_list, query_size=20):
    jobs_dict = {}

    command = "sacct --jobs=%s" % str(job_id_list)[1:-1].replace(" ", "")
    while True:
        try:
            job_list = hu.subprocess_call(command)
        except Exception as e:
            if "Socket timed out" in str(e):
                print("sacct time out and retry now")
                time.sleep(1)
                continue
        break

    lines = job_list.split('\n')
    header = lines[0]
    state_index = header.index("State")
    job_id_index = header.index("JobID")
    cpu_time_index = header.index("CPUTime")
    for line in lines[2:]:
        elements = line.split()
        job_id = elements[job_id_index]
        if '.' in job_id:
            continue
        state = elements[state_index]
        cpuTime = elements[cpu_time_index]
        jobs_dict[job_id] = {"state": state, "cpuTime": cpuTime, "runs": -1}

    return jobs_dict

# Job kill
# ===========


def kill_job(api, job_id):
    """Kill a job job until it is dead."""
    job = get_job(api, job_id)

    if job["status"] in ["CANCELLED", "COMPLETED"]:
        print('%s is already dead' % job_id)
    else:
        kill_command = "scancel %s" % job_id
        while True:
            try:
                hu.subprocess_call(kill_command)
                print('%s CANCELLING...' % job_id)
            except Exception as e:
                if "Socket timed out" in str(e):
                    print("scancel time out and retry now")
                    time.sleep(1)
                    continue
            break

        # confirm cancelled
        job = get_job(api, job_id)
        while job["state"] != "CANCELLED":
            time.sleep(2)
            job = get_job(api, job_id)

        print('%s now is dead.' % job_id)
