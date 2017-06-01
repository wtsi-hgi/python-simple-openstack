from simpleopenstack.managers import OpenstackItemManager
from simpleopenstack.models import OpenstackKeypair, OpenstackInstance, OpenstackImage, OpenstackConnector


class MockOpenstackConnector(OpenstackConnector):
    """
    TODO
    """


class MockOpenstackKeypairManager(OpenstackItemManager[OpenstackKeypair]):
    """
    Manager of key-pairs.
    """


class MockOpenstackInstanceManager(OpenstackItemManager[OpenstackInstance]):
    """
    Manager of instances.
    """


class MockOpenstackImageManager(OpenstackItemManager[OpenstackImage]):
    """
    Manager of images.
    """


