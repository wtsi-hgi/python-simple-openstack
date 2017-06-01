from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic, Set, Type, Union, Sequence, Optional, List

from simpleopenstack.models import OpenstackItem, OpenstackKeypair, OpenstackInstance, \
    OpenstackImage, OpenstackIdentifier, OpenstackConnector

Managed = TypeVar("Managed", bound=OpenstackItem)
RawModel = TypeVar("RawModel")
ConnectorType = TypeVar("ConnectorType", bound=OpenstackConnector)


class OpenstackItemManager(Generic[Managed, ConnectorType], metaclass=ABCMeta):
    """
    Manager for OpenStack items.
    """
    @property
    @abstractmethod
    def item_type(self) -> Type[OpenstackItem]:
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
    def _delete(self, item: Managed=None):
        """
        Deletes an OpenStack item with the given identifier.
        :param item: the OpenStack item to delete
        """

    def __init__(self, openstack_connector: ConnectorType):
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
    Generic[ConnectorType], OpenstackItemManager[OpenstackKeypair, ConnectorType], metaclass=ABCMeta):
    """
    Manager of key-pairs.
    """
    @property
    def item_type(self):
        return OpenstackKeypair


class OpenstackInstanceManager(
    Generic[ConnectorType], OpenstackItemManager[OpenstackInstance, ConnectorType], metaclass=ABCMeta):
    """
    Manager of instances.
    """
    @property
    def item_type(self):
        return OpenstackInstance


class OpenstackImageManager(
    Generic[ConnectorType], OpenstackItemManager[OpenstackImage, ConnectorType], metaclass=ABCMeta):
    """
    Manager of images.
    """
    @property
    def item_type(self):
        return OpenstackImage


