from abc import ABCMeta, abstractmethod
from types import SimpleNamespace
from typing import Generic, Iterable, Set, Sequence, Optional, List, Type, Dict

from dateutil.parser import parse as parse_datetime
from glanceclient.client import Client as GlanceClient
from glanceclient.exc import HTTPNotFound
from keystoneclient.v2_0 import Client as KeystoneClient
from novaclient.base import ManagerWithFind
from novaclient.client import Client as NovaClient
from novaclient.exceptions import ClientException, NotFound
from novaclient.v2.flavors import Flavor
from novaclient.v2.images import Image
from novaclient.v2.keypairs import Keypair
from novaclient.v2.networks import Network
from novaclient.v2.servers import Server
from neutronclient.v2_0.client import Client as NeutronClient

from simpleopenstack.managers import Managed, RawModel, OpenstackKeypairManager, OpenstackInstanceManager, \
    OpenstackImageManager, OpenstackItemManager, Connector, OpenstackFlavorManager, OpenstackNetworkManager
from simpleopenstack.models import OpenstackKeypair, OpenstackIdentifier, OpenstackInstance, OpenstackImage, \
    OpenstackConnector, OpenstackItem, OpenstackFlavor, OpenstackNetwork


class RealOpenstackConnector(OpenstackConnector):
    """
    TODO
    """
    def __init__(self, auth_url: str, tenant: str, username: str, password: str):
        """
        Constructor.
        :param auth_url: the authentication URL of OpenStack.
        :param tenant: the tenant to connect to
        :param username: the username
        :param password: the password
        """
        self.auth_url = auth_url
        self.tenant = tenant
        self.username = username
        self.password = password


class _RawModelConvertingManager(
        Generic[Managed, RawModel], OpenstackItemManager[Managed, RealOpenstackConnector], metaclass=ABCMeta):
    """
    Manager for OpenStack items.
    """
    @abstractmethod
    def _get_by_id_raw(self, identifier: OpenstackIdentifier=None) -> Optional[RawModel]:
        """
        Gets raw model of the OpenStack item with the given identifier.
        :param identifier: the OpenStack item's identifier
        :return: raw model of the OpenStack item
        """

    @abstractmethod
    def _get_by_name_raw(self, name: str) -> Sequence[RawModel]:
        """
        Gets raw models of the OpenStack items with the given name.
        :param identifier: the OpenStack item's identifier
        :return: raw model of the OpenStack item
        """

    @abstractmethod
    def _get_all_raw(self) -> Iterable[RawModel]:
        """
        Gets raw models of all the OpenStack items of the type this manager manages.
        :return: all OpenStack items
        """

    def __init__(self, openstack_connector: Connector):
        super().__init__(openstack_connector)
        self._cached_client = None

    def get_by_id(self, identifier: OpenstackIdentifier) -> Optional[Managed]:
        raw_item = self._get_by_id_raw(identifier)
        if raw_item is None:
            return None
        item = self._convert_raw(raw_item)
        assert item.identifier == identifier
        return item

    def get_by_name(self, name: str) -> List[Managed]:
        items = [self._convert_raw(raw_model) for raw_model in self._get_by_name_raw(name)]
        assert len({item.name for item in items if item.name == name}) <= 1
        return items

    def get_all(self) -> Set[Managed]:
        # TODO: This could be list comprehended
        models: Set[Managed] = set()
        for item in self._get_all_raw():
            models.add(self._convert_raw(item))
        return models

    def _convert_raw(self, model: RawModel) -> Managed:
        """
        Converts the raw model to the domain model.

        Default function returns an object of the type the manager deals with, with its identifier and name set.
        :param model: the raw model
        :return: the domain model equivalent
        """
        return self.item_type(
            identifier=model.id,
            name=model.name
        )



