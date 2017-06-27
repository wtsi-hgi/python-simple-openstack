from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic, Dict, Type

from simpleopenstack.managers import OpenstackImageManager, OpenstackKeypairManager, OpenstackInstanceManager, \
    OpenstackItemManager, OpenstackFlavorManager, OpenstackNetworkManager
from simpleopenstack.models import OpenstackConnector
from simpleopenstack.os_managers import GlanceOpenstackImageManager, NovaOpenstackKeypairManager, \
    NovaOpenstackInstanceManager, RealOpenstackConnector, NovaOpenstackFlavorManager, NovaOpenstackNetworkManager
from simpleopenstack.os_mock_managers import MockOpenstackKeypairManager, MockOpenstackInstanceManager, \
    MockOpenstackImageManager, MockOpenstackConnector, MockOpenstackFlavorManager, MockOpenstackNetworkManager

_OpenstackItemManagerType = TypeVar("OpenstackItemFactoryProductType", bound=OpenstackItemManager)


class _OpenstackFactory(metaclass=ABCMeta):
    """
    Base class for Openstack factories.
    """
    def __init__(self, openstack_connector: OpenstackConnector):
        """
        Constructor.
        :param openstack_connector:
        """
        self.openstack_connector = openstack_connector


class OpenstackItemManagerFactory(Generic[_OpenstackItemManagerType], _OpenstackFactory, metaclass=ABCMeta):
    """
    Factory for Openstack item managers.
    """
    @staticmethod
    @abstractmethod
    def _connector_manager_map() -> Dict[Type[OpenstackConnector], _OpenstackItemManagerType]:
        """
        Gets the mapping between the Openstack connector type and the manager for that type that will work with the
        connector.
        :return: manager for type and connector
        """

    def create(self) -> _OpenstackItemManagerType:
        """
        Creates a manger.
        :return: the created manager
        """
        if type(self.openstack_connector) not in self._connector_manager_map():
            raise ValueError(f"Unsupported connector: {type(self.openstack_connector)}")
        return self._connector_manager_map()[type(self.openstack_connector)](self.openstack_connector)


class OpenstackKeypairManagerFactory(OpenstackItemManagerFactory[OpenstackKeypairManager]):
    """
    Factory for Openstack key-pair managers.
    """
    @staticmethod
    def _connector_manager_map():
        return {
            RealOpenstackConnector: NovaOpenstackKeypairManager,
            MockOpenstackConnector: MockOpenstackKeypairManager
        }


class OpenstackInstanceManagerFactory(OpenstackItemManagerFactory[OpenstackInstanceManager]):
    """
    Factory for Openstack instance managers.
    """
    @staticmethod
    def _connector_manager_map():
        return {
            RealOpenstackConnector: NovaOpenstackInstanceManager,
            MockOpenstackConnector: MockOpenstackInstanceManager
        }


class OpenstackImageManagerFactory(OpenstackItemManagerFactory[OpenstackImageManager]):
    """
    Factory for Openstack image managers.
    """
    @staticmethod
    def _connector_manager_map():
        return {
            RealOpenstackConnector: GlanceOpenstackImageManager,
            MockOpenstackConnector: MockOpenstackImageManager
        }


class OpenstackFlavorManagerFactory(OpenstackItemManagerFactory[OpenstackFlavorManager]):
    """
    Factory for Openstack flavour managers.
    """
    @staticmethod
    def _connector_manager_map():
        return {
            RealOpenstackConnector: NovaOpenstackFlavorManager,
            MockOpenstackConnector: MockOpenstackFlavorManager
        }


class OpenstackNetworkManagerFactory(OpenstackItemManagerFactory[OpenstackNetworkManager]):
    """
    Factory for Openstack network managers.
    """
    @staticmethod
    def _connector_manager_map():
        return {
            RealOpenstackConnector: NovaOpenstackNetworkManager,
            MockOpenstackConnector: MockOpenstackNetworkManager
        }


class OpenstackManagerFactory(_OpenstackFactory):
    """
    Factory for creating Openstack managers for different types of Openstack items.
    """
    def create_keypair_manager(self) -> OpenstackKeypairManager:
        return OpenstackKeypairManagerFactory(self.openstack_connector).create()

    def create_instance_manager(self) -> OpenstackInstanceManager:
        return OpenstackInstanceManagerFactory(self.openstack_connector).create()

    def create_image_manager(self) -> OpenstackImageManager:
        return OpenstackImageManagerFactory(self.openstack_connector).create()

    def create_flavor_manager(self) -> OpenstackFlavorManager:
        return OpenstackFlavorManagerFactory(self.openstack_connector).create()

    def create_network_manager(self) -> OpenstackNetworkManager:
        return OpenstackNetworkManagerFactory(self.openstack_connector).create()

