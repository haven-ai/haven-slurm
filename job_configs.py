import os
import getpass

# need to set up the environment variable before use
ACCOUNT_ID = 'def-dnowrouz-ab'
USER_NAME = getpass.getuser()
# change the output directory
JOB_CONFIG = {
    'account_id':None,
    'time': '12:00:00',
    'cpus-per-task': '2',
    'mem-per-cpu': '20G',
    'gres': 'gpu:v100:1',
}