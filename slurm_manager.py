from .. import haven_utils as hu
from .. import haven_chk as hc
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
    # todo: use sacct can get the state of completed job, but limited info
    # sacct header: Account, User, JobID, Start, End, AllocCPUS, Elapsed, AllocTRES, CPUTime, AveRSS, MaxRSS MaxRSSTask MaxRSSNode, NodeList ExitCode, State
    # todo: return job obj?
    command = "scontrol show job %s" % (job_id)
    job_info = ''
    while True:
      try:
        job_info = hu.subprocess_call(command)
        job_info = job_info.replace('\n', '')
        job_info = {v.split('=')[0]:v.split('=')[1] for v in job_info.split(' ') if '=' in v }
      except Exception as e:
        if "Socket timed out" in str(e):
          print("scontrol time out and retry now")
          time.sleep(1)
          continue
      break
    return job_info


def get_jobs(api, account_id):
    ''' get all jobs launched by the current user'''
    # todo: can only get the running and pending jobs; use sacct?
    # use user_name instead of account_id for the search
    # todo: return job objs?
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
              print("scontrol time out and retry now")
              time.sleep(1)
              continue
      break
    return result
           

def get_jobs_dict(api, job_id_list, query_size=20):
    # todo: not returning job obj!! error can occur in haven_jobs
    # info: state, command(?), id, run(?)
   
    # todo: get all jobs at once
    jobs = []
    jobs_dict = {}

    command = "sacct --jobs=%s" % str(job_id_list)[1:-1].replace(" ", "")
    job_list = hu.subprocess_call(command)
    lines = job_list.split('\n')
    header = lines[0]
    state_index = header.index("State")
    job_id_index = header.index("JobID")
    for line in lines[2:]:
      job_id = line.split()[job_id_index]
      if '.' in job_id:
        continue
      state = line.split()[state_index]
      jobs_dict[job_id] = state


    # for i in range(0, len(job_id_list)):
    #     job_id_string = "id__in="
    #     for job_id in  job_id_list[i:i + query_size]:
    #         job_id_string += "%s," % job_id
    #     job_id_string = job_id_string[:-1]
    #     jobs += api.v1_cluster_job_get(q=job_id_string).items

    # jobs_dict = {job.id: job for job in jobs}

    return jobs_dict
    
# Job kill
# ===========
def kill_job(api, job_id):
    """Kill a job job until it is dead."""
    job = get_job(api, job_id)

    # todo: running and pending only?
    if not job["status"] == "RUNNING" or "PENDING":
        print('%s is already dead' % job_id)
    else:
        # toolkit
        kill_command  = "scancel %s" % job_id
        while True:
          try:
            hu.subprocess_call(kill_command)
            print('%s CANCELLING...' % job_id) 
          except Exception as e:
            # todo: confirm cacelled state?
            if "Socket timed out" in str(e):
              print("scancel time out and retry now")
              time.sleep(1)
              continue
          break
        print('%s now is dead.' % job_id)
        return
