#    Copyright 2015 Intel Corp.
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


from cinder.api.openstack import api_version_request as api_version
from cinder.api.v3.resource_capabilities import ResourceCapabilitiesController
from cinder import context
from cinder import db
from cinder import test
from cinder.tests.unit.api import fakes
from cinder.tests.unit import fake_constants as fake
import datetime

fake_backup_capability_list = [
    {'binary': 'cinder-backup',
     'host': 'host1',
     'availability_zone': 'cinder',
     'id': 1,
     'disabled': True,
     'updated_at': datetime.datetime(2012, 10, 29, 13, 42, 2),
     'created_at': datetime.datetime(2012, 9, 18, 2, 46, 27),
     'disabled_reason': 'test1',
     'modified_at': ''}]


def fake_get_backup_service_info(context):
    return fake_backup_capability_list


def fake_backup_disabled(context):
    return []


class TestResourceCapabilities(test.TestCase):
    """" tests for the public API which checks if backup is enabled for a

    cinder deployment
    """

    def setUp(self):
        super(TestResourceCapabilities, self).setUp()
        self.ctxt = context.RequestContext(fake.USER_ID, fake.PROJECT_ID,
                                           auth_token=True)
        self.controller = ResourceCapabilitiesController()

    def test_return_true_if_enabled(self):
        self.stubs.Set(db, "get_backup_service_info",
                       fake_get_backup_service_info)
        expectedResponse = [{
            'name': 'volume-backup',
            'desc': 'Allows creating backup of volumes'
        }]

        req = fakes.HTTPRequest.blank('/v3/%s/resource-capabilities' % (
            fake.PROJECT_ID))
        # req.headers['OpenStack-API-Version'] = 'volume 3.6'
        req.api_version_request = api_version.APIVersionRequest('3.7')

        resp = self.controller.index(req)
        self.assertEqual(expectedResponse, resp['rc'])

    def test_returns_empty_list_when_backup_disabled(self):
        self.stubs.Set(db, "get_backup_service_info",
                       fake_backup_disabled)
        req = fakes.HTTPRequest.blank('/v3/%s/resource-capabilities' % (
            fake.PROJECT_ID))
        req.headers['OpenStack-API-Version'] = 'volume 3.7'
        req.api_version_request = api_version.APIVersionRequest('3.7')
        resp = self.controller.index(req)
        self.assertEqual([], resp['rc'])

    def test_api_should_work_for_all_users(self):
        self.stubs.Set(db, "get_backup_service_info",
                       fake_get_backup_service_info)
        expectedResponse = [{
            'name': 'volume-backup',
            'desc': 'Allows creating backup of volumes'
        }]

        # for admin user
        self.ctxt = context.RequestContext('admin', fake.PROJECT_ID,
                                           auth_token=True)
        req = fakes.HTTPRequest.blank('/v3/%s/resource-capabilities' % (
            fake.PROJECT_ID))
        req.headers['OpenStack-API-Version'] = 'volume 3.7'
        req.api_version_request = api_version.APIVersionRequest('3.7')
        resp = self.controller.index(req)
        self.assertEqual(expectedResponse, resp['rc'])

        # for normal user
        self.ctxt = context.RequestContext(fake.USER_ID, fake.PROJECT_ID,
                                           auth_token=True)
        req = fakes.HTTPRequest.blank('/v3/%s/resource-capabilities' % (
            fake.PROJECT_ID))
        req.headers['OpenStack-API-Version'] = 'volume 3.7'
        req.api_version_request = api_version.APIVersionRequest('3.7')
        resp = self.controller.index(req)
        self.assertEqual(expectedResponse, resp['rc'])
