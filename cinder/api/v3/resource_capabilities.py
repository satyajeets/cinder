# Copyright 2012 IBM Corp.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from cinder.api.openstack import wsgi
from cinder.objects import resource_capabilities as rc
import cinder.policy


def check_policy(context, action):
    """Checks policy.json to ensure this action is permitted by user"""
    target = {
        'project_id': context.project_id,
        'user_id': context.user_id,
    }
    _action = 'resource_capabilities:%s' % action
    cinder.policy.enforce(context, _action, target)


class ResourceCapabilitiesController(wsgi.Controller):
    """The Resource Capabilities Controller for Openstack API V3"""

    def __init__(self):
        super(ResourceCapabilitiesController, self).__init__()

    @wsgi.Controller.api_version('3.6')
    def index(self, req):
        """Return a list of resource capabilities.

        Currently returning only for backup
        """
        context = req.environ['cinder.context']
        check_policy(context, action='index')
        # resource capabilities list
        rcl = \
            rc.ResourceCapabilitiesList.get_resource_capabilities_list(context)

        # constructing response object
        resp = []
        for svc in rcl:
            ret_fields = {'name': svc.binary.replace('cinder', 'volume'),
                          'desc': 'Allows creating backup of volumes'}
            resp.append(ret_fields)
        return {'rc': resp}


def create_resource():
    return wsgi.Resource(ResourceCapabilitiesController())
