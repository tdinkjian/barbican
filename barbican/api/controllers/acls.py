#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import itertools

import pecan

from barbican import api
from barbican.api import controllers
from barbican.common import hrefs
from barbican.common import utils
from barbican.common import validators
from barbican import i18n as u
from barbican.model import models
from barbican.model import repositories as repo

LOG = utils.getLogger(__name__)


def _acls_not_found(acl_for=None):
    """Throw exception indicating no secret or container acls found."""
    pecan.abort(404, u._('Not Found. Sorry no ACL found for given {0}.').
                format(acl_for))


def _acl_not_found():
    """Throw exception indicating no secret or container acl found."""
    pecan.abort(404, u._('Not Found. Sorry no ACL found for given id.'))


def _acls_already_exist():
    """Throw exception indicating secret or container acls already exist."""
    pecan.abort(400, u._('Existing ACL cannot be updated with POST method.'))


def _acl_operation_update_not_allowed():
    """Throw exception indicating existing secret or container acl operation.

    Operation cannot be changed for an existing ACL. Allowed change is list of
    users and/or creator_only flag change.
    """
    pecan.abort(400, u._("Existing ACL's operation cannot be updated."))


class SecretACLController(object):
    """Handles a SecretACL entity retrieval and update requests."""

    def __init__(self, acl_id, secret_project_id, secret):
        self.acl_id = acl_id
        self.secret_project_id = secret_project_id
        self.secret = secret
        self.acl_repo = repo.get_secret_acl_repository()
        self.validator = validators.ACLValidator()

    @pecan.expose(generic=True)
    def index(self):
        pecan.abort(405)  # HTTP 405 Method Not Allowed as default

    @index.when(method='GET', template='json')
    @controllers.handle_exceptions(u._('SecretACL retrieval'))
    @controllers.enforce_rbac('secret_acl:get')
    def on_get(self, external_project_id):
        secret_acl = self.acl_repo.get(
            entity_id=self.acl_id,
            suppress_exception=True)

        if not secret_acl:
            _acl_not_found()

        dict_fields = secret_acl.to_dict_fields()

        return hrefs.convert_acl_to_hrefs(dict_fields)

    @index.when(method='PATCH', template='json')
    @controllers.handle_exceptions(u._('A SecretACL Update'))
    @controllers.enforce_rbac('secret_acl:patch')
    @controllers.enforce_content_types(['application/json'])
    def on_patch(self, external_project_id, **kwargs):
        """Handles existing secret ACL update for given acl id."""

        data = api.load_body(pecan.request, validator=self.validator)
        LOG.debug('Start SecretACLController on_patch...%s', data)

        secret_acl = self.acl_repo.get(
            entity_id=self.acl_id,
            suppress_exception=True)
        if not secret_acl:
            _acl_not_found()

        # Make sure request acl operation matches with acl stored in db
        operation = secret_acl.operation
        input_acl = data.get(operation)
        if not input_acl:
            _acl_operation_update_not_allowed()

        creator_only = input_acl.get('creator-only')
        user_ids = input_acl.get('users')
        if creator_only is not None:
            secret_acl.creator_only = creator_only

        self.acl_repo.create_or_replace_from(self.secret,
                                             secret_acl=secret_acl,
                                             user_ids=user_ids)
        acl_ref = hrefs.convert_acl_to_hrefs(secret_acl.to_dict_fields())

        return {'acl_ref': acl_ref['acl_ref']}

    @index.when(method='DELETE', template='json')
    @controllers.handle_exceptions(u._('SecretACL deletion'))
    @controllers.enforce_rbac('secret_acl:delete')
    def on_delete(self, external_project_id, **kwargs):
        """Deletes existing ACL by acl_id provided in URI."""

        secret_acl = self.acl_repo.get(
            entity_id=self.acl_id,
            suppress_exception=True)

        if not secret_acl:
            _acl_not_found()

        self.acl_repo.delete_entity_by_id(entity_id=self.acl_id,
                                          external_project_id=None)


