import unittest
from abc import ABCMeta

from simpleopenstack.os_mock_managers import MockOpenstackKeypairManager, MockOpenstackInstanceManager, \
    MockOpenstackImageManager, MockOpenstack, MockOpenstackConnector, MockOpenstackFlavorManager
from simpleopenstack.tests._test_managers import OpenstackKeypairManagerTest, OpenstackInstanceManagerTest, \
    OpenstackImageManagerTest, OpenstackFlavorManagerTest


class _MockOpenstackItemManagerTest(unittest.TestCase, metaclass=ABCMeta):
    """
    TODO
    """
    def setUp(self):
        self._mock_openstack = MockOpenstack()
        self.openstack_connector = MockOpenstackConnector(self._mock_openstack)
        super().setUp()


class MockOpenstackKeypairManagerTest(
        _MockOpenstackItemManagerTest, OpenstackKeypairManagerTest[MockOpenstackKeypairManager]):
    """
    Tests for `MockOpenstackKeypairManager`.
    """
    def _create_manager(self) -> MockOpenstackKeypairManager:
        return MockOpenstackKeypairManager(self.openstack_connector)


class MockOpenstackInstanceManagerTest(
        _MockOpenstackItemManagerTest, OpenstackInstanceManagerTest[MockOpenstackInstanceManager]):
    """
    Tests for `MockOpenstackInstanceManager`.
    """
    def _create_manager(self) -> MockOpenstackInstanceManager:
        return MockOpenstackInstanceManager(self.openstack_connector)


class MockOpenstackImageManagerTest(
        _MockOpenstackItemManagerTest, OpenstackImageManagerTest[MockOpenstackImageManager]):
    """
    Tests for `MockOpenstackImageManager`.
    """
    def _create_manager(self) -> MockOpenstackImageManager:
        return MockOpenstackImageManager(self.openstack_connector)


class MockOpenstackFlavorManagerTest(
        _MockOpenstackItemManagerTest, OpenstackFlavorManagerTest[MockOpenstackFlavorManager]):
    """
    Tests for `MockOpenstackFlavorManager`.
    """
    def _create_manager(self) -> MockOpenstackFlavorManager:
        return MockOpenstackFlavorManager(self.openstack_connector)


# TODO: unittest is really stupid and will try to run the below as a test... Probably can add some ignore rules
del OpenstackKeypairManagerTest, OpenstackInstanceManagerTest, OpenstackImageManagerTest, OpenstackFlavorManagerTest,\
    _MockOpenstackItemManagerTest


if __name__ == "__main__":
    unittest.main()
