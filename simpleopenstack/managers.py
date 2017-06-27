from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic, Set, Type, Optional, List

from simpleopenstack.models import OpenstackItem, OpenstackKeypair, OpenstackInstance, OpenstackImage, \
    OpenstackIdentifier, OpenstackConnector, OpenstackFlavor, OpenstackNetwork

Managed = TypeVar("Managed", bound=OpenstackItem)
RawModel = TypeVar("RawModel")
Connector = TypeVar("Connector", bound=OpenstackConnector)


class OpenstackItemManager(Generic[Managed, Connector], metaclass=ABCMeta):
    """
    Manager for OpenStack items.
    """
    @property
    @abstractmethod
    def item_type(self) -> Type[Managed]:
        """
        Gets the type of items that the manager manages (i.e. the concrete `Managed` type).
        :return: the item type
        """

    @abstractmethod
    def get_by_id(self, identifier: OpenstackIdentifier) -> Optional[Managed]:
        """
        Gets the managed OpenStack item that has the given identifier
        :param identifier: the item's identifier
        :return: the matched item
        """

    @abstractmethod
    def get_by_name(self, name: str) -> List[Managed]:
        """
        Gets the managed OpenStack items with the given name
        :param name: the items' name
        :return: the matched items
        """

    @abstractmethod
    def get_all(self) -> Set[Managed]:
        """
        Gets all of the OpenStack items of the managed type.
        :return: the OpenStack items
        """

    @abstractmethod
    def create(self, model: Managed) -> Managed:
        """
        Creates a manged item in OpenStack, based on the given model.
        :param model: the model to base the item created in OpenStack off. Should not have an identifier
        :return: model of the created item in OpenStack. It will have an identifier
        """

    @abstractmethod
    def _delete(self, identifier: OpenstackIdentifier):
        """
        Deletes an OpenStack item with the given identifier.
        :param identifier: the identifier of the item to delete
        """

    def __init__(self, openstack_connector: Connector):
        """
        Constructor.
        :param openstack_connector: connector to Openstack environment
        """
        self.openstack_connector = openstack_connector

    def delete(self, *, item: Managed=None, identifier: OpenstackIdentifier=None):
        """
        Deletes the given OpenStack item.
        :param item: the item to delete
        :param identifier: the identifier of the item to delete
        """
        if item is not None and identifier is not None and item.identifier != identifier:
            raise ValueError(f"An item has been given with the identifier {item.identifier}, along with a different "
                             f"identifier {identifier} - provide either the item or the identifier")
        if item is None and identifier is None:
            raise ValueError("An item or identifier must be provided")
        if identifier is None and item is not None:
            identifier = item.identifier
        self._delete(identifier)


class OpenstackKeypairManager(
       Generic[Connector], OpenstackItemManager[OpenstackKeypair, Connector], metaclass=ABCMeta):
    """
    Manager of key-pairs.
    """
    @property
    def item_type(self) -> Type[OpenstackKeypair]:
        return OpenstackKeypair


class OpenstackInstanceManager(
        Generic[Connector], OpenstackItemManager[OpenstackInstance, Connector], metaclass=ABCMeta):
    """
    Manager of instances.
    """
    @abstractmethod
    def _create(self, model: OpenstackInstance) -> OpenstackInstance:
        """
        TODO
        :param model:
        :return:
        """

    @property
    def item_type(self) -> Type[OpenstackInstance]:
        return OpenstackInstance

    def create(self, model: OpenstackInstance):
        from simpleopenstack.common import ensure_exists
        from simpleopenstack.factories import OpenstackManagerFactory

        manager_factory = OpenstackManagerFactory(self.openstack_connector)
        ensure_exists(model.image, manager_factory.create_image_manager())
        ensure_exists(model.flavor, manager_factory.create_flavor_manager())
        ensure_exists(model.key_name, manager_factory.create_keypair_manager())

        return self._create(model)


class OpenstackImageManager(
        Generic[Connector], OpenstackItemManager[OpenstackImage, Connector], metaclass=ABCMeta):
    """
    Manager of images.
    """
    @property
    def item_type(self) -> Type[OpenstackImage]:
        return OpenstackImage


class OpenstackFlavorManager(
        Generic[Connector], OpenstackItemManager[OpenstackFlavor, Connector], metaclass=ABCMeta):
    """
    Manager of image flavors.
    """
    @property
    def item_type(self) -> Type[OpenstackFlavor]:
        return OpenstackFlavor


class OpenstackNetworkManager(
        Generic[Connector], OpenstackItemManager[OpenstackNetwork, Connector], metaclass=ABCMeta):
    """
    Manager of networks.
    """
    @property
    def item_type(self) -> Type[OpenstackNetwork]:
        return OpenstackNetwork
