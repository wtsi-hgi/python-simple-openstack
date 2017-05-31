from abc import ABCMeta, abstractmethod
from typing import Generic, Iterable, Set

from dateutil.parser import parse as parse_datetime
from glanceclient.client import Client as GlanceClient
from keystoneclient.v2_0 import Client as KeystoneClient
from novaclient.client import Client as NovaClient
from novaclient.exceptions import ClientException
from novaclient.v2.images import Image
from novaclient.v2.keypairs import Keypair
from novaclient.v2.servers import Server

from simpleopenstack.managers import Managed, RawModel, OpenstackKeypairManager, OpenstackInstanceManager, \
    OpenstackImageManager, Manager
from simpleopenstack.models import OpenstackKeypair, OpenstackIdentifier, OpenstackInstance, OpenstackImage, \
    OpenstackCredentials


class _RawModelConvertingManager(Generic[Managed, RawModel], Manager[Managed], metaclass=ABCMeta):
    """
    Manager for OpenStack items.
    """
    @abstractmethod
    def _get_by_id_raw(self, identifier: OpenstackIdentifier=None) -> RawModel:
        """
        Gets raw model of the OpenStack item with the given identifier.
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

    def __init__(self, openstack_credentials: OpenstackCredentials):
        """
        Constructor.
        :param openstack_credentials: OpenStack credentials
        """
        self.openstack_credentials = openstack_credentials

    def get_by_id(self, identifier: OpenstackIdentifier=None) -> Managed:
        """
        Gets the managed OpenStack item that has the given identifier
        :param identifier: the item's identifier
        :return: the matched item
        """
        item = self._get_by_id_raw(identifier)
        return self._convert_raw(item)

    def get_all(self) -> Set[Managed]:
        """
        Gets all of the OpenStack items of the managed type.
        :return: the OpenStack items
        """
        models: Set[Managed] = set()
        for item in self._get_all_raw():
            models.add(self._convert_raw(item))
        return models


class _NovaManager(Generic[Managed, RawModel], _RawModelConvertingManager[Managed, RawModel], metaclass=ABCMeta):
    """
    Manager that uses Nova client.
    """
    NOVA_VERSION = "2"

    def __init__(self, *args, **kwargs):
        """
        Constructor.
        """
        super().__init__(*args, **kwargs)
        self._client = NovaClient(_NovaManager.NOVA_VERSION, self.openstack_credentials.username,
                                  self.openstack_credentials.password, project_name=self.openstack_credentials.tenant,
                                  auth_url=self.openstack_credentials.auth_url)


class NovaOpenstackKeypairManager(OpenstackKeypairManager, _NovaManager[OpenstackKeypair, Keypair]):
    """
    Manager for OpenStack key-pairs.
    """
    def _get_by_id_raw(self, identifier: OpenstackIdentifier=None) -> RawModel:
        return self._client.keypairs.get(identifier)

    def _get_all_raw(self) -> Iterable[RawModel]:
        return self._client.keypairs.list()

    def _convert_raw(self, model: Keypair) -> OpenstackKeypair:
        return OpenstackKeypair(
            identifier=model.name,
            name=model.name,
            fingerprint=model.fingerprint
        )

    def _delete(self, identifier: OpenstackIdentifier=None):
        self._client.keypairs.delete(identifier)


class NovaOpenstackInstanceManager(OpenstackInstanceManager, _NovaManager[OpenstackInstance, Server]):
    """
    Manager for OpenStack instances.
    """
    @property
    def item_type(self):
        return OpenstackInstance

    def _get_by_id_raw(self, identifier: OpenstackIdentifier=None) -> RawModel:
        return self._client.servers.get(identifier)

    def _get_all_raw(self) -> Iterable[RawModel]:
        return self._client.servers.list()

    def _convert_raw(self, model: Server) -> OpenstackInstance:
        return OpenstackInstance(
            identifier=model.id,
            name=model.name,
            created_at=parse_datetime(model.created),
            updated_at=parse_datetime(model.updated),
            image=model.image["id"],
            key_name=model.key_name
        )

    def _delete(self, identifier: OpenstackIdentifier=None):
        try:
            self._client.servers.force_delete(identifier)
        except ClientException as e:
            if "nova.exception.InstanceInvalidState" not in e.message:
                raise e
            self._client.servers.reset_state(identifier)
            self._client.servers.force_delete(identifier)


class GlanceOpenstackImageManager(OpenstackImageManager, _RawModelConvertingManager[OpenstackImage, Image]):
    """
    Manager for OpenStack images.
    """
    GLANCE_VERSION = "2"

    @property
    def item_type(self):
        return OpenstackImage

    def __init__(self, *args, **kwargs):
        """
        Constructor.
        """
        super().__init__(*args, **kwargs)
        keystone = KeystoneClient(
            auth_url=self.openstack_credentials.auth_url, username=self.openstack_credentials.username,
            password=self.openstack_credentials.password, tenant_name=self.openstack_credentials.tenant)
        glance_endpoint = keystone.service_catalog.url_for(service_type="image", endpoint_type="publicURL")
        self._client = GlanceClient(GlanceOpenstackImageManager.GLANCE_VERSION, glance_endpoint, token=keystone.auth_token)

    def _get_by_id_raw(self, identifier: OpenstackIdentifier = None) -> RawModel:
        return self._client.images.get(identifier)

    def _get_all_raw(self) -> Iterable[RawModel]:
        return self._client.images.list()

    def _convert_raw(self, model: Image) -> OpenstackImage:
        return OpenstackImage(
            identifier=model.id,
            name=model.name,
            created_at=parse_datetime(model.created_at),
            updated_at=parse_datetime(model.updated_at),
            protected=model.protected
        )

    def _delete(self, identifier: OpenstackIdentifier=None):
        self._client.images.delete(identifier)
