from simpleopenstack.managers import OpenstackItemManager


def ensure_exists(identifier: str, item_manager: OpenstackItemManager):
    """
    TODO
    :param identifier:
    :param item_manager:
    :return:
    """
    item = item_manager.get_by_id(identifier)
    if item is None:
        items = item_manager.get_by_name(identifier)
        if len(items) > 1:
            raise ValueError(
                f"There is more than one item of type \"{item_manager.item_type.__name__}\" with the name "
                f"\"{identifier}\" - please refer to the required itemby ID to resolve the ambiguity")
        elif len(items) == 0:
            raise ValueError(
                f"No item of type \"{item_manager.item_type.__name__}\" with ID or name \"{identifier}\" found")
