from simpleopenstack.managers import OpenstackKeypairManager, OpenstackInstanceManager, OpenstackImageManager
from simpleopenstack.models import OpenstackConnector


class MockOpenstackConnector(OpenstackConnector):
    """
    TODO
    """


class MockOpenstackKeypairManager(OpenstackKeypairManager[MockOpenstackConnector]):
    """
    Mock key-pair manager.
    """


class MockOpenstackInstanceManager(OpenstackInstanceManager[MockOpenstackConnector]):
    """
    Mock instance manager.
    """


class MockOpenstackImageManager(OpenstackImageManager[MockOpenstackConnector]):
    """
    Mock image manager.
    """


