from abc import ABCMeta
from typing import TypeVar, Generic, Optional

from simpleopenstack._managers import GlanceOpenstackImageManager, NovaOpenstackKeypairManager, \
    NovaOpenstackInstanceManager
from simpleopenstack.managers import OpenstackImageManager, OpenstackKeypairManager, OpenstackInstanceManager
from simpleopenstack.models import OpenstackItem, OpenstackCredentials

_OpenstackItemManagerType = TypeVar("OpenstackItemFactoryProductType", bound=OpenstackItem)


class OpenstackItemFactory(Generic[_OpenstackItemManagerType], metaclass=ABCMeta):
    """
    Factory for Openstack item managers.
    """
    def __init__(self, *, openstack_credentials: Optional[OpenstackCredentials]=None, mock_managers: bool=False):
        """
        Constructor.
        :param openstack_credentials: credentials for OpenStack
        :param mock_managers: whether to create mock managers
        """
        self.openstack_credentials = openstack_credentials
        self.mock_managers = mock_managers

    def create(self) -> _OpenstackItemManagerType:
        """
        Creates a manger.
        :return: the created manager
        """


class OpenstackKeypairManagerFactory(OpenstackItemFactory[OpenstackKeypairManager]):
    """
    Factory for Openstack keypair managers.
    """
    def create(self) -> OpenstackKeypairManager:
        return NovaOpenstackKeypairManager(self.openstack_credentials)


class OpenstackInstanceManagerFactory(OpenstackItemFactory[OpenstackInstanceManager]):
    """
    Factory for Openstack instance managers.
    """
    def create(self) -> OpenstackInstanceManager:
        return NovaOpenstackInstanceManager(self.openstack_credentials)


class OpenstackImageManagerFactory(OpenstackItemFactory[OpenstackImageManager]):
    """
    Factory for Openstack image managers.
    """
    def create(self) -> OpenstackImageManager:
        return GlanceOpenstackImageManager(self.openstack_credentials)
