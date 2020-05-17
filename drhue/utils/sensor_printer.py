from drhue.bridge import DrHueBridge
from drhue.context import Context
from drhue.entities.sensor import Sensor
from reprint import output


def read_sensors(sensor_names):
    sensors = [Sensor(sensor_name) for sensor_name in sensor_names]
    context = Context(
        bridge=DrHueBridge(),
        refresh_interval=1
    )
    for sensor in sensors:
        sensor.attach_context(context)

    while True:
        info = {}
        for sensor in sensors:
            info[sensor.name] ={
                "dark": sensor.read('dark'),
                'motion': sensor.read('motion')
            }
        with output(output_type="dict") as output_dict:
            for sensor, sensor_data in info.items():
                output_dict[sensor+' dark'] = sensor_data['dark']
                output_dict[sensor+' motion'] = sensor_data['motion']

        context.update_and_wait(log=False)
        for sensor in sensors:
            sensor.sync_states()


if __name__ == '__main__':
    read_sensors(['Kitchen sensor', 'Lounge sensor', 'Hallway sensor'])
