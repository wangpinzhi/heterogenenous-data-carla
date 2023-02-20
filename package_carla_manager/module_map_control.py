import carla


def function_set_map(parameter_client: carla.Client,
                     parameter_map: dict):
    """
    This function is used to set world map according to the configs which
    are obtained from the file.

    :param parameter_client: client for set map
    :param parameter_map: target map name
    :return:
    """

    # get current map name
    local_current_map = parameter_client.get_world().get_map().name.spilt('/')[-1]

    # load new map
    if parameter_map['name'] != local_current_map:
        parameter_client.load_world(parameter_map['name'])

