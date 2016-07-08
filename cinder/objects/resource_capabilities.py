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

from cinder import db
from cinder.objects import base
from oslo_versionedobjects import fields


@base.CinderObjectRegistry.register
class ResourceCapability(base.CinderObject, base.CinderObjectDictCompat,
                         base.CinderComparableObject):
    # Version 1.0: Initial version
    VERSION = '1.0'

    fields = {
        'binary': fields.StringField(nullable=True)
    }

    @staticmethod
    def _from_db_object(context, rc, db_service):
        for name, field in rc.fields.items():
            value = db_service.get(name)
            if isinstance(field, fields.IntegerField):
                value = value or 0
            elif isinstance(field, fields.DateTimeField):
                value = value or None
            rc[name] = value

        rc._context = context
        rc.obj_reset_changes()
        return rc


@base.CinderObjectRegistry.register
class ResourceCapabilitiesList(base.ObjectListBase, base.CinderObject):

    VERSION = '1.0'
    fields = {
        'objects': fields.ListOfObjectsField('ResourceCapability'),
    }

    @classmethod
    def get_resource_capabilities_list(cls, context):
        """Returns list of resource capabilities for given cinder deployment"""
        rc = db.get_backup_service_info(context)
        return base.obj_make_list(context, cls(context), ResourceCapability,
                                  rc)
