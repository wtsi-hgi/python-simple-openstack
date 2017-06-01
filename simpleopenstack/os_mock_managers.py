from simpleopenstack.managers import Manager
from simpleopenstack.models import OpenstackKeypair, OpenstackInstance, OpenstackImage


class MockOpenstackKeypairManager(Manager[OpenstackKeypair]):
    """
    Manager of key-pairs.
    """


class MockOpenstackInstanceManager(Manager[OpenstackInstance]):
    """
    Manager of instances.
    """


class MockOpenstackImageManager(Manager[OpenstackImage]):
    """
    Manager of images.
    """


