# cx-scan
This project helps automate onboarding and scanning in Checkmarx and enables the use of instance profiles with cross-account access to AWS CodeCommit repositories. This enables organizations to onboard projects without gathering and maintaining credentials for every repository. It also can allow developers to set up webhooks or Lambda triggers to kick off incremental or full scans if deployed appropriately.

In order to function, the placeholders identified by <\**SOME_PLACEHOLDER_DESCRIPTION\**> will need to be set to the appropriate values. The following URL is an example of the format to use to supply additional values to the script or git wrapper:

https://git-codecommit.us-east-1.amazonaws.com/v1/repos/WebGoat#team=\CxServer#account=123456789012#role=CrossAccount-Role#region=us-east-1
