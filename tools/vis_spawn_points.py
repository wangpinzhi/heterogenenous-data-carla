import sys,os
parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)

from utilities import get_args

import carla,logging,cv2,re

if __name__ == '__main__':

    args = get_args()
    logging.basicConfig(format='[%(levelname)s]: %(message)s', level=logging.INFO)

    # 创建client
    client = carla.Client(args.server_ip, args.server_port)
    client.set_timeout(10.0)

    # 获取world
    world = client.get_world()

    # 获取当前map
    
    reg = re.compile('Town\d\d')
    old_map = re.findall(reg,world.get_map().name)
    logging.info('world map: %s',old_map[0])

    # 获取所有 spawn points
    spawn_points = world.get_map().get_spawn_points()
    walker_spawn_location = carla.Location(x=-36,y=36,z=0.6)

    logging.info('Found %d recommanded spawn points',len(spawn_points))

    for i, spawn_point in enumerate(spawn_points):
        world.debug.draw_string(spawn_point.location, str(f'i:{i}, y:{spawn_point.location.y}'), life_time=10)
    world.debug.draw_string(walker_spawn_location, 'walker', color=carla.Color(0,255,0,255),life_time=20)