from abc import abstractmethod, ABCMeta
from copy import copy
from typing import Optional, Set, List, Generic
from uuid import uuid4

from novaclient.v2.flavors import Flavor

from simpleopenstack.managers import OpenstackKeypairManager, OpenstackInstanceManager, OpenstackImageManager, \
    OpenstackItemManager, Managed, OpenstackFlavorManager, OpenstackNetworkManager
from simpleopenstack.models import OpenstackConnector, OpenstackIdentifier, OpenstackKeypair, \
    OpenstackImage, OpenstackInstance, Model, OpenstackFlavor, OpenstackNetwork


class MockOpenstack(Model):
    """
    Mock OpenStack environment.
    """
    def __init__(self):
        self.images: List[OpenstackImage] = []
        self.instances: List[OpenstackInstance] = []
        self.keypairs: List[OpenstackKeypair] = []
        self.flavors: List[OpenstackFlavor] = []
        self.networks: List[OpenstackNetwork] = []


class MockOpenstackConnector(OpenstackConnector):
    """
    Connector for mock OpenStack environment.
    """
    def __init__(self, mock_openstack: MockOpenstack):
        self.mock_openstack = mock_openstack


class MockOpenstackItemManager(
        Generic[Managed], OpenstackItemManager[Managed, MockOpenstackConnector], metaclass=ABCMeta):
    """
    Manager of items in mock OpenStack environment.
    """
    @abstractmethod
    def _get_item_collection(self) -> List[Managed]:
        """
        Gets pointer to item collection that this manager deal with in the mock OpenStack environment.
        :return: pointer to the item collection (not a copy)
        """

    def get_all(self) -> Set[Managed]:
        return set(self._get_item_collection())

    def get_by_id(self, identifier: OpenstackIdentifier) -> Optional[Managed]:
        for item in self._get_item_collection():
            if item.identifier == identifier:
                return item
        return None

    def get_by_name(self, name: str) -> List[Managed]:
        matched_items = []
        for item in self._get_item_collection():
            if item.name == name:
                matched_items.append(item)
        return matched_items

    def create(self, model: Managed) -> Managed:
        created = copy(model)
        created.identifier = uuid4()
        self._get_item_collection().append(created)
        return created

    def _delete(self, identifier: OpenstackIdentifier):
        self._get_item_collection().remove(self.get_by_id(identifier))


class MockOpenstackKeypairManager(
        MockOpenstackItemManager[OpenstackKeypair], OpenstackKeypairManager[MockOpenstackConnector]):
    """
    Mock key-pair manager.
    """
    def create(self, model: OpenstackKeypair) -> OpenstackKeypair:
        if len(self.get_by_name(model.name)) >= 1:
            raise ValueError(f"Keypairs with duplicate names are not allowed in OpenStack: {model.name}")
        return super().create(model)

    def _get_item_collection(self) -> List[OpenstackKeypair]:
        return self.openstack_connector.mock_openstack.keypairs


class MockOpenstackInstanceManager(
        MockOpenstackItemManager[OpenstackInstance], OpenstackInstanceManager[MockOpenstackConnector]):
    """
    Mock instance manager.
    """
    # Not using override in MockOpenstackItemManager
    def create(self, model: OpenstackInstance) -> OpenstackInstance:
        return OpenstackInstanceManager.create(self, model)

    def _create(self, model: OpenstackInstance) -> OpenstackInstance:
        return MockOpenstackItemManager.create(self, model)

    def _get_item_collection(self) -> List[OpenstackInstance]:
        return self.openstack_connector.mock_openstack.instances


class MockOpenstackImageManager(
        MockOpenstackItemManager[OpenstackImage], OpenstackImageManager[MockOpenstackConnector]):
    """
    Mock image manager.
    """
    def _get_item_collection(self) -> List[OpenstackImage]:
        return self.openstack_connector.mock_openstack.images


class MockOpenstackFlavorManager(
        MockOpenstackItemManager[OpenstackFlavor], OpenstackFlavorManager[MockOpenstackConnector]):
    """
    Mock image flavour manager.
    """
    def _get_item_collection(self) -> List[OpenstackFlavor]:
        return self.openstack_connector.mock_openstack.flavors


class MockOpenstackNetworkManager(
        MockOpenstackItemManager[OpenstackNetwork], OpenstackNetworkManager[MockOpenstackConnector]):
    """
    Mock image flavour manager.
    """
    def _get_item_collection(self) -> List[OpenstackNetwork]:
        return self.openstack_connector.mock_openstack.networks
