from abc import ABCMeta
from datetime import datetime
from typing import NewType, Set, Optional

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
    def __init__(self, fingerprint: str=None, **kwargs):
        super().__init__(**kwargs)
        self.fingerprint = fingerprint


class OpenstackInstance(OpenstackItem, Timestamped):
    """
    An instance on OpenStack.
    """
    def __init__(self, image: str=None, key_name: str=None, flavor: str=None, **kwargs):
        super().__init__(**kwargs)
        self.image = image
        self.key_name = key_name
        self.flavor = flavor


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
