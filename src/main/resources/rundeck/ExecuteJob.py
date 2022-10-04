#
# Copyright 2022 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

from datetime import timedelta
from time import sleep
from org.rundeck.client import RundeckClient     # type: ignore
from org.rundeck.client.api.model import JobRun  # type: ignore

# Initialize variables and objects
rdUsername = rundeckServer['username']
rdPassword = rundeckServer['password']
rdUrl = rundeckServer['url']
rdAuthToken = rundeckServer['rundeckAuthToken']
rundeckApi = None
job = None

# Authenticate either using username/password or use auth token
rundeckClientBuilder = RundeckClient.builder().baseUrl(rdUrl)
if rdAuthToken:
    rundeckApi = rundeckClientBuilder.tokenAuth(rdAuthToken).build().getService()
else:
    rundeckApi = rundeckClientBuilder.passwordAuth(rdUsername, rdPassword).build().getService()

listJobsResult = rundeckApi.listJobs(rundeckProject, None, None, rundeckJobName, rundeckJobGroup).execute()
if listJobsResult.successful:
    listJobs = listJobsResult.body()
    job = listJobs[0] if len(listJobs) > 0 else None

if job is None:
    raise TypeError(
        'No job has been found with name "%s" in project "%s"' %
        (rundeckJobName, rundeckProject)
    )
else:
    print(
        'Job "%s" has been found in project "%s"' %
        (job.getName(), job.getProject())
    )

jobRun = JobRun()
jobRun.setOptions(rundeckJobOptions)
runJobResult = rundeckApi.runJob(job.getId(), jobRun).execute()
if not runJobResult.successful:
    raise TypeError(
        'Job "%s" execution attempt has been failed in project "%s"' %
        (rundeckJobName, rundeckProject)
    )

# Either wait for execution or fire and forget
execution = runJobResult.body()
rundeckExecutionId = execution.getId()
rundeckJobStatus = execution.getPermalink()
rundeckJobDuration = -1
print(
    'Execution for job "%s" in project "%s" has been started with id "%s"' %
    (job.getName(), job.getProject(), rundeckExecutionId)
)

if rundeckdWaitForJob:
    while True:
        getExecutionStateResult = rundeckApi.getExecutionState(rundeckExecutionId).execute()
        if not getExecutionStateResult.successful:
            raise TypeError('Failed to get execution state for execution with id "%s"' % rundeckExecutionId)
        executionState = getExecutionStateResult.body()
        if executionState.getCompleted():
            rundeckJobStatus = executionState.getExecutionState()
            if rundeckJobStatus == 'SUCCEEDED':
                jobDuration = (executionState.getEndTime().unixtime - executionState.getStartTime().unixtime) / 1000
                rundeckJobDuration = str(timedelta(seconds=int(jobDuration + 0.5)))
            else:
                raise TypeError(
                    'Execution with id "%s" for job "%s" in project "%s" has "%s" state' %
                    (rundeckExecutionId, rundeckJobName, rundeckProject, rundeckJobStatus)
                )
            break
        sleep(5)
