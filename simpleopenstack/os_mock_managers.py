from copy import copy
from typing import Optional, Set, List, Generic
from uuid import uuid4

from simpleopenstack.managers import OpenstackKeypairManager, OpenstackInstanceManager, OpenstackImageManager, \
    OpenstackItemManager, Managed
from simpleopenstack.models import OpenstackConnector, OpenstackIdentifier, OpenstackKeypair, \
    OpenstackImage, OpenstackInstance, Model


class MockOpenstack(Model):
    """
    TODO
    """
    def __init__(self):
        self.images: List[OpenstackImage] = []
        self.instances: List[OpenstackInstance] = []
        self.keypairs: List[OpenstackKeypair] = []


class MockOpenstackConnector(OpenstackConnector):
    """
    TODO
    """
    def __init__(self, mock_openstack: MockOpenstack):
        self.mock_openstack = mock_openstack


class MockOpenstackItemManager(Generic[Managed], OpenstackItemManager[Managed, MockOpenstackConnector]):
    """
    TODO
    """
    def get_by_id(self, identifier: OpenstackIdentifier) -> Optional[Managed]:
        for instance in self.get_all():
            if instance.identifier == identifier:
                return instance
        return None

    def get_by_name(self, name: str) -> List[Managed]:
        return []

    def create(self, model: Managed) -> Managed:
        created = copy(model)
        created.identifier = uuid4()
        self.openstack_connector.mock_openstack.instances.append(created)
        return created

    def _delete(self, item: Managed=None):
        pass


class MockOpenstackKeypairManager(
        MockOpenstackItemManager[OpenstackKeypair], OpenstackKeypairManager[MockOpenstackConnector]):
    """
    Mock key-pair manager.
    """
    def get_all(self) -> Set[OpenstackKeypair]:
        return set(self.openstack_connector.mock_openstack.keypairs)


class MockOpenstackInstanceManager(
        MockOpenstackItemManager[OpenstackInstance], OpenstackInstanceManager[MockOpenstackConnector]):
    """
    Mock instance manager.
    """
    def get_all(self) -> Set[OpenstackInstance]:
        return set(self.openstack_connector.mock_openstack.instances)


class MockOpenstackImageManager(
        MockOpenstackItemManager[OpenstackImage], OpenstackImageManager[MockOpenstackConnector]):
    """
    Mock image manager.
    """
    def get_all(self) -> Set[OpenstackImage]:
        return set(self.openstack_connector.mock_openstack.images)


