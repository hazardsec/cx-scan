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
        if 'team' not in cx_config:
            team = self.get_team_id_from_project_name(cx_config['project'])
            if team == CxService.unknown_id_str:
                raise Exception(" Couldn't find team for project " + cx_config['project'])
        else:
            team = self.get_team_id(cx_config['team'])
            if team == CxService.unknown_id_str:
                raise Exception(" Couldn't find team " + cx_config['team'])        

        #print(team)
        project = self.get_project_id(team, cx_config['project'])
        
        # create project if doesn't exist
        if project == CxService.unknown_id:
            prj = self.cx.create_project_with_default_configuration(name=cx_config['project'], owning_team=team,
                                                                    is_public=True).json()
            project = prj['id']
            
        remote_source_settings = self.cx.get_remote_source_settings_for_git_by_project_id(project)
        if 'url' not in remote_source_settings:
            self.cx.set_remote_source_setting_to_git(project, None, cx_config['base_url'] + cx_config['project'], cx_config['default_branch'])

        self.cx.create_new_scan(project)

    @staticmethod
    def get_urls():
        try:
            with open("urls.json") as urls:
                return json.loads(urls.read())
        except Exception as e:
            raise Exception("Unable to get configuration: {} . ".format(e))


