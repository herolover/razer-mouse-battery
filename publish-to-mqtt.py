import json
import subprocess
import time
import paho.mqtt.client as mqtt

MQTT_BROKER = "homelab"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/mouse/heroloverpc_razer"

UTILITY_PATH = "C:/Users/anton/Projects/my/razer-mouse-battery/build/Release/razer-mouse-battery.exe"

def get_battery_level():
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

        result = subprocess.run(UTILITY_PATH, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, startupinfo=startupinfo)
        data = json.loads(result.stdout)

        battery_level = data.get("BatteryLevel")
        is_idle = data.get("IsIdle")
        if battery_level is not None and not is_idle:
            return round(battery_level, 1)

    except Exception as e:
        print(f"Error: {e}")

    return None

def publish_battery_level(client):
    battery_level = get_battery_level()
    if battery_level is not None:
        print(f"Publish battery level: {battery_level}")
        client.publish(MQTT_TOPIC, payload=battery_level)

def main():
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    publish_battery_level(client)

if __name__ == "__main__":
    main()
