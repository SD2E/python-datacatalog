import os
import json
import re
from attrdict import AttrDict

HERE = os.path.abspath(__file__)
PARENT = os.path.dirname(HERE)

class Project(AttrDict):
    pass

class Projects(object):

    @classmethod
    def sync(cls):
        """Fetch the current set of Data Catalog projects
        """
        # TODO - enable retrieval from a Tapis metadata record
        projects_obj = Projects()
        projects_file = os.path.join(PARENT, 'projects.json')
        projects = json.load(open(projects_file, 'r'))
        for p in projects:
            for project_id, project_body in p.items():
                # project_id = proj
                new_project_body = Project(project_body)
                setattr(projects_obj,
                        cls._propertize_project_id(project_id),
                        new_project_body)
        return projects_obj

    @classmethod
    def _propertize_project_id(cls, project_id):
        project_id = project_id.upper()
        project_id = project_id.replace('.', '_')
        project_id = project_id.replace('-', '_')
        if re.match('^[0-9]', project_id):
            project_id = '_' + project_id
        return project_id

    def names(self):
        """Return the property-named list of projects
        """
        names = list()
        for prop in dir(self):
            p = getattr(self, prop)
            if isinstance(p, Project):
                names.append(prop)
        names.sort()
        return names

    def project_names(self):
        """Return a sorted list of project identifiers
        """
        ids = list()
        for prop in dir(self):
            p = getattr(self, prop)
            if isinstance(p, Project):
                ids.append(p.tacc_name)
        ids.sort()
        return ids

    def validate_project_id(self, project_id, permissive=True):
        """Validate the supplied string against known project identifiers
        """
        if project_id in self.project_ids():
            return True
        else:
            if permissive is True:
                return False
            else:
                raise ValueError('{} not a known project id'.format(project_id))
