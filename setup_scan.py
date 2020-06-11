# include standard modules
import argparse
import CxService
from copy import deepcopy

# Set AWS defaults
default_role = "<**DEFAULT_ROLE**>"
default_region = "<**DEFAULT_REGION**>"

def count_iterator(iterator):
	icopy = deepcopy(iterator)
	return len(list(icopy))

# Create argument parser object
parser = argparse.ArgumentParser()

# Accept any number of space delimited arguments in any format
parser.add_argument('all_args',nargs='*')

# Parse all the arguments
args = parser.parse_args()

# Split the git URL on the # sign to separate the options for cx_config
iter_args = iter(args.all_args[0].split("#"))

# Save the git URL
git_url = next(iter_args)

# Create cx_config dictionary
cx_config = {}
if count_iterator(iter_args) > 0:
    cx_config = dict(item.split("=") for item in iter_args)

if "branch" not in cx_config.keys():
    default_branch = "refs/heads/master"
    cx_config.update( { "branch" : default_branch } )
elif "refs" not in cx_config["branch"]:
    updated_branch = "refs/heads/" + cx_config["branch"]
    cx_config.update( { "branch" : updated_branch } )

base_url = ""
if "project" in cx_config.keys():
    base_url = git_url + "/"
else:
    url_parts = git_url.split("/")
    base_url = '/'.join(url_parts[0:len(url_parts)-1]) + "/"
    project = url_parts[len(url_parts)-1]
    cx_config.update( { "project" : project } )
    
if "account" in cx_config.keys():
    account = cx_config["account"]
    role = cx_config.get("role", default_role)
    region = cx_config.get("region", default_region)
    account_params = "#account=" + account + "#role=" + role + "#region=" + region
    cx_config.update( { "account_params" : account_params } )

cx_config.update( { "base_url" : base_url } )

cx = CxService.CxService("<**CHECKMARX_URL**>/CxRestAPI", "<**USER_FROM_KEYSTORE**>", "<**PASSWORD_FROM_KEYSTORE**>", cx_config)
cx.start_scan(cx_config)
