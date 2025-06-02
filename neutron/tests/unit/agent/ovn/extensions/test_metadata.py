# Copyright 2026 Red Hat, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may
#    obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from unittest import mock

from neutron.agent.ovn.extensions import metadata
from neutron.common.ovn import constants as ovn_const
from neutron.tests import base


class TestMetadataExtension(base.BaseTestCase):

    def _get_extension(self):
        ext = metadata.MetadataExtension.__new__(
            metadata.MetadataExtension)
        ext.agent_api = mock.MagicMock()
        ext._is_started = False
        return ext

    def _assert_ovn_bridge_written(self, ext):
        ext.agent_api.sb_idl.db_set.assert_called_once_with(
            'Chassis_Private', ext.agent_api.chassis,
            ('external_ids',
             {ovn_const.OVN_AGENT_OVN_BRIDGE: ext.agent_api.ovn_bridge}))
        (ext.agent_api.sb_idl.db_set.return_value.execute
         .assert_called_once_with(check_error=True))

    @mock.patch.object(metadata.metadata_server,
                       'UnixDomainMetadataProxy')
    @mock.patch.object(metadata.threading, 'Thread')
    def test_start_sets_ovn_bridge_in_chassis_private(
            self, mock_thread, mock_proxy):
        ext = self._get_extension()
        ext.sync = mock.Mock()
        ext._load_config = mock.Mock()
        ext.register_metadata_agent = mock.Mock()

        ext.start()

        self._assert_ovn_bridge_written(ext)
        mock_thread.assert_called_once_with(target=ext._proxy.wait)

    def test_resync_sets_ovn_bridge_in_chassis_private(self):
        ext = self._get_extension()
        ext.sync = mock.Mock()

        ext.resync()

        ext.agent_api.load_config.assert_called_once_with()
        self._assert_ovn_bridge_written(ext)
        ext.sync.assert_called_once_with()
