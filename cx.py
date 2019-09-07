import CxService

#cx_config = {
#    "project": "<end_of_repo_url>",
#    "base_url": "https://git-codecommit.us-east-1.amazonaws.com/v1/repos/",
#    "default_branch": "refs/heads/master"
#}

cx_config = {
    "team": "\\CxServer",
    "project": "WebGoat",
    "base_url": "https://github.com/WebGoat/",
    "default_branch": "refs/heads/master"
}

cx = CxService.CxService("https://checkmarx.local/CxRestAPI", "admin", "*******", cx_config)
cx.start_scan(cx_config)
