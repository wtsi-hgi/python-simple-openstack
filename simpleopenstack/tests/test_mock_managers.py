import unittest

from simpleopenstack.os_mock_managers import MockOpenstackKeypairManager, MockOpenstackInstanceManager, \
    MockOpenstackImageManager
from simpleopenstack.tests._test_managers import OpenstackKeypairManagerTest, OpenstackInstanceManagerTest, \
    OpenstackImageManagerTest


class MockOpenstackKeypairManagerTest(OpenstackKeypairManagerTest[MockOpenstackKeypairManager]):
    """
    Tests for `MockOpenstackKeypairManager`.
    """
    def _create_manager(self) -> MockOpenstackKeypairManager:
        return MockOpenstackKeypairManager(self.openstack_connector)


class MockOpenstackInstanceManagerTest(OpenstackInstanceManagerTest[MockOpenstackInstanceManager]):
    """
    TODO
    """
    def _create_manager(self) -> MockOpenstackInstanceManager:
        return MockOpenstackInstanceManager(self.openstack_connector)


class MockOpenstackImageManagerTest(OpenstackImageManagerTest[MockOpenstackImageManager]):
    """
    TODO
    """
    def _create_manager(self) -> MockOpenstackImageManager:
        return MockOpenstackImageManager(self.openstack_connector)


# TODO: unittest is really stupid and will try to run the below as a test... Probably can add some ignore rules
del OpenstackKeypairManagerTest, OpenstackInstanceManagerTest, OpenstackImageManagerTest


if __name__ == "__main__":
    unittest.main()