class _NovaManager(Generic[Managed, RawModel], _RawModelConvertingManager[Managed, RawModel], metaclass=ABCMeta):
    """
    Manager that uses Nova client.
    """
    NOVA_VERSION = "2"

    @property
    @abstractmethod
    def _manager(self) -> ManagerWithFind:
        """
        TODO
        :return:
        """

    @property
    def _client(self) -> NovaClient:
        if self._cached_client is None:
            self._cached_client = NovaClient(
                _NovaManager.NOVA_VERSION, self.openstack_connector.username,
                self.openstack_connector.password, project_name=self.openstack_connector.tenant,
                auth_url=self.openstack_connector.auth_url)
        return self._cached_client

    def _get_by_id_raw(self, identifier: OpenstackIdentifier=None) -> Optional[RawModel]:
        try:
            return self._manager.get(identifier)
        except NotFound:
            return None

    def _get_by_name_raw(self, name: str) -> Sequence[Managed]:
        return self._manager.findall(name=name)

    def _get_all_raw(self) -> Iterable[RawModel]:
        return self._manager.list()

    def _delete(self, identifier: OpenstackIdentifier):
        self._manager.delete(identifier)


class NovaOpenstackKeypairManager(
        OpenstackKeypairManager[RealOpenstackConnector], _NovaManager[OpenstackKeypair, Keypair]):
    """
    Manager for OpenStack key-pairs.
    """
    @property
    def _manager(self) -> ManagerWithFind:
        return self._client.keypairs

    def _convert_raw(self, model: Keypair) -> OpenstackKeypair:
        converted = super()._convert_raw(model)
        converted.fingerprint = model.fingerprint
        converted.public_key = model.public_key
        return converted

    def create(self, model: OpenstackKeypair) -> OpenstackKeypair:
        return self._convert_raw(self._manager.create(name=model.name, public_key=model.public_key))


class NovaOpenstackInstanceManager(
        OpenstackInstanceManager[RealOpenstackConnector], _NovaManager[OpenstackInstance, Server]):
    """
    Manager for OpenStack instances.
    """
    @property
    def _manager(self) -> ManagerWithFind:
        return self._client.servers

    def _convert_raw(self, model: Server) -> OpenstackInstance:
        converted = super()._convert_raw(model)
        converted.created_at = parse_datetime(model.created)
        converted.updated_at = parse_datetime(model.updated)
        converted.image = model.image["id"]
        converted.key_name = model.key_name,
        converted.flavor = model.flavor["id"]
        converted.networks = [network for network in model.networks.keys()]
        converted.status = model.status
        return converted

    def _delete(self, identifier: OpenstackIdentifier):
        try:
            super().delete(identifier)
        except ClientException as e:
            if "nova.exception.InstanceInvalidState" not in e.message:
                raise e
            self._client.servers.reset_state(identifier)
            self._client.servers.force_delete(identifier)

    def _create(self, model: OpenstackInstance):
        from simpleopenstack.factories import OpenstackManagerFactory
        manager_factory = OpenstackManagerFactory(self.openstack_connector)

        image_manager = manager_factory.create_image_manager()
        image_id = (image_manager.get_by_id(model.image) or image_manager.get_by_name(model.image)[0]).identifier

        flavor_manager = manager_factory.create_flavor_manager()
        flavor_id = (flavor_manager.get_by_id(model.flavor) or flavor_manager.get_by_name(model.flavor)[0]).identifier

        network_manager = manager_factory.create_network_manager()
        network_ids = []
        for network in model.networks:
            network_ids.append(
                (network_manager.get_by_id(network) or network_manager.get_by_name(network)[0]).identifier)

        return self._convert_raw(self._client.servers.create(
            name=model.name, image=image_id, flavor=flavor_id, key_name=model.key_name,
            nics=[{"net-id": network for network in network_ids}]))


class NovaOpenstackFlavorManager(
        OpenstackFlavorManager[RealOpenstackConnector], _NovaManager[OpenstackFlavor, Flavor]):
    """
    Manager for OpenStack image flavours.
    """
    @property
    def _manager(self) -> ManagerWithFind:
        return self._client.flavors

    def create(self, model: OpenstackFlavor):
        raise NotImplementedError()


class NeutronOpenstackNetworkManager(
        OpenstackNetworkManager[RealOpenstackConnector], _RawModelConvertingManager[OpenstackNetwork, SimpleNamespace]):
    """
    Manager for OpenStack networks.
    """
    @staticmethod
    def _parse_result(result: Dict) -> List[SimpleNamespace]:
        return [SimpleNamespace(**network) for network in result["networks"]]

    @property
    def _client(self) -> NeutronClient:
        if self._cached_client is None:
            keystone = KeystoneClient(
                auth_url=self.openstack_connector.auth_url, username=self.openstack_connector.username,
                password=self.openstack_connector.password, tenant_name=self.openstack_connector.tenant)
            neutron_endpoint = keystone.service_catalog.url_for(service_type="network", endpoint_type="publicURL")
            self._cached_client = NeutronClient(endpoint_url=neutron_endpoint, token=keystone.auth_token)
        return self._cached_client

    def _get_by_id_raw(self, identifier: OpenstackIdentifier=None) -> Optional[SimpleNamespace]:
        parsed_result = NeutronOpenstackNetworkManager._parse_result(self._client.list_networks(id=identifier))
        assert len(parsed_result) <= 1
        return parsed_result[0] if len(parsed_result) == 1 else None

    def _get_by_name_raw(self, name: str) -> Sequence[SimpleNamespace]:
        return NeutronOpenstackNetworkManager._parse_result(self._client.list_networks(name=name))

    def _get_all_raw(self) -> Iterable[SimpleNamespace]:
        return NeutronOpenstackNetworkManager._parse_result(self._client.list_networks())

    def _delete(self, identifier: OpenstackIdentifier):
        self._client.delete_network(identifier)

    def create(self, model: OpenstackNetwork) -> OpenstackNetwork:
        return self._convert_raw(
            SimpleNamespace(**self._client.create_network({"network": {"name": model.name}})["network"]))


class GlanceOpenstackImageManager(
        OpenstackImageManager[RealOpenstackConnector], _RawModelConvertingManager[OpenstackImage, Image]):
    """
    Manager for OpenStack images.
    """
    GLANCE_VERSION = "2"

    @property
    def _client(self) -> GlanceClient:
        if self._cached_client is None:
            keystone = KeystoneClient(
                auth_url=self.openstack_connector.auth_url, username=self.openstack_connector.username,
                password=self.openstack_connector.password, tenant_name=self.openstack_connector.tenant)
            glance_endpoint = keystone.service_catalog.url_for(service_type="image", endpoint_type="publicURL")
            self._cached_client = GlanceClient(
                GlanceOpenstackImageManager.GLANCE_VERSION, glance_endpoint, token=keystone.auth_token)
        return self._cached_client

    def _get_by_id_raw(self, identifier: OpenstackIdentifier=None) -> Optional[Image]:
        try:
            return self._client.images.get(identifier)
        except HTTPNotFound:
            return None

    def _get_by_name_raw(self, name: str) -> Sequence[Image]:
        # XXX: No obvious way of doing this in the (terrible) documentation:
        # https://docs.openstack.org/developer/python-glanceclient/ref/v2/images.html
        return [raw_item for raw_item in self._get_all_raw() if raw_item.name == name]

    def _get_all_raw(self) -> Iterable[Image]:
        return self._client.images.list()

    def _convert_raw(self, model: Image) -> OpenstackImage:
        return OpenstackImage(
            identifier=model.id,
            name=model.name,
            created_at=parse_datetime(model.created_at),
            updated_at=parse_datetime(model.updated_at),
            protected=model.protected
        )

    def _delete(self, identifier: OpenstackIdentifier):
        self._client.images.delete(identifier)

    def create(self, model: OpenstackImage) -> OpenstackImage:
        return self._convert_raw(self._client.images.create(name=model.name))
