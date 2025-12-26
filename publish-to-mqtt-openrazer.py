import json
import subprocess
import time
import paho.mqtt.client as mqtt

from openrazer.client import DeviceManager

MQTT_BROKER = "homelab"
MQTT_PORT = 1883
MQTT_BATTERY_STATE_TOPIC = "heroloverpc/mouse/battery/state"

def get_battery_state():
    device_manager = DeviceManager()
    device = device_manager.devices[1]

    return {
        "Status": "OK",
        "BatteryLevel": device.battery_level,
        "IsIdle": False,
        "IsCharging": device.is_charging,
    }

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    while True:
        client.publish(MQTT_BATTERY_STATE_TOPIC, payload=json.dumps(get_battery_state()))

        time.sleep(30)

if __name__ == "__main__":
    main()
