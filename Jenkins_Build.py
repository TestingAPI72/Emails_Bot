import requests
import re
import sys
import json
import time
import subprocess
from subprocess import PIPE

QUEUE_POLL_INTERVAL = 2
JOB_POLL_INTERVAL = 20
OVERALL_TIMEOUT = 14400 # 4 hour

# job specifics: should be passed in
auth_token = '3112d5d74bb48ad0249f8f717e5ca414'
jenkins_uri = '10.174.81.44:8080'
job_names = ['SZ6_1_AP_SoftGRE_Enhancements', 'SZ6_1_AP_Web_Reputation_and_Safe_Search_Enhancements',
                 'SZ6_1_Wired_Ratelimit_support_and_Increased_Ratelimit_Enhancements_Suit']


for job_name in job_names:

    # start the build

    start_build_url = 'http://{}/job/{}/buildWithParameters?token={}'.format(jenkins_uri, job_name, auth_token)
    response = requests.post(start_build_url)

    # from return headers get job queue location
    #
    m = re.match(r"http.+(queue.+)\/", response.headers['Location'])
    if not m:
        # To Do: handle error
        print("Job started request did not have queue location")
        sys.exit(1)

    # poll the queue looking for job to start
    #
    queue_id = m.group(1)
    job_info_url = 'http://{}/{}/api/json'.format(jenkins_uri,queue_id)
    elasped_time = 0
    print('{} Job {} added to queue: {}'.format(time.ctime(), job_name, job_info_url))
    while True:
        l = requests.get(job_info_url)
        jqe = l.json()
        task = jqe['task']['name']
        try:
            job_id = jqe['executable']['number']
            break
        except:
            time.sleep(QUEUE_POLL_INTERVAL)
            elasped_time += QUEUE_POLL_INTERVAL

        if (elasped_time % (QUEUE_POLL_INTERVAL * 10)) == 0:
            print ("{}: Job {} not started yet from {}".format(time.ctime(), job_name, queue_id))

    # poll job status waiting for a result
    #
    job_url = 'http://{}/job/{}/{}/api/json'.format(jenkins_uri, job_name, job_id)
    start_epoch = int(time.time())
    while True:
        print ("{}: Job started URL: {}".format(time.ctime(), job_url))
        j = requests.get(job_url)
        jje = j.json()
        result = jje['result']
        if result == 'SUCCESS':
            # Do success steps
            print ("{}: Job: {} Status: {}".format(time.ctime(), job_name, result))
            break
        elif result == 'FAILURE':
            # Do failure steps
            print ("{}: Job: {} Status: {}".format(time.ctime(), job_name, result))
            break
        elif result == 'ABORTED':
            # Do aborted steps
            print("{}: Job: {} Status: {}".format(time.ctime(), job_name, result))
            break
        else:
            print( "{}: Job: {} Status: {}. Polling again in {} secs".format(
                    time.ctime(), job_name, result, JOB_POLL_INTERVAL))

        cur_epoch = int(time.time())
        if (cur_epoch - start_epoch) > OVERALL_TIMEOUT:
            print( "No status before timeout of {} secs".format(OVERALL_TIMEOUT))
            sys.exit(1)

        time.sleep(JOB_POLL_INTERVAL)