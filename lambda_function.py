import json
import boto3
import CxService
from copy import deepcopy

def count_iterator(iterator):
	icopy = deepcopy(iterator)
	return len(list(icopy))
	
def SendSNS(subject, message, topic_arn):
    sns     = boto3.client("sns")
    try:
        sns_response = sns.publish(
            TopicArn = topic_arn,
            Message = message,
            Subject = subject,
            MessageStructure = "string"
        )
    except Exception as e:
        print("ERROR! Failed to publish message to SNS topic")
        print("ERROR! Exception: " + str(e))

def lambda_handler(event, context):
    ssm     = boto3.client("ssm", endpoint_url="<**ENDPOINT_URL_IF_NEEDED_IF_NOT_REMOVE_PARAMETER**>")
    outputMessage = "Event = " + str(event) + "\r\n"
    print(event)
    innerEvent    = event["Records"][0]
    nameOfTrigger = innerEvent["eventTriggerName"]
    outputMessage = outputMessage + "Name of trigger = " + nameOfTrigger + "\r\n"
    print(nameOfTrigger)
    
    try:
        # Pull connection information from SSM
        userParam = ssm.get_parameter(Name="<**USER_PARAMETER_NAME**>")
        passwordParam = ssm.get_parameter(Name='<**PASS_PARAMETER_NAME**>', WithDecryption=True)
        serverParam = ssm.get_parameter(Name='<**CHECKMARX_MANAGER_SERVER_URL_PARAMETER_NAME**>')
        securityTeamTopicParam = ssm.get_parameter(Name='<**SNS_TOPIC_ARN_PARAMETER**>')
        securityTeamTopic = securityTeamTopicParam['Parameter']['Value']
        
        user = userParam['Parameter']['Value']
        password = passwordParam['Parameter']['Value']
        server = serverParam['Parameter']['Value']
        customData    = innerEvent["customData"]
        
        # Split the git URL on the # sign to separate the options for cx_config
        iter_args = iter(customData.split("#"))
        
        # Save the git URL
        git_url = next(iter_args)
        git_url.rstrip("/")
        
        # Create cx_config dictionary
        cx_config = {}
        if count_iterator(iter_args) > 0:
            cx_config = dict(item.split("=", 1) for item in iter_args)
            
        if "branch" not in cx_config.keys():
            default_branch = "refs/heads/master"
            cx_config.update( { "branch" : default_branch } )
        elif "refs" not in cx_config["branch"]:
            updated_branch = "refs/heads/" + cx_config["branch"]
            cx_config.update( { "branch" : updated_branch } )
        
        base_url = ""
        if "project" in cx_config.keys():
            base_url = git_url
            cx_config.update( { "project" : "#" + project } )
        else:
            url_parts = git_url.split("/")
            base_url = '/'.join(url_parts[0:len(url_parts)-1]) + "/"
            project = url_parts[len(url_parts)-1]
            cx_config.update( { "project" : project } )
       
        if "account" in cx_config.keys():
            account = cx_config["account"]
            role = cx_config.get("role", "<**default_role_name**>")
            region = cx_config.get("region", "<**default_region**>")
            account_params = "#account=" + account + "#role=" + role + "#region=" + region
            cx_config.update( { "account_params" : account_params } )

        cx_config.update( { "base_url" : base_url } )
        
        outputMessage = outputMessage + "cx_config = " + str(cx_config) + "\r\n"    
        outputMessage = outputMessage + "server = " + server + "\r\n"   

        cx = CxService.CxService(server + "/CxRestAPI", user, password, cx_config)

        cx.start_scan(cx_config)
    except Exception as e:
        print(str(e))
        SendSNS("Error: Checkmarx Setup & Scan Lambda",str(e),securityTeamTopic)
    finally:
        return outputMessage
