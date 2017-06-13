import unittest
from abc import ABCMeta, abstractmethod
from copy import copy
from threading import Lock
from typing import Generic, TypeVar

from simpleopenstack.managers import Managed, OpenstackItemManager, OpenstackKeypairManager, OpenstackInstanceManager, \
    OpenstackImageManager
from simpleopenstack.models import OpenstackKeypair, OpenstackInstance, OpenstackImage
from simpleopenstack.os_mock_managers import MockOpenstack, MockOpenstackConnector

Manager = TypeVar("Manager", bound=OpenstackItemManager)
KeypairManager = TypeVar("KeypairManager", bound=OpenstackKeypairManager)
InstanceManager = TypeVar("InstanceManager", bound=OpenstackInstanceManager)
ImageManager = TypeVar("ImageManager", bound=OpenstackImageManager)


class OpenstackItemManagerTest(Generic[Manager, Managed], unittest.TestCase, metaclass=ABCMeta):
    """
    TODO
    """
    @abstractmethod
    def _create_test_item(self) -> Managed:
        """
        TODO
        :return:
        """

    @abstractmethod
    def _create_manager(self) -> Manager:
        """
        TODO
        :return:
        """

    @property
    def item_count(self) -> int:
        """
        TODO
        :return:
        """
        with self._item_counter_lock:
            count = self._item_counter
            self._item_counter += 1
        return count

    def setUp(self):
        self._item_counter_lock = Lock()
        self._item_counter = 0
        self.manager = self._create_manager()
        self.item = self._create_test_item()
        assert self.item.identifier is None

    def test_item_type(self):
        self.assertEqual(type(self.item), self.manager.item_type)

    def test_create(self):
        assert len(self.manager.get_all()) == 0
        self.manager.create(self.item)
        all_items = self.manager.get_all()
        self.assertEqual(1, len(all_items))
        real_item = copy(list(all_items)[0])
        real_item.identifier = None
        self.assertEqual(real_item, self.item)

    def test_get_by_id_when_not_exists(self):
        self.assertIsNone(self.manager.get_by_id("other"))

    def test_get_by_id_when_exists(self):
        self.manager.create(self._create_test_item())
        self.item.identifier = self.manager.create(self.item).identifier
        self.assertEqual(self.item, self.manager.get_by_id(self.item.identifier))

    def test_get_by_name_when_not_exists(self):
        self.assertEqual([], self.manager.get_by_name("other"))

    def test_get_by_name(self):
        self.item.identifier = self.manager.create(self.item).identifier
        self.assertEqual(self.item, self.manager.get_by_name(self.item.name))

    def test_get_by_name_when_multiple_with_same_name(self):
        common_name = "same_name"
        items = {self._create_test_item() for _ in range(3)}
        for item in items:
            item.name = common_name
            item.identifier = self.manager.create(item).identifier
        self.assertEqual(items, self.manager.get_by_name(common_name))

    # TODO: Test other properties


class _MockOpenstackItemManagerTest(unittest.TestCase, metaclass=ABCMeta):
    """
    TODO
    """
    def setUp(self):
        self._mock_openstack = MockOpenstack()
        self.openstack_connector = MockOpenstackConnector(self._mock_openstack)
        super().setUp()


class OpenstackKeypairManagerTest(
        Generic[KeypairManager], _MockOpenstackItemManagerTest,
        OpenstackItemManagerTest[KeypairManager, OpenstackKeypair], metaclass=ABCMeta):
    """
    Tests for `OpenstackItemManagerTest`.
    """
    def _create_test_item(self) -> OpenstackKeypair:
        return OpenstackKeypair(name=f"example-keypair-{self.item_count}")


class OpenstackInstanceManagerTest(
        Generic[InstanceManager], _MockOpenstackItemManagerTest,
        OpenstackItemManagerTest[InstanceManager, OpenstackInstance], metaclass=ABCMeta):
    """
    Test for `OpenstackInstanceManagerTest`.
    """
    def _create_test_item(self) -> OpenstackInstance:
        return OpenstackInstance(name=f"example-instance-{self.item_count}")


class OpenstackImageManagerTest(
        Generic[ImageManager], _MockOpenstackItemManagerTest,
        OpenstackItemManagerTest[ImageManager, OpenstackImage], metaclass=ABCMeta):
    """
    Test for `OpenstackInstanceManagerTest`.
    """
    def _create_test_item(self) -> OpenstackImage:
        return OpenstackImage(name=f"example-image-{self.item_count}")


del _MockOpenstackItemManagerTest