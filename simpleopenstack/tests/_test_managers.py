import unittest
from abc import ABCMeta, abstractmethod
from copy import copy
from threading import Lock
from types import SimpleNamespace
from typing import Generic, TypeVar

from simpleopenstack.common import raise_if_absent, get_identifier
from simpleopenstack.factories import OpenstackManagerFactory
from simpleopenstack.managers import Managed, OpenstackItemManager, OpenstackKeypairManager, OpenstackInstanceManager, \
    OpenstackImageManager, OpenstackFlavorManager, OpenstackNetworkManager
from simpleopenstack.models import OpenstackKeypair, OpenstackInstance, OpenstackImage, OpenstackFlavor, \
    OpenstackNetwork

Manager = TypeVar("Manager", bound=OpenstackItemManager)
KeypairManager = TypeVar("KeypairManager", bound=OpenstackKeypairManager)
InstanceManager = TypeVar("InstanceManager", bound=OpenstackInstanceManager)
ImageManager = TypeVar("ImageManager", bound=OpenstackImageManager)
FlavorManager = TypeVar("FlavorManager", bound=OpenstackFlavorManager)
NetworkManager = TypeVar("NetworkManager", bound=OpenstackNetworkManager)


class OpenstackItemManagerTest(Generic[Manager, Managed], unittest.TestCase, metaclass=ABCMeta):
    """
    Tests for `OpenstackItemManager`.
    """
    @abstractmethod
    def _create_test_item(self) -> Managed:
        """
        Creates an item that can be managed by the manager under test.
        :return: the OpenStack item
        """

    @abstractmethod
    def _create_manager(self) -> Manager:
        """
        Creates a manager of the type that is under test.
        :return: the created manager
        """

    @property
    def item_count(self) -> int:
        """
        Gets the number of test items that have been created and increments the counter by one.
        :return: the number of test itmes that have been created
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
        self.assertEqual([self.item], self.manager.get_by_name(self.item.name))

    def test_get_by_name_when_multiple_with_same_name(self):
        common_name = "same_name"
        items = {self._create_test_item() for _ in range(3)}
        for item in items:
            item.name = common_name
            item.identifier = self.manager.create(item).identifier
        self.assertCountEqual(items, self.manager.get_by_name(common_name))

    def test_delete_by_id(self):
        self.manager.create(self._create_test_item())
        self.item.identifier = self.manager.create(self.item).identifier
        assert self.item in self.manager.get_all()
        self.manager.delete(identifier=self.item.identifier)
        self.assertNotIn(self.item, self.manager.get_all())

    def test_delete_by_item(self):
        self.manager.create(self._create_test_item())
        self.item.identifier = self.manager.create(self.item).identifier
        assert self.item in self.manager.get_all()
        self.manager.delete(item=self.item)
        self.assertNotIn(self.item, self.manager.get_all())


class OpenstackKeypairManagerTest(
        Generic[KeypairManager], OpenstackItemManagerTest[KeypairManager, OpenstackKeypair], metaclass=ABCMeta):
    """
    Tests for `OpenstackKeypairManager`.
    """
    def _create_test_item(self) -> OpenstackKeypair:
        return OpenstackKeypair(
            name=f"example-keypair-{self.item_count}",
            public_key="ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAqmEmDTNBC6O8H"
                       "GCdu0MZ9zLCivDsYSttrrmlq87/YsEBpvwUTiF3UEQuFLaq5Gm+dtgxJewg/UwsZrDFxz"
                       "pQhCHB6VmqrbKN2hEIkk/HJvCnAmR1ehXv8n2BWw3Jlw7Z+VgWwXAH50f2HWYqTaE4qP4" 
                       "Dxc4RlElxgNmlDPGXw/dYBvChYBG/RvIiTz1L+pYzPD4JR54IMmTOwjcGIJl7nk1VjKvl" 
                       "3D8Wgp6qejv4MfZ7Htdc99SUKcKWAeHYsjPXosSk3GlwKiS/sZi51Yca394GE7T4hZu6H"
                       "TaXeZoD8+IZ7AijYn89H7EPjuu0iCAa/cjVzBsFHGszQYG+U5KfIw== user@host"
        )

    # Keypairs are different in that their names are unique
    def test_get_by_name_when_multiple_with_same_name(self):
        item = self._create_test_item()
        self.manager.create(item)
        self.assertRaises(ValueError, self.manager.create, item)


class OpenstackInstanceManagerTest(
        Generic[InstanceManager], OpenstackItemManagerTest[InstanceManager, OpenstackInstance], metaclass=ABCMeta):
    """
    Test for `OpenstackInstanceManager`.
    """
    _EXAMPLE_IMAGE = "Ubuntu Xenial"
    _EXAMPLE_FLAVOR = "m1.tiny"
    _EXAMPLE_KEY = "test-key"
    _EXAMPLE_NETWORK = "test-network"

    def _create_test_item(self) -> OpenstackInstance:
        prerequisites = {
            OpenstackImage: SimpleNamespace(name=OpenstackInstanceManagerTest._EXAMPLE_IMAGE),
            OpenstackFlavor: SimpleNamespace(name=OpenstackInstanceManagerTest._EXAMPLE_FLAVOR),
            OpenstackKeypair: SimpleNamespace(name=OpenstackInstanceManagerTest._EXAMPLE_KEY),
            OpenstackNetwork: SimpleNamespace(name=OpenstackInstanceManagerTest._EXAMPLE_NETWORK)
        }

        # Creates prerequisites
        manager_factory = OpenstackManagerFactory(self.manager.openstack_connector)
        for item_type, data in prerequisites.items():
            assert hasattr(data, "name")
            manager = manager_factory.create_for_managing(item_type)
            if len(manager.get_by_name(data.name)) == 0:
                manager.create(item_type(**vars(data)))
            assert raise_if_absent(data.name, manager)

        return OpenstackInstance(name=f"example-instance-{self.item_count}",
                                 image=OpenstackInstanceManagerTest._EXAMPLE_IMAGE,
                                 flavor=OpenstackInstanceManagerTest._EXAMPLE_FLAVOR,
                                 key_name=OpenstackInstanceManagerTest._EXAMPLE_KEY,
                                 networks=[OpenstackInstanceManagerTest._EXAMPLE_NETWORK])


class OpenstackImageManagerTest(
        Generic[ImageManager], OpenstackItemManagerTest[ImageManager, OpenstackImage], metaclass=ABCMeta):
    """
    Test for `OpenstackImageManager`.
    """
    def _create_test_item(self) -> OpenstackImage:
        return OpenstackImage(name=f"example-image-{self.item_count}")


class OpenstackFlavorManagerTest(
        Generic[FlavorManager], OpenstackItemManagerTest[FlavorManager, OpenstackFlavor], metaclass=ABCMeta):
    """
    Test for `OpenstackFlavorManager`.
    """
    def _create_test_item(self) -> OpenstackFlavor:
        return OpenstackFlavor(name=f"example-flavor-{self.item_count}")


class OpenstackNetworkManagerTest(
        Generic[NetworkManager], OpenstackItemManagerTest[NetworkManager, OpenstackNetwork], metaclass=ABCMeta):
    """
    Test for `OpenstackNetworkManager`.
    """
    def _create_test_item(self) -> OpenstackNetwork:
        return OpenstackNetwork(name=f"example-network-{self.item_count}")
