from simpleopenstack.managers import OpenstackKeypairManager, OpenstackInstanceManager, OpenstackImageManager
from simpleopenstack.models import OpenstackConnector


class MockOpenstackConnector(OpenstackConnector):
    """
    TODO
    """


class MockOpenstackKeypairManager(OpenstackKeypairManager[MockOpenstackConnector]):
    """
    Manager of key-pairs.
    """


class MockOpenstackInstanceManager(OpenstackInstanceManager[MockOpenstackConnector]):
    """
    Manager of instances.
    """


class MockOpenstackImageManager(OpenstackImageManager[MockOpenstackConnector]):
    """
    Manager of images.
    """


