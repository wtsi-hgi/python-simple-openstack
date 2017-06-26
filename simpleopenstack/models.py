from abc import ABCMeta
from datetime import datetime
from typing import NewType, Set, Optional

from sshpubkeys import SSHKey

OpenstackIdentifier = NewType("OpenstackIdentifier", str)


# Stolen from hgicommon until this is resolved: https://github.com/wtsi-hgi/python-common/issues/11 -----
class Model(metaclass=ABCMeta):
    """
    Superclass that POPOs (Plain Old Python Objects) can implement.
    """
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        for property_name, value in vars(self).items():
            if other.__dict__[property_name] != self.__dict__[property_name]:
                return False
        return True

    def __str__(self) -> str:
        string_builder = []
        for property, value in vars(self).items():
            if isinstance(value, Set):
                value = str(sorted(value, key=id))
            string_builder.append("%s: %s" % (property, value))
        string_builder = sorted(string_builder)
        return "{ %s }" % ', '.join(string_builder)

    def __repr__(self) -> str:
        return "<%s object at %s: %s>" % (type(self), id(self), str(self))

    def __hash__(self):
        return hash(str(self))
# -----


class OpenstackConnector(Model):
    """
    Connector to an OpenStack environment.
    """


class Timestamped(Model, metaclass=ABCMeta):
    """
    Timestamps.
    """
    def __init__(self, created_at: datetime=None, updated_at: datetime=None):
        self.created_at = created_at
        self.updated_at = updated_at


class OpenstackItem(Model, metaclass=ABCMeta):
    """
    An item in OpenStack.
    """
    def __init__(self, identifier: Optional[OpenstackIdentifier]=None, name: str=None, **kwargs):
        super().__init__(**kwargs)
        self.identifier = identifier
        self.name = name


class OpenstackKeypair(OpenstackItem):
    """
    A key-pair in OpenStack.
    """
    @staticmethod
    def _generate_fingerprint(public_key: str) -> str:
        """
        Generates the fingerprint for the given public key.
        :param public_key: the public key
        :return: the fingerprint
        """
        return SSHKey(public_key).hash_md5().strip("MD5:")

    @property
    def public_key(self) -> Optional[str]:
        return self._public_key

    @property
    def fingerprint(self) -> Optional[str]:
        return self._fingerprint

    @public_key.setter
    def public_key(self, public_key: Optional[str]):
        self._public_key = public_key
        self._fingerprint = OpenstackKeypair._generate_fingerprint(public_key) if public_key is not None else None

    @fingerprint.setter
    def fingerprint(self, fingerprint: Optional[str]):
        if self._public_key is not None:
            expected = OpenstackKeypair._generate_fingerprint(self._public_key)
            if fingerprint != expected:
                raise ValueError(f"The given fingerprint \"{self.fingerprint}\" does not match that for the currently "
                                 f"set public key \"{self.public_key}\" (expecting \"{expected}\")")
        self._fingerprint = fingerprint

    def __init__(self, fingerprint: str=None, public_key: str=None, **kwargs):
        super().__init__(**kwargs)
        self._fingerprint = None
        self._public_key = None
        self.fingerprint = fingerprint
        self.public_key = public_key


class OpenstackInstance(OpenstackItem, Timestamped):
    """
    An instance on OpenStack.
    """
    def __init__(self, image: str=None, key_name: str=None, flavor: str=None, network: str=None, **kwargs):
        super().__init__(**kwargs)
        self.image = image
        self.key_name = key_name
        self.flavor = flavor
        self.network = network


class OpenstackImage(OpenstackItem, Timestamped):
    """
    An image on OpenStack.
    """
    def __init__(self, protected: bool=None, **kwargs):
        super().__init__(**kwargs)
        self.protected = protected


class OpenstackFlavor(OpenstackItem):
    """
    An OpenStack image flavour.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
