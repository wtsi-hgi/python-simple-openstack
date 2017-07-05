# import unittest
# from abc import ABCMeta
#
# from simpleopenstack.models import OpenstackConnector
# from simpleopenstack.os_managers import NovaOpenstackKeypairManager
# from simpleopenstack.os_mock_managers import MockOpenstackKeypairManager, MockOpenstackInstanceManager, \
#     MockOpenstackImageManager
# from simpleopenstack.tests._test_managers import OpenstackKeypairManagerTest, OpenstackInstanceManagerTest, \
#     OpenstackImageManagerTest
#
#
# class _OpenstackItemManagerTest(unittest.TestCase, metaclass=ABCMeta):
#     """
#     TODO
#     """
#     def setUp(self):
#         self.openstack_connector = OpenstackConnector()
#         super().setUp()
#
#
# class NovaOpenstackKeypairManagerTest(OpenstackKeypairManagerTest[NovaOpenstackKeypairManager]):
#     """
#     Tests for `NovaOpenstackKeypairManager`.
#     """
#     def _create_manager(self) -> NovaOpenstackKeypairManager:
#         return NovaOpenstackKeypairManager(self.openstack_connector)
#
#
# class NovaOpenstackInstanceManagerTest(OpenstackInstanceManagerTest[MockOpenstackInstanceManager]):
#     """
#     TODO
#     """
#     def _create_manager(self) -> MockOpenstackInstanceManager:
#         return MockOpenstackInstanceManager(self.openstack_connector)
#
#
# class GlanceOpenstackImageManagerTest(OpenstackImageManagerTest[MockOpenstackImageManager]):
#     """
#     TODO
#     """
#     def _create_manager(self) -> MockOpenstackImageManager:
#         return MockOpenstackImageManager(self.openstack_connector)
#
#
# # TODO: unittest is really stupid and will try to run the below as a test... Probably can add some ignore rules
# del OpenstackKeypairManagerTest, OpenstackInstanceManagerTest, OpenstackImageManagerTest, _OpenstackItemManagerTest
# 
#
# if __name__ == "__main__":
#     unittest.main()
