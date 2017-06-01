import unittest
from uuid import uuid4
from abc import ABCMeta, abstractmethod
from copy import copy
from typing import Generic, Sequence, TypeVar

from simpleopenstack.managers import Managed, OpenstackItemManager, OpenstackKeypairManager
from simpleopenstack.models import OpenstackIdentifier, OpenstackKeypair

Manager = TypeVar("Manager", bound=OpenstackItemManager)
KeypairManager = TypeVar("KeypairManager", bound=OpenstackKeypairManager)


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
    def _put_in_openstack(self, item: Managed) -> OpenstackIdentifier:
        """
        Creates the given item in the OpenStack environment that the manger under test can access.
        :param item: the item to create
        :return: the item's unique identifier in OpenStack
        """

    @abstractmethod
    def _get_all_in_openstack(self) -> Sequence[Managed]:
        """
        Gets all the items that the manger under test can access.
        :return: the items
        """

    @abstractmethod
    def _create_manager(self) -> Manager:
        """
        TODO
        :return:
        """

    def setUp(self):
        self.manager = self._create_manager()
        self.item = self._create_test_item()
        assert self.item.identifier is None

    def test_item_type(self):
        self.assertEqual(type(self.item), self.manager.item_type)

    def test_create(self):
        assert len(self._get_all_in_openstack()) == 0
        self.manager.create(self.item)
        all_items = self._get_all_in_openstack()
        self.assertEqual(1, len(all_items))
        real_item = copy(list(all_items)[0])
        real_item.identifier = None
        self.assertEqual(real_item, self.item)

    def get_by_id_when_not_exists(self):
        self.assertIsNone(self.manager.get_by_id("other"))

    def get_by_id_when_exists(self):
        self.item.identifier = self._put_in_openstack(self.item)
        self.assertEqual(self.item, self.manager.get_by_id(self.item.identifier))

    # TODO: Test other properties


class OpenstackKeypairManagerTest(
        Generic[KeypairManager], OpenstackItemManagerTest[KeypairManager, OpenstackKeypair], metaclass=ABCMeta):
    """
    Tests for `OpenstackItemManagerTest`.
    """
    def _create_test_item(self) -> OpenstackKeypair:
        return OpenstackKeypair(name=f"example-keypair-{uuid4()}")


# TODO: Create other manager test setups

