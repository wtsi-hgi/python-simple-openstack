import unittest
import os
from abc import ABCMeta

from simpleopenstack.managers import OpenstackInstanceManager, OpenstackImageManager, OpenstackFlavorManager, \
    OpenstackNetworkManager
from simpleopenstack.models import OpenstackConnector
from simpleopenstack.os_managers import NovaOpenstackKeypairManager, RealOpenstackConnector, \
    NovaOpenstackInstanceManager, GlanceOpenstackImageManager, NeutronOpenstackNetworkManager, \
    NovaOpenstackFlavorManager
from simpleopenstack.tests._test_managers import OpenstackKeypairManagerTest, OpenstackInstanceManagerTest, \
    OpenstackImageManagerTest, OpenstackNetworkManagerTest, OpenstackFlavorManagerTest

class _OpenstackItemManagerTest(unittest.TestCase, metaclass=ABCMeta):
    """
    TODO
    """
    def setUp(self):
        self.openstack_connector = RealOpenstackConnector(os.getenv('OS_AUTH_URL'),
                                                          os.getenv('OS_TENANT'),
                                                          os.getenv('OS_USERNAME'),
                                                          os.getenv('OS_PASSWORD'))
        super().setUp()


class NovaOpenstackKeypairManagerTest(
    _OpenstackItemManagerTest, OpenstackKeypairManagerTest[NovaOpenstackKeypairManager]):
    """
    Tests for `NovaOpenstackKeypairManager`.
    """
    def _create_manager(self) -> NovaOpenstackKeypairManager:
        return NovaOpenstackKeypairManager(self.openstack_connector)


class NovaOpenstackInstanceManagerTest(
    _OpenstackItemManagerTest, OpenstackInstanceManagerTest[OpenstackInstanceManager]):
    """
    TODO
    """
    def _create_manager(self) -> OpenstackInstanceManager:
        return NovaOpenstackInstanceManager(self.openstack_connector)


class GlanceOpenstackImageManagerTest(
    _OpenstackItemManagerTest, OpenstackImageManagerTest[OpenstackImageManager]):
    """
    TODO
    """
    def _create_manager(self) -> OpenstackImageManager:
        return GlanceOpenstackImageManager(self.openstack_connector)

class NovaOpenstackFlavorManagerTest(
    _OpenstackItemManagerTest, OpenstackFlavorManagerTest[OpenstackFlavorManager]):
    """
    Tests for `MockOpenstackFlavorManager`.
    """

    def _create_manager(self) -> OpenstackFlavorManager:
        return NovaOpenstackFlavorManager(self.openstack_connector)

class NeutronOpenstackNetworkManagerTest(
    _OpenstackItemManagerTest, OpenstackNetworkManagerTest[OpenstackNetworkManager]):
    """
    Tests for `MockOpenstackNetworkManager`.
    """

    def _create_manager(self) -> OpenstackNetworkManager:
        return NeutronOpenstackNetworkManager(self.openstack_connector)


# TODO: unittest is really stupid and will try to run the below as a test... Probably can add some ignore rules
del OpenstackKeypairManagerTest, OpenstackInstanceManagerTest, OpenstackImageManagerTest, _OpenstackItemManagerTest, \
    OpenstackNetworkManagerTest, OpenstackFlavorManagerTest


if __name__ == "__main__":
    unittest.main()
