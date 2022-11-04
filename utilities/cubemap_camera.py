
import carla
from utilities.callback_func import cubemap_data_callback

'''
get cubemap_camera_rgb actors from dict
'''
def get_cubemap_camera_rgb(world, target_vehicle, sensor_queue, settings:list, save_data_path):

    blueprint_library = world.get_blueprint_library()
    cam_bp = blueprint_library.find('sensor.camera.rgb')
    actors = []
    for cur_setting in settings:
        cam_bp.set_attribute("image_size_x", "{}".format(cur_setting["image_width"]))
        cam_bp.set_attribute("image_size_y", "{}".format(cur_setting["image_height"]))
        cam_bp.set_attribute("sensor_tick", '{}'.format(cur_setting["sensor_tick"]))
        cam_bp.set_attribute("fov", '{}'.format(cur_setting["fov"]))
        
        items = [('front',0,0,0),('right',0,90,0),('back',0,180,0),('left',0,-90,0),('up',90,0,0),('down',-90,0,0)]
        for view, rotation_pitch, rotation_yaw, rotation_roll in items:
            
            actor=world.spawn_actor(cam_bp, 
            carla.Transform(carla.Location(x=cur_setting['location_x'],y=cur_setting['location_y'],z=cur_setting['location_z']),
                            carla.Rotation(pitch=rotation_pitch,yaw=rotation_yaw,roll=rotation_roll)
            ), attach_to=target_vehicle)

            actor.listen(lambda data, s_name=cur_setting["name"], s_view=view: cubemap_data_callback(data, sensor_queue, s_name, s_view, save_data_path))
            actors.append(actor)
    
    return actors

'''
get cubemap_camera_depth actors from dict
'''
def get_cubemap_camera_depth(world, target_vehicle, sensor_queue, settings:list, save_data_path):

    blueprint_library = world.get_blueprint_library()
    cam_bp = blueprint_library.find('sensor.camera.depth')
    actors = []
    for cur_setting in settings:
        cam_bp.set_attribute("image_size_x", "{}".format(cur_setting["image_width"]))
        cam_bp.set_attribute("image_size_y", "{}".format(cur_setting["image_height"]))
        cam_bp.set_attribute("sensor_tick", '{}'.format(cur_setting["sensor_tick"]))
        cam_bp.set_attribute("fov", '{}'.format(cur_setting["fov"]))
        
        items = [('front',0,0,0),('right',0,90,0),('back',0,180,0),('left',0,-90,0),('up',90,0,0),('down',-90,0,0)]
        for view, rotation_pitch, rotation_yaw, rotation_roll in items:
            actor=world.spawn_actor(cam_bp, 
            carla.Transform(carla.Location(x=cur_setting['location_x'],y=cur_setting['location_y'],z=cur_setting['location_z']),
                            carla.Rotation(pitch=rotation_pitch,yaw=rotation_yaw,roll=rotation_roll)
            ), attach_to=target_vehicle)

            actor.listen(lambda data, s_name=cur_setting["name"], s_view=view: cubemap_data_callback(data, sensor_queue, s_name, s_view, save_data_path))
            actors.append(actor)
    
    return actors