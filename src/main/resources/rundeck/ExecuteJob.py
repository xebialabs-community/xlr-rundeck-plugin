#
# Copyright 2019 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
from org.rundeck.api import RundeckClient
from org.rundeck.api import RunJobBuilder
from org.rundeck.api import OptionsBuilder
from org.rundeck.api.domain import RundeckExecution


# Intialize variables and objects
rdUsername  = rundeckServer['username']
rdPassword  = rundeckServer['password']
rdUrl       = rundeckServer['url']
rdAuthToken = rundeckServer['rundeckAuthToken']
jobOptions  = OptionsBuilder()
nodeFilters = OptionsBuilder()
rundeck     = None

# Build the job options 
for key,value in rundeckJobOptions.iteritems():
    jobOptions.addOption(key,value)

# Authenticate either using username/apssword or use auth token
if rdAuthToken:
     rundeck = RundeckClient.builder().url(rdUrl).token(rdAuthToken).build() 
else:
     rundeck = RundeckClient.builder().url(rdUrl).login(rdUsername, rdPassword).build()



# Validate job exist and get the UUID
# Not using findjobs as that matches a substring and retutns first match... !
# Job names are not unique hence iterating through list udner the project and finding the matched one

jobToRun  = None
jobs      = rundeck.getJobs(rundeckProject);

if rundeckJobGroup:
   rdjobFullName = "%s%s%s" % (rundeckJobGroup,"/",rundeckJobName)
else:
    rdjobFullName = rundeckJobName


for job in jobs:
    if job.getFullName() == rdjobFullName:
       jobToRun = job
       break

if jobToRun is None:
   raise TypeError("No job found with name:\"%s\" in project: \"%s\" \n" % (rdjobFullName, rundeckProject))
else:
     print "Job found: %s in project: %s \n" % (jobToRun.getFullName(),rundeckProject)

# Set the Job Options
rundeckJobName = jobToRun.getFullName()
runJob         = RunJobBuilder.builder().setJobId(jobToRun.id).setOptions(jobOptions.toProperties()).build()


# Either wait for execution or fire and forget
if rundeckdWaitForJob == True :
  execution           = rundeck.runJob(runJob)
  rundeckJobStatus    = execution.status.toString()
  rundeckJobDuration  = execution.duration
  rundeckExecutionId  = execution.id
  print "Execution #%s for job %s succeeded\n" % (rundeckExecutionId, rundeckJobName)

  # Task should fail if output is not SUCCEEDED
  if execution.status != RundeckExecution.ExecutionStatus.SUCCEEDED:
     raise TypeError("Execution #%s for job %s FAILED\n" % (rundeckExecutionId, rundeckJobName))

else:
   execution = rundeck.triggerJob(runJob)
   rundeckJobStatus   = "%s\n" % execution.url
   rundeckJobDuration = -1
   rundeckExecutionId = execution.id
   print rundeckJobStatus     


