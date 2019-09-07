from botocore.vendored import requests
import os
import re
import time
import json
from requests_toolbelt import MultipartEncoder


class CxRestClient(object):

    def __init__(self, server, username, password, cx_config):
        # self.server, self.username, self.password = self.get_config()
        self.server = server
        self.username = username
        self.password = password
        self.urls = self.get_urls()
        self.token = self.get_token()
        self.headers = {"Authorization": "Bearer " + self.token['access_token'], "Content-Type": "application/json;charset=UTF-8"}
        self.headers.update({"Accept": "application/json;v=2.0", "api-version": "2.0"})
        pass

    @staticmethod
    def get_config():
        try:
            with open("config.json") as config:
                conf = json.loads(config.read())
            server = conf.get("server")
            username = conf.get("username")
            password = conf.get("password")
            return server, username, password
        except Exception as e:
            raise Exception("Unable to get configuration: {} . ".format(e))

    @staticmethod
    def get_urls():
        try:
            with open("urls.json") as urls:
                return json.loads(urls.read())
        except Exception as e:
            raise Exception("Unable to get configuration: {} . ".format(e))

    def send_requests(self, keyword, url_sub=None, headers=None, data=None):
        if url_sub is None:
            url_sub = dict(pattern="", value="")
        try:
            url_parameters = self.urls.get(keyword, None)
            if not url_parameters:
                raise Exception("Keyword not in urls.json")
            url = self.server + re.sub(url_sub.get("pattern"),
                                       url_sub.get("value"),
                                       url_parameters.get("url_suffix"))
            s = requests.Session()
            headers = headers or self.headers
            req = requests.Request(method=url_parameters.get("http_method"),
                                   headers=headers,
                                   url=url, data=data)
            prepped = req.prepare()
            #print(req.method)
            #print(req.url)
            #print(req.headers.items())
            #print(req.data)
            resp = s.send(prepped)
            if resp.status_code == 200:
                if headers.get("Accept") == "application/json;v=1.0":
                    return resp
                else:
                    return resp
            elif resp.status_code in [201, 202]:
                return resp
            elif resp.status_code == 204:
                return resp
            elif resp.status_code == 400:
                raise Exception(" 400 Bad Request: {}.".format(resp.text))
            elif resp.status_code == 404:
                rd = json.loads(resp.text)
                if rd['messageCode'] == 47642:
                    return resp
                else:
                    raise Exception(" 404 Not found {}.".format(resp.text))
            else:
                raise Exception(" Failed: {}.".format(resp.text))

        except Exception as e:
            raise Exception("{}".format(e))

    def get_token(self):
        data = {"username": self.username,
                "password": self.password,
                "grant_type": "password",
                "scope": "sast_rest_api",
                "client_id": "resource_owner_client",
                "client_secret": '014DF517-39D1-4453-B7B3-9930C563627C'}
        url = self.server + self.urls.get("token").get("url_suffix")
        token = requests.post(url=url, data=data)
        return token.json()

    def login(self):
        data = {
            "username": self.username,
            "password": self.password
        }
        try:
            url = self.server + self.urls.get("login").get("url_suffix")
            r = requests.post(url, data=data)
            if r.status_code == 200:
                cx_cookie = r.cookies.get("cxCookie")
                cx_csrf_token = r.cookies.get("CXCSRFToken")
                return {
                    "cxCookie": cx_cookie,
                    "CXCSRFToken": cx_csrf_token,
                }
            elif r.status_code == 400:
                raise Exception(" 400 Bad Request. ")
            else:
                raise Exception(" login Failed. ")
        except Exception as e:
            raise Exception("Unable to get cookies: {} .".format(e))

    def get_all_teams(self):
        keyword = "get_all_teams"
        return self.send_requests(keyword=keyword)

    def get_all_projects(self):
        keyword = "get_all_projects"
        return self.send_requests(keyword=keyword)      

    def get_project_details_by_id(self, project_id):
        keyword = "get_project_details_by_id"
        url_sub = {"pattern": "{project_id}",
                   "value": project_id}
        return self.send_requests(keyword=keyword, url_sub=url_sub)

    def create_project_with_default_configuration(self, name, owning_team, is_public=True):
        keyword = "create_project_with_default_configuration"
        data = {"name": name,
                "owningTeam": owning_team,
                "isPublic": is_public}
        data_json = json.dumps(data)
        return self.send_requests(keyword=keyword, data=data_json)

    def upload_source_code_zip_file(self, project_id, zip_path):
        keyword = "upload_source_code_zip_file"
        url_sub = {"pattern": "{project_id}",
                   "value": str(project_id)}
        file_name = zip_path.split()[-1]
        files = MultipartEncoder(fields={"zippedSource": (file_name,
                                                          open(zip_path, 'rb'),
                                                          "application/zip")})
        headers = self.headers.copy()
        headers.update({"Content-Type": files.content_type})
        return self.send_requests(keyword=keyword, url_sub=url_sub, headers=headers, data=files)

    def get_all_scan_details_in_queue(self):
        keyword = "get_all_scan_details_in_queue"
        return self.send_requests(keyword=keyword)    

    def get_remote_source_settings_for_git_by_project_id(self, id):
        keyword = "get_remote_source_settings_for_git_by_project_id"
        url_sub = {"pattern": "{id}",
                   "value": str(id)}
        return self.send_requests(keyword=keyword, url_sub=url_sub).json()
        
    def set_remote_source_setting_to_git(self, project_id, config_path=None,
                                         git_url=None, branch=None):
        keyword = "set_remote_source_setting_to_git"
        url_sub = {"pattern": "{project_id}",
                   "value": str(project_id)}
        if config_path is not None:
            try:
                with open(config_path) as f:
                    config = json.loads(f.read())
                git_url = config.get("url")
                branch = config.get("branch")
            except Exception as e:
                raise e
        data = {"url": git_url,
                "branch": branch}
        data_json = json.dumps(data)        
        return self.send_requests(keyword=keyword, url_sub=url_sub, data=data_json)        
    
    def create_new_scan(self, project_id, is_incremental=False, is_public=True, force_scan=True):
        keyword = "create_new_scan"
        data = {"projectId": project_id,
                "isIncremental": is_incremental,
                "isPublic": is_public,
                "forceScan": force_scan}
        data_json = json.dumps(data)
        return self.send_requests(keyword=keyword, data=data_json)

    def create_an_osa_scan_request(self, project_id, zip_path):
        keyword = "create_an_osa_scan_request"
        file_name = zip_path.split()[-1]
        files = MultipartEncoder(fields={"projectId": str(project_id),
                                         "zippedSource": (file_name,
                                                          open(zip_path, 'rb'),
                                                          "application/zip")})
        # print(files)
        headers = self.headers.copy()
        headers.update({"Content-Type": files.content_type})
        return self.send_requests(keyword=keyword, headers=headers, data=files).json()
        
