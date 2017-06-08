from typing import Type, Optional, Set, List

from simpleopenstack.managers import OpenstackKeypairManager, OpenstackInstanceManager, OpenstackImageManager
from simpleopenstack.models import OpenstackConnector, OpenstackItem, OpenstackIdentifier, OpenstackKeypair, \
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


class MockOpenstackKeypairManager(OpenstackKeypairManager[MockOpenstackConnector]):
    """
    Mock key-pair manager.
    """
    def item_type(self) -> Type[OpenstackItem]:
        return type(None)

    def get_by_id(self, identifier: OpenstackIdentifier) -> Optional[OpenstackKeypair]:
        return None

    def get_by_name(self, name: str) -> List[OpenstackKeypair]:
        return []

    def get_all(self) -> Set[OpenstackKeypair]:
        return set(self.openstack_connector.mock_openstack.keypairs)

    def create(self, model: OpenstackKeypair) -> OpenstackKeypair:
        self.openstack_connector.mock_openstack.keypairs.append(model)
        return model

    def _delete(self, item: OpenstackKeypair=None):
        pass


class MockOpenstackInstanceManager(OpenstackInstanceManager[MockOpenstackConnector]):
    """
    Mock instance manager.
    """


class MockOpenstackImageManager(OpenstackImageManager[MockOpenstackConnector]):
    """
    Mock image manager.
    """


