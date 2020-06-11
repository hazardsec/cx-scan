# cx-scan
This project helps automate onboarding and scanning in Checkmarx (on-premise only) and enables the use of instance profiles with cross-account access to AWS CodeCommit repositories. This enables organizations to onboard projects without gathering and maintaining credentials for every repository. It also can allow developers to set up webhooks or triggers to kick off incremental or full scans if deployed appropriately.

In order to function, the placeholders identified by <\*\*SOME_PLACEHOLDER_DESCRIPTION\*\*> will need to be set to the appropriate values. The following URL is an example of the format to use to supply additional values to the script or git wrapper:

https://git-codecommit.us-east-1.amazonaws.com/v1/repos/WebGoat#team=\CxServer#account=123456789012#role=CrossAccount-Role#region=us-east-1#incremental=False#clearqueued=True

Available Parameters  
team = Fully-qualified Checkmarx team name (need to use double backslashes when setting calling from codecommit trigger)  
project = Checkmarx project name if already set up and different from last part of repository path (default = the last segment of the repository URI)  
account = AWS Account Number in which codecommit repository resides  
role = AWS Role to assume that has access to codecommit repository (must be assumable by Checkmarx Manager's EC2 Instance profile)  
region = AWS Region  
incremental = True (default) enables incremental scanning; False will submit a full scan request  
clearqueued = False (default) does not clear queued entries for the current project when submitting a scan;  True clears the projects current scans unless they are already in "Scanning" status or "Canceled" status  

Installation  
Update git.py to inlcude the proper path to the git binary/executable on the Checkmarx Manager on line 94  
Add git.bat and git.py to a directory on the Checkmarx Manager and configure "Path to GIT client executable" under "Management > Application Settings > General" to point to git.bat (e.g. C:\Git\cmd\git.bat)  
Configure either setup_scan.py or lambda_function.py with environment-specific values by replacing placeholders with format of <\*\*SOME_PLACEHOLDER_DESCRIPTION\*\*>  
If deploying to Lambda, you will also need to include some of the python libraries used (see https://docs.aws.amazon.com/lambda/latest/dg/python-package.html#python-package-dependencies)  