class SecretACLsController(object):
    """Handles SecretACL requests by a given secret id."""

    def __init__(self, secret):
        self.secret = secret
        self.secret_project_id = (self.secret.project_assocs[0].
                                  projects.external_id)
        self.acl_repo = repo.get_secret_acl_repository()
        self.validator = validators.ACLValidator()

    @pecan.expose()
    def _lookup(self, acl_id, *remainder):
        return SecretACLController(acl_id, self.secret_project_id,
                                   self.secret), remainder

    @pecan.expose(generic=True)
    def index(self, **kwargs):
        pecan.abort(405)  # HTTP 405 Method Not Allowed as default

    @index.when(method='GET', template='json')
    @controllers.handle_exceptions(u._('SecretACL(s) retrieval'))
    @controllers.enforce_rbac('secret_acls:get')
    def on_get(self, external_project_id, **kw):
        LOG.debug('Start secret ACL on_get '
                  'for secret-ID %s:', self.secret.id)

        return self._return_acl_hrefs(self.secret.id)

    @index.when(method='POST', template='json')
    @controllers.handle_exceptions(u._('SecretACL(s) creation'))
    @controllers.enforce_rbac('secret_acls:post')
    @controllers.enforce_content_types(['application/json'])
    def on_post(self, external_project_id, **kwargs):
        """Handles secret acls creation request.

        Once a set of ACLs exists for a given secret, it can only be updated
        via PATCH method. In create, multiple operation ACL payload can be
        specified as mentioned in sample below.

        {
          "read":{
            "users":[
              "5ecb18f341894e94baca9e8c7b6a824a"
            ]
          },
          "write":{
            "users":[
              "20b63d71f90848cf827ee48074f213b7",
              "5ecb18f341894e94baca9e8c7b6a824a"
            ],
            "creator-only":false
          }
        }
        """

        count = self.acl_repo.get_count(self.secret.id)
        LOG.debug('Count of existing ACL on_post is [%s] '
                  ' for secret-ID %s:', count, self.secret.id)
        if count > 0:
            _acls_already_exist()

        data = api.load_body(pecan.request, validator=self.validator)
        LOG.debug('Start on_post...%s', data)

        for operation in itertools.ifilter(lambda x: data.get(x),
                                           validators.ACL_OPERATIONS):
            input_cr_only = data[operation].get('creator-only')
            creator_only = True if input_cr_only else False
            new_acl = models.SecretACL(self.secret.id, operation=operation,
                                       creator_only=creator_only)
            self.acl_repo.create_or_replace_from(
                self.secret, secret_acl=new_acl,
                user_ids=data[operation].get('users'))

        pecan.response.status = 201
        return self._return_acl_hrefs(self.secret.id)

    @index.when(method='PATCH', template='json')
    @controllers.handle_exceptions(u._('SecretACL(s) Update'))
    @controllers.enforce_rbac('secret_acls:patch')
    @controllers.enforce_content_types(['application/json'])
    def on_patch(self, external_project_id, **kwargs):
        """Handles update of existing secret acl requests.

        At least one secret ACL needs to exist for update to proceed.
        In update, multiple operation ACL payload can be specified as
        mentioned in sample below. A specific ACL can be updated by its
        own id via SecretACLController patch request.

        {
          "read":{
            "users":[
              "5ecb18f341894e94baca9e8c7b6a824a",
              "20b63d71f90848cf827ee48074f213b7",
              "c7753f8da8dc4fbea75730ab0b6e0ef4"
            ]
          },
          "write":{
            "users":[
              "5ecb18f341894e94baca9e8c7b6a824a"
            ],
            "creator-only":true
          }
        }
        """

        count = self.acl_repo.get_count(self.secret.id)
        LOG.debug('Count of existing ACL on_secret is [%s] '
                  ' for secret-ID %s:', count, self.secret.id)
        if count == 0:
            _acls_not_found("secret")

        data = api.load_body(pecan.request, validator=self.validator)
        LOG.debug('Start on_patch...%s', data)

        existing_acls_map = {acl.operation: acl for acl in
                             self.secret.secret_acls}
        for operation in itertools.ifilter(lambda x: data.get(x),
                                           validators.ACL_OPERATIONS):
            creator_only = data[operation].get('creator-only')
            user_ids = data[operation].get('users')
            s_acl = None
            if operation in existing_acls_map:  # update if matching acl exists
                s_acl = existing_acls_map[operation]
                if creator_only is not None:
                    s_acl.creator_only = creator_only
            else:
                s_acl = models.SecretACL(self.secret.id, operation=operation,
                                         creator_only=creator_only)
            self.acl_repo.create_or_replace_from(self.secret, secret_acl=s_acl,
                                                 user_ids=user_ids)

        return self._return_acl_hrefs(self.secret.id)

    @index.when(method='DELETE', template='json')
    @controllers.handle_exceptions(u._('SecretACL(s) deletion'))
    @controllers.enforce_rbac('secret_acls:delete')
    def on_delete(self, external_project_id, **kwargs):

        count = self.acl_repo.get_count(self.secret.id)
        if count == 0:
            _acls_not_found("secret")
        self.acl_repo.delete_acls_for_secret(self.secret)

    def _return_acl_hrefs(self, secret_id):
        result = self.acl_repo.get_by_secret_id(secret_id)

        if not result:
            _acls_not_found("secret")
        else:
            acl_recs = [hrefs.convert_acl_to_hrefs(acl.to_dict_fields())
                        for acl in result]
            return [{'acl_ref': acl['acl_ref']} for acl in acl_recs]