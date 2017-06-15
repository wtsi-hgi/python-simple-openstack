from abc import ABCMeta, abstractmethod
from typing import Generic, Iterable, Set, Sequence, Optional, List, Type

from dateutil.parser import parse as parse_datetime
from glanceclient.client import Client as GlanceClient
from glanceclient.exc import HTTPNotFound
from keystoneclient.v2_0 import Client as KeystoneClient
from novaclient.client import Client as NovaClient
from novaclient.exceptions import ClientException
from novaclient.v2.images import Image
from novaclient.v2.keypairs import Keypair
from novaclient.v2.servers import Server

from simpleopenstack.managers import Managed, RawModel, OpenstackKeypairManager, OpenstackInstanceManager, \
    OpenstackImageManager, OpenstackItemManager, Connector
from simpleopenstack.models import OpenstackKeypair, OpenstackIdentifier, OpenstackInstance, OpenstackImage, \
    OpenstackConnector, OpenstackItem


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

    @abstractmethod
    def _convert_raw(self, model: RawModel) -> Managed:
        """
        Converts the raw model to the domain model.
        :param model: the raw model
        :return: the domain model equivalent
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
        assert len({item.name for item in items if item.name == name}) == 1
        return items

    def get_all(self) -> Set[Managed]:
        # TODO: This could be list comprehended
        models: Set[Managed] = set()
        for item in self._get_all_raw():
            models.add(self._convert_raw(item))
        return models


class _NovaManager(Generic[Managed, RawModel], _RawModelConvertingManager[Managed, RawModel], metaclass=ABCMeta):
    """
    Manager that uses Nova client.
    """
    NOVA_VERSION = "2"

    @property
    def _client(self) -> NovaClient:
        if self._cached_client is None:
            self._cached_client = NovaClient(
                _NovaManager.NOVA_VERSION, self.openstack_connector.username,
                self.openstack_connector.password, project_name=self.openstack_connector.tenant,
                auth_url=self.openstack_connector.auth_url)
        return self._cached_client


class NovaOpenstackKeypairManager(
        OpenstackKeypairManager[RealOpenstackConnector], _NovaManager[OpenstackKeypair, Keypair]):
    """
    Manager for OpenStack key-pairs.
    """
    def _get_by_id_raw(self, identifier: OpenstackIdentifier=None) -> Optional[Keypair]:
        try:
            return self._client.keypairs.get(identifier)
        except HTTPNotFound:
            return None

    def _get_by_name_raw(self, name: str) -> Sequence[OpenstackKeypair]:
        return self._client.keypairs.find(name=name)

    def _get_all_raw(self) -> Iterable[Keypair]:
        return self._client.keypairs.list()

    def _convert_raw(self, model: Keypair) -> OpenstackKeypair:
        return OpenstackKeypair(
            identifier=model.name,
            name=model.name,
            fingerprint=model.fingerprint
        )

    def _delete(self, identifier: OpenstackIdentifier):
        self._client.keypairs.delete(identifier)

    def create(self, model: OpenstackKeypair) -> OpenstackKeypair:
        raise NotImplementedError()


class NovaOpenstackInstanceManager(
        OpenstackInstanceManager[RealOpenstackConnector], _NovaManager[OpenstackInstance, Server]):
    """
    Manager for OpenStack instances.
    """
    @property
    def item_type(self) -> Type[OpenstackItem]:
        return OpenstackInstance

    def _get_by_id_raw(self, identifier: OpenstackIdentifier=None) -> Optional[Server]:
        try:
            self._client.servers.get(identifier)
        except HTTPNotFound:
            return None

    def _get_by_name_raw(self, name: str) -> Sequence[OpenstackInstance]:
        return self._client.servers.find(name=name)

    def _get_all_raw(self) -> Iterable[Server]:
        return self._client.servers.list()

    def _convert_raw(self, model: Server) -> OpenstackInstance:
        return OpenstackInstance(
            identifier=model.id,
            name=model.name,
            created_at=parse_datetime(model.created),
            updated_at=parse_datetime(model.updated),
            image=model.image["id"],
            key_name=model.key_name,
            flavor=model.flavor["id"]
        )

    def _delete(self, identifier: OpenstackIdentifier):
        try:
            self._client.servers.force_delete(identifier)
        except ClientException as e:
            if "nova.exception.InstanceInvalidState" not in e.message:
                raise e
            self._client.servers.reset_state(identifier)
            self._client.servers.force_delete(identifier)

    def create(self, model: OpenstackInstance):
        raise NotImplementedError()
        # if model.identifier is not None:
        #     raise ValueError(f"Cannot create an instance with a particular identifier (\"{model.identifier}\" given)")
        #
        # image_manager = GlanceOpenstackImageManager(self.openstack_credentials)
        # image = image_manager.get_by_id(model.image)
        # if image is None:
        #     images = image_manager.get_by_name(model.image)
        #     if len(images) > 1:
        #         raise ValueError(f"There is more than one image with the name \"{model.name}\" - please refer to the "
        #                          f"required image by ID to resolve the ambiguity")
        #     elif len(images) == 0:
        #         raise ValueError(f"No image with ID or name \"{model.image}\" found")
        #     image = images[0]
        #
        # # TODO: This hints at the requirement of a flavor manager!
        # try:
        #     flavor = self._client.flavors.get(model.flavor)
        # except NotFound:
        #     try:
        #         flavor = self._client.flavors.find(name=model.flavor)
        #     except NotFound:
        #         raise ValueError(f"Could not find flavor with ID or name \"{model.flavor}\"")
        # self._client.servers.create(name=model.name, image=image.identifier, flavor=flavor.id, network="123")


class GlanceOpenstackImageManager(
        OpenstackImageManager[RealOpenstackConnector], _RawModelConvertingManager[OpenstackImage, Image]):
    """
    Manager for OpenStack images.
    """
    GLANCE_VERSION = "2"

    @property
    def item_type(self) -> Type[OpenstackItem]:
        return OpenstackImage

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
        raise NotImplementedError()
