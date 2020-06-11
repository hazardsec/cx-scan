import json
import CxRest


class CxService(object):

    unknown_id = -1
    unknown_id_str = "-1"
    source_artifact = "SourceArtifact"
    build_artifact = "BuildArtifact"

    def __init__(self, server, username, password, cx_config):
        self.server = server
        self.username = username
        self.password = password
        self.cx_config = cx_config
        self.cx = CxRest.CxRestClient(server, username, password, cx_config)
        pass

    def get_team_id(self, team):
        teams = self.cx.get_all_teams().json()
        for t in teams:
            if t['fullName'] == team:
                return t['id']
        return CxService.unknown_id_str
        
    def get_scan_queue_for_project(self, project):
        queued_scans = self.cx.get_all_scan_details_in_queue()
        queued_scans = [obj for obj in queued_scans if(obj["project"]["id"] == project and obj["stage"]["value"] not in ["Scanning","Canceled"])]
        print(json.dumps(sorted(queued_scans, key=lambda d: d["project"]["id"], reverse=True), indent=2))
        return queued_scans
        
    def cancel_scan(self, scan_id):
        return self.cx.update_queued_scan_status_by_scan_id(scan_id)
        
    def get_team_id_from_project_name(self, project):
        projects = self.cx.get_all_projects().json()
        for p in projects:
            if p['name'] == project:
                return p['teamId']
        return CxService.unknown_id      

    def get_project_id(self, team_id, project):
        projects = self.cx.get_all_projects().json()
        for p in projects:
            if p['teamId'] == team_id and p['name'] == project:
                return p['id']
        return CxService.unknown_id

    def start_scan(self, cx_config):
        plainProject = cx_config['project'].lstrip("#")
        if 'team' not in cx_config:
            team = self.get_team_id_from_project_name(plainProject)
            if team == CxService.unknown_id_str:
                raise Exception(" Couldn't find team for project " + plainProject)
        else:
            team = self.get_team_id(cx_config['team'])
            if team == CxService.unknown_id_str:
                raise Exception(" Couldn't find team " + cx_config['team'])        

        project = self.get_project_id(team, plainProject)

        # create project if doesn't exist
        if project == CxService.unknown_id:
            prj = self.cx.create_project_with_default_configuration(name=plainProject, owning_team=team,
                                                                    is_public=True).json()
            project = prj['id']
            
        remote_source_settings = self.cx.get_remote_source_settings_for_git_by_project_id(project)

        updated_url = cx_config['base_url'] + cx_config['project'] + cx_config.get('account_params', '')
        
        if remote_source_settings.get('url','') == '' or updated_url != remote_source_settings["url"]:
            self.cx.set_remote_source_setting_to_git(project, None, updated_url.strip(), cx_config['branch'])
            
        if cx_config.get("clearqueued", False) == True:
            scan_queue = cx.get_scan_queue_for_project(project)
            for queued_scan in scan_queue:
                cx.cancel_scan(queued_scan["id"])

        self.cx.create_new_scan(project, cx_config.get("incremental", True))

    @staticmethod
    def get_urls():
        try:
            with open("urls.json") as urls:
                return json.loads(urls.read())
        except Exception as e:
            raise Exception("Unable to get configuration: {} . ".format(e))
