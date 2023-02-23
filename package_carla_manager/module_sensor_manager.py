import carla
from queue import Queue, Empty
from threading import Thread
import numpy as np
import os
from func_timeout import func_set_timeout
import func_timeout

# import global vehicle manager to find vehicle
from module_vehicle_manager import instance_var_vehicle_manager as global_var_vehicle_manager

__all__ = ['instance_var_sensor_manager']

GLOBAL_CONSTANT_SENSOR_TYPE_CUBE = 0
GLOBAL_CONSTANT_SENSOR_TYPE_NORMAL = 1


class ClassCubeSensorUnit(Thread):
    def __init__(self,
                 parameter_name_id: str,
                 parameter_blueprint: carla.ActorBlueprint,
                 parameter_root_actor: carla.Actor):
        super(ClassCubeSensorUnit, self).__init__()
        self.__local_val_frame_counter = 0
        self.__local_val_save_path = ''
        self.__local_val_store = []  # Only for store sensor.listen, do not use it.
        self.__local_val_type = 'cube'
        self.__local_val_root_actor = parameter_root_actor
        self.__local_val_blueprint = parameter_blueprint
        self.__local_val_name_id = parameter_name_id
        self.__local_val_save_queue = Queue()
        self.__local_val_task_lock = Queue(maxsize=1)

        # parameter_root_actor is 'front' actor, we need it to obtain other 5 actors.
        self.__local_sensor_group = self._function_get_sensor_group()

    def function_get_save_queue(self):
        return self.__local_val_save_queue

    def function_get_counter(self):
        return self.__local_val_frame_counter

    def run(self) -> None:
        self.function_save_data()

    def function_sync(self):
        self.__local_val_task_lock.put(1)
        self.__local_val_task_lock.join()

    def function_save_data(self):
        while True:
            local_val_save_data = {}
            try:
                for i in range(6):
                    local_val_name, local_val_data = self.__local_val_save_queue.get(block=True, timeout=5.0)
                    # print(self.name, self.__local_val_name_id, local_val_name, self.__local_val_frame_counter)
                    if local_val_name == 'front':
                        local_val_save_data['ex_matrix'] = np.array(local_val_data.transform.get_matrix())
                        local_val_save_data['timestamp'] = local_val_data.timestamp

                    # convert raw data to numpy array
                    local_val_data_array = np.frombuffer(local_val_data.raw_data, dtype=np.dtype("uint8"))
                    local_val_data_array = np.reshape(local_val_data_array,
                                                      (local_val_data.height, local_val_data.width, 4))
                    local_val_data_array = local_val_data_array[:, :, :3]
                    local_val_save_data[local_val_name] = local_val_data_array

                np.savez(
                    os.path.join(self.__local_val_save_path,
                                 f'{self.__local_val_name_id}_{self.__local_val_frame_counter}.npz'),
                    front_data=local_val_save_data['front'],
                    left_data=local_val_save_data['left'],
                    right_data=local_val_save_data['right'],
                    back_data=local_val_save_data['back'],
                    up_data=local_val_save_data['up'],
                    down_data=local_val_save_data['down'],
                    ex_matrix=local_val_save_data['ex_matrix'],
                    timestamp=local_val_save_data['timestamp']
                )
                self.__local_val_frame_counter += 1
                self.__local_val_task_lock.get()
                self.__local_val_task_lock.task_done()
            except Empty:
                break

            # save data to npz

    def _function_get_sensor_group(self) -> dict:
        local_val_cube_info = [('left', carla.Rotation(0., -90., 0)), ('right', carla.Rotation(0., 90., 0.)),
                               ('back', carla.Rotation(0., 180., 0.)), ('up', carla.Rotation(90., 0., 0.)),
                               ('down', carla.Rotation(-90., 0., 0.))]

        local_val_group = {'front': self.__local_val_root_actor.id}
        local_val_world = self.__local_val_root_actor.get_world()

        for local_val_name, local_val_rotation in local_val_cube_info:
            local_val_transform = carla.Transform(carla.Location(0., 0., 0.), local_val_rotation)
            # other 5 sensor('left', 'right', 'up', 'down', 'back) attach to 'front'
            local_val_group[local_val_name] = local_val_world.spawn_actor(self.__local_val_blueprint,
                                                                          local_val_transform,
                                                                          self.__local_val_root_actor).id
        return local_val_group

    def function_listen(self,
                        parameter_save_path: str):
        """
        This function starts the sensor listen method, so sensor will data.
        This function must be used when sync mode is on.

        :return:
        """
        # get save path
        self.__local_val_save_path = os.path.join(parameter_save_path, self.__local_val_name_id)
        os.makedirs(self.__local_val_save_path, exist_ok=True)

        local_val_world = self.__local_val_root_actor.get_world()
        for local_val_name in ['front', 'left', 'right', 'up', 'down', 'back']:
            local_val_sensor = local_val_world.get_actor(self.__local_sensor_group[local_val_name])
            local_val_sensor.listen(
                lambda data, name=local_val_name, cube_sensor=self: function_cube_sensor_callback(data,
                                                                                                  name,
                                                                                                  cube_sensor)
            )
            self.__local_val_store.append(local_val_sensor)

    def function_stop(self):
        """
        This function stops the sensor listen method, so sensor will not get any data.

        :return:
        """
        local_val_world = self.__local_val_root_actor.get_world()
        local_val_world.get_actor(self.__local_sensor_group['front']).stop()
        local_val_world.get_actor(self.__local_sensor_group['left']).stop()
        local_val_world.get_actor(self.__local_sensor_group['right']).stop()
        local_val_world.get_actor(self.__local_sensor_group['up']).stop()
        local_val_world.get_actor(self.__local_sensor_group['down']).stop()
        local_val_world.get_actor(self.__local_sensor_group['back']).stop()

    def function_destroy(self):
        self.join(timeout=8.0)
        local_val_world = self.__local_val_root_actor.get_world()
        # First destroy other 5 actor
        local_val_world.get_actor(self.__local_sensor_group['left']).destroy()
        local_val_world.get_actor(self.__local_sensor_group['right']).destroy()
        local_val_world.get_actor(self.__local_sensor_group['up']).destroy()
        local_val_world.get_actor(self.__local_sensor_group['down']).destroy()
        local_val_world.get_actor(self.__local_sensor_group['back']).destroy()
        # destroy root actor
        self.__local_val_root_actor.destroy()


