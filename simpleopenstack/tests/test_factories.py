import unittest
from abc import ABCMeta, abstractmethod
from typing import Type, Generic, TypeVar

from simpleopenstack.factories import OpenstackKeypairManagerFactory, OpenstackItemManagerFactory, \
    OpenstackInstanceManagerFactory, OpenstackImageManagerFactory, OpenstackManagerFactory
from simpleopenstack.managers import OpenstackItemManager, OpenstackKeypairManager, OpenstackInstanceManager, \
    OpenstackImageManager
from simpleopenstack.os_mock_managers import MockOpenstackConnector, MockOpenstack
from simpleopenstack.tests._test_managers import Manager

ItemManagerFactory = TypeVar("ItemManagerFactory", bound=OpenstackItemManagerFactory)


class _TestOpenstackItemManagerFactory(Generic[ItemManagerFactory, Manager], metaclass=ABCMeta):
    """
    Tests for `OpenstackItemManagerFactory`.
    """
    @property
    @abstractmethod
    def factory_type(self) -> Type[ItemManagerFactory]:
        """
        The type of factory under test.
        :return: the type of the factory under test
        """

    @property
    @abstractmethod
    def manager_type(self) -> Type[Manager]:
        """
        The manager type that should be produced by the factory that is being tested.
        :return: the manager type
        """

    def setUp(self):
        self.mock_connector = MockOpenstackConnector(MockOpenstack())

    def test_create_mock_manager(self):
        factory = self.factory_type(self.mock_connector)
        manager = factory.create()
        self.assertIsInstance(manager, self.manager_type)
        self.assertEqual(self.mock_connector, manager.openstack_connector)


class TestOpenstackKeypairManagerFactory(
        _TestOpenstackItemManagerFactory[OpenstackKeypairManagerFactory, OpenstackKeypairManager]):
    """
    Tests for `OpenstackKeypairManagerFactory`.
    """
    @property
    def factory_type(self) -> Type[OpenstackItemManagerFactory]:
        return OpenstackKeypairManagerFactory

    @property
    def manager_type(self) -> Type[OpenstackItemManager]:
        return OpenstackKeypairManager


class TestOpenstackInstanceManagerFactory(
        _TestOpenstackItemManagerFactory[OpenstackInstanceManagerFactory, OpenstackInstanceManager]):
    """
    Tests for `TestOpenstackInstanceManagerFactory`.
    """
    @property
    def factory_type(self) -> Type[OpenstackInstanceManagerFactory]:
        return OpenstackInstanceManagerFactory

    @property
    def manager_type(self) -> Type[OpenstackInstanceManager]:
        return OpenstackInstanceManager


class TestOpenstackImageManagerFactory(
        _TestOpenstackItemManagerFactory[OpenstackImageManagerFactory, OpenstackImageManager]):
    """
    Tests for `OpenstackImageManagerFactory`.
    """
    @property
    def factory_type(self) -> Type[OpenstackImageManagerFactory]:
        return OpenstackImageManagerFactory

    @property
    def manager_type(self) -> Type[OpenstackImageManager]:
        return OpenstackImageManager


class TestOpenstackManagerFactory(unittest.TestCase):
    """
    Tests for `OpenstackManagerFactory`.
    """
    def setUp(self):
        self.mock_connector = MockOpenstackConnector(MockOpenstack())
        self.factory = OpenstackManagerFactory(self.mock_connector)

    def test_create_keypair_manager(self):
        manager = self.factory.create_keypair_manager()
        self.assertIsInstance(manager, OpenstackKeypairManager)
        self.assertEqual(self.mock_connector, manager.openstack_connector)

    def test_create_instance_manager(self):
        manager = self.factory.create_instance_manager()
        self.assertIsInstance(manager, OpenstackInstanceManager)
        self.assertEqual(self.mock_connector, manager.openstack_connector)

    def test_create_image_manager(self):
        manager = self.factory.create_image_manager()
        self.assertIsInstance(manager, OpenstackImageManager)
        self.assertEqual(self.mock_connector, manager.openstack_connector)


del _TestOpenstackItemManagerFactory

if __name__ == "__main__":
    unittest.main()