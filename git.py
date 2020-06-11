# include standard modules
import sys, os, tempfile, urllib.parse, re

# Set to True to enable print statements and logging to temporary file
debug = False

# Set AWS defaults
default_account = "<**DEFAULT_ACCOUNT**>"
default_role = "<**DEFAULT_ROLE**>"
default_region = "<**DEFAULT_REGION**>"

if debug:
    print(tempfile.gettempdir())
    f = tempfile.NamedTemporaryFile(mode="w+",delete=False)
    f.write(os.getcwd() + "\r\n")
    print(f.name)

args = sys.argv

indices = [i for i, elem in enumerate(args) if 'http' in elem]
git_url_index = indices[0]

# Split the git URL on the # sign to separate the URL and each of the options for cx_config
url_plus_args = urllib.parse.unquote(args[git_url_index]).split("#")

# Save the git URL
git_url = url_plus_args[0]

# Remove URL so only cx_config parameters are left
url_plus_args.pop(0)
    
after_url_args = ""

# Get any additional arguments after the URL with parameters
if len(args) > git_url_index:
	after_url_args = ' '.join(args[git_url_index + 1:])

# Put git statement back together without additional parameters
git_args = ' '.join(args[1:git_url_index]) + ' ' + git_url + ' ' + after_url_args

# Normalize branch name to prevent errors
git_args = git_args.replace("refs/heads/","")
git_args = git_args.replace("refs/tags/","")
git_args = git_args.replace("heads/","")
git_args = git_args.replace("tags/","")

if debug:
    print("URL Plus Args = " + ' '.join(url_plus_args))
    print("GIT URL = " + git_url)
    print("Custom arguments after URL = " + after_url_args)
    print("Arguments to pass to git = " + git_args)
    f.write("Arguments to pass to git = " + git_args + "\r\n")

# Create cx_config dictionary
if len(url_plus_args) > 0:
    cx_config = dict(item.split("=", 1) for item in url_plus_args)  
else:
    cx_config = {}

if debug:	
    print(cx_config)
    f.write("Cx Config = " + str(cx_config) + "\r\n")

# Set values based on cx_config parameters or the defaults at top of script
account = cx_config.get("account", default_account)
role = cx_config.get("role", default_role)
region = cx_config.get("region", default_region)

# Validate account number
if not re.search(r'^[0-9]{12}$',account):
    if debug:
        print ("Invalid account number!")
    account = default_account

# Validate role
if not re.search(r'^[-a-zA-Z0-9,@_=\.\+]{1,64}$',role):
    if debug:
        print ("Invalid role!")
    role = default_role

# Validate region
if not re.search(r'^[a-z]{2}-(([a-z]{4,9})||([a-z]{3}-[a-z]{4}))-\d$',region):
    if debug:
        print ("Invalid region!")
    region = default_region

if debug:
    print(cx_config)
    print("Account: " + account)
    print("Role: " + role)
    print("Region: " + region)

# Set up OS commands to run <**Update path to git executable below based on environment**>
os_commands = 'aws configure set profile.cross-account-role.region ' + region + ' & aws configure set profile.cross-account-role.role_arn arn:aws:iam::' + account + ':role/' + role + ' & aws configure set profile.cross-account-role.credential_source Ec2InstanceMetadata & C:\Git\cmd\git.exe config --global credential.helper "!aws codecommit --profile cross-account-role credential-helper $@">NUL & C:\Git\cmd\git.exe ' + git_args

if debug:
    print(os_commands)
    f.write(os_commands + "\r\n")
    f.close()

# Run OS commands
os.system(os_commands)