class ClassSensorManager(object):

    def __init__(self) -> None:
        self.__local_val_sensors = []
        self.__local_save_root_path = './'

    @staticmethod
    def _function_get_spawn(parameter_sensor_config: dict,
                            parameter_blueprint_library: carla.BlueprintLibrary):
        """
        This function gets the blueprint and spawn point from the config json (obtained from 'sensor_config.json')

        :param parameter_blueprint_library: Obtained by 'carla.World.get_blueprint_library()'
        :param parameter_sensor_config: json string for sensor setting
        :return: blueprint, transform and attach actor
        """
        local_val_blueprint = None
        if "rgb" in parameter_sensor_config['name_id']:
            local_val_blueprint = parameter_blueprint_library.find('sensor.camera.rgb')
        elif "depth" in parameter_sensor_config['name_id']:
            local_val_blueprint = parameter_blueprint_library.find('sensor.camera.depth')

        # according to the config, set the blueprint
        local_val_blueprint.set_attribute('image_size_x', parameter_sensor_config['image_size']['width'])
        local_val_blueprint.set_attribute('image_size_y', parameter_sensor_config['image_size']['height'])

        # not all sensors have blew settings.
        if 'fov' in parameter_sensor_config.keys():
            local_val_blueprint.set_attribute('fov', parameter_sensor_config['fov'])
        else:
            local_val_blueprint.set_attribute('fov', '90')
        if 'sensor_tick' in parameter_sensor_config.keys():
            local_val_blueprint.set_attribute('sensor_tick', parameter_sensor_config['sensor_tick'])
        else:
            local_val_blueprint.set_attribute('sensor_tick', '0.0')

        # attach actor
        local_val_attach = global_var_vehicle_manager.function_get_vehicle_by_role_name(
            parameter_sensor_config['attach'])

        # attach spawn point transform
        local_val_spawn_point = carla.Transform()
        local_val_spawn_point.location = carla.Location(x=parameter_sensor_config['transform'][0],
                                                        y=parameter_sensor_config['transform'][1],
                                                        z=parameter_sensor_config['transform'][2])
        local_val_spawn_point.rotation = carla.Rotation(pitch=parameter_sensor_config['transform'][3],
                                                        yaw=parameter_sensor_config['transform'][4],
                                                        roll=parameter_sensor_config['transform'][5])

        return local_val_blueprint, local_val_spawn_point, local_val_attach

    def function_spawn_sensors(self,
                               parameter_client: carla.Client,
                               parameter_sensor_configs: list):
        """
        This function must be used when sync mode is off.

        :param parameter_client: client to spawn actors
        :param parameter_sensor_configs:  sensor configs obtained from 'sensor_config.json'
        :return:
        """
        local_val_blueprint_library = parameter_client.get_world().get_blueprint_library()
        local_val_world = parameter_client.get_world()
        for local_val_sensor_config in parameter_sensor_configs:
            local_val_blueprint, local_val_transform, local_val_attach = self._function_get_spawn(
                local_val_sensor_config,
                local_val_blueprint_library)

            local_val_actor = local_val_world.spawn_actor(local_val_blueprint,
                                                          local_val_transform,
                                                          local_val_attach)

            self.__local_val_sensors.append(ClassCubeSensorUnit(local_val_sensor_config['name_id'],
                                                                local_val_blueprint,
                                                                local_val_actor))
        print('\033[1;33;42m[Spawn Sensors]:\033[0m', '    ',
              f'\033[1;33;43m{len(self.__local_val_sensors)}/{len(parameter_sensor_configs)}\033[0m')

    def function_set_save_root_path(self,
                                    parameter_save_root_path):
        self.__local_save_root_path = parameter_save_root_path

    def function_listen_sensors(self):
        """
        This function will listen all sensors in 'self.__local_val_sensors'. After this, sensor will start to obtain
        data .

        :return:
        """
        for sensor in self.__local_val_sensors:
            sensor.function_listen(self.__local_save_root_path)

    def function_start_sensors(self):
        """
        This function will allow sensor to save data by using multiThread

        :return:
        """
        for sensor in self.__local_val_sensors:
            sensor.start()

    @func_set_timeout(5.0)
    def function_sync_sensors(self):
        for sensor in self.__local_val_sensors:
            try:
                sensor.function_sync()
            except func_timeout.exceptions.FunctionTimedOut:
                print('sync_sensors timeout')

    def function_stop_sensors(self):
        for sensor in self.__local_val_sensors:
            sensor.function_stop()

    def function_destroy_sensors(self):
        for sensor in self.__local_val_sensors:
            sensor.function_destroy()


def function_cube_sensor_callback(parameter_data: carla.SensorData,
                                  parameter_name: str,
                                  parameter_cube_sensor: ClassCubeSensorUnit):
    parameter_cube_sensor.function_get_save_queue().put((parameter_name, parameter_data))


instance_var_sensor_manager = ClassSensorManager()
