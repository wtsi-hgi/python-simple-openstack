from abc import ABCMeta
from typing import TypeVar, Generic, Optional

from simpleopenstack.managers import OpenstackImageManager, OpenstackKeypairManager, OpenstackInstanceManager, \
    OpenstackItemManager
from simpleopenstack.models import OpenstackCredentials
from simpleopenstack.os_managers import GlanceOpenstackImageManager, NovaOpenstackKeypairManager, \
    NovaOpenstackInstanceManager
from simpleopenstack.os_mock_managers import MockOpenstackKeypairManager, MockOpenstackInstanceManager, \
    MockOpenstackImageManager

_OpenstackItemManagerType = TypeVar("OpenstackItemFactoryProductType", bound=OpenstackItemManager)






# class Factory:
#     """
#     TODO
#     """
#     _factory_cache: Set[OpenstackItemManager] = set()
#
#     def __init__(self, openstack_credentials: Optional[OpenstackCredentials]=None):
#         self.openstack_credentials = openstack_credentials
#
#     def create(self, manager_type: Type[OpenstackItemManager]) -> Type[OpenstackItemManager]:
#         pass





class OpenstackItemManagerFactory(Generic[_OpenstackItemManagerType], metaclass=ABCMeta):
    """
    Factory for Openstack item managers.
    """
    def __init__(self, openstack_credentials: Optional[OpenstackCredentials]=None, mock_managers: bool=False):
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


class OpenstackKeypairManagerFactory(OpenstackItemManagerFactory[OpenstackKeypairManager]):
    """
    Factory for Openstack keypair managers.
    """
    def create(self) -> OpenstackKeypairManager:
        return NovaOpenstackKeypairManager(self.openstack_credentials) \
            if not self.mock_managers else MockOpenstackKeypairManager()


class OpenstackInstanceManagerFactory(OpenstackItemManagerFactory[OpenstackInstanceManager]):
    """
    Factory for Openstack instance managers.
    """
    def create(self) -> OpenstackInstanceManager:
        return NovaOpenstackInstanceManager(self.openstack_credentials) \
            if not self.mock_managers else MockOpenstackInstanceManager()


class OpenstackImageManagerFactory(OpenstackItemManagerFactory[OpenstackImageManager]):
    """
    Factory for Openstack image managers.
    """
    def create(self) -> OpenstackImageManager:
        return GlanceOpenstackImageManager(self.openstack_credentials) \
            if not self.mock_managers else MockOpenstackImageManager()
