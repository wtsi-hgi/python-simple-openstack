from simpleopenstack.managers import OpenstackItemManager
from simpleopenstack.models import ItemNotFoundException


def raise_if_absent(identifier: str, item_manager: OpenstackItemManager):
    """
    TODO
    :param identifier:
    :param item_manager:
    :return:
    """
    if identifier is None:
        raise ValueError(f"None is not a valid identifier for items of type \"{item_manager.item_type.__name__}\"")
    try:
        get_identifier(identifier, item_manager)
    except ValueError as e:
        raise ItemNotFoundException(str(e))
    return True


def get_identifier(name_or_identifier: str, item_manager: OpenstackItemManager) -> str:
    """
    TODO
    :param name_or_identifier:
    :param item_manager:
    :return:
    """
    item = item_manager.get_by_id(name_or_identifier)
    if item is not None:
        return name_or_identifier

    items = item_manager.get_by_name(name_or_identifier)
    if len(items) == 1:
        return items[0].identifier
    elif len(items) > 1:
        raise ValueError(
            f"There is more than one item of type \"{item_manager.item_type.__name__}\" with the name "
            f"\"{name_or_identifier}\" - please refer to the required item by ID to resolve the ambiguity")
    elif len(items) == 0:
        raise ValueError(
            f"No item of type \"{item_manager.item_type.__name__}\" with ID or name \"{name_or_identifier}\" found")
