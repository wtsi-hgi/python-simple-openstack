import unittest
from typing import Sequence, List

from copy import copy
from uuid import uuid4

from simpleopenstack.models import OpenstackKeypair, Model, OpenstackImage, OpenstackInstance
from simpleopenstack.os_mock_managers import MockOpenstackKeypairManager, MockOpenstackConnector
from simpleopenstack.tests._managers import OpenstackKeypairManagerTest


# FIXME: This should not be defined here - showing as example!
class MockOpenstack(Model):
    def __init__(self):
        self.images: List[OpenstackImage] = []
        self.instances: List[OpenstackInstance] = []
        self.keypairs: List[OpenstackKeypair] = []


class MockOpenstackKeypairManagerTest(OpenstackKeypairManagerTest[MockOpenstackKeypairManager]):
    """
    Tests for `MockOpenstackItemManagerTest`.
    """
    def _create_manager(self) -> MockOpenstackKeypairManager:
        return MockOpenstackKeypairManager(self.openstack_connector)

    def _put_in_openstack(self, item: OpenstackKeypair) -> OpenstackKeypair:
        self._mock_openstack.keypairs.append(item)
        openstack_item = copy(item)
        openstack_item.identifier = uuid4()
        return openstack_item

    def _get_all_in_openstack(self) -> Sequence[OpenstackKeypair]:
        return self._mock_openstack.keypairs

    def setUp(self):
        self._mock_openstack = MockOpenstack()
        self.openstack_connector = MockOpenstackConnector()     # TODO: Pass in `self._mock_openstack`
        super().setUp()


# TODO: Test other mock managers


# FIXME: unittest is really stupid and will try to run the below as a test... Probably can add some ignore rules
del OpenstackKeypairManagerTest


if __name__ == "__main__":
    unittest.main()
