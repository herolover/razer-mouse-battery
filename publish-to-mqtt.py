import json
import subprocess
import time
import paho.mqtt.client as mqtt

MQTT_BROKER = "homelab"
MQTT_PORT = 1883
MQTT_BATTERY_LEVEL_TOPIC = "heroloverpc/mouse/battery/level"
MQTT_IS_CHARGING_TOPIC = "heroloverpc/mouse/battery/is_charging"

UTILITY_PATH = "C:/Users/anton/Projects/my/razer-mouse-battery/build/Release/razer-mouse-battery.exe"

def get_battery_level():
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

        result = subprocess.run(UTILITY_PATH, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, startupinfo=startupinfo)
        data = json.loads(result.stdout)

        battery_level = data.get("BatteryLevel")
        is_charging = data.get("IsCharging")
        is_idle = data.get("IsIdle")
        if battery_level is not None and not is_idle:
            return (round(battery_level, 1), is_charging)

    except Exception as e:
        print(f"Error: {e}")

    return (None, None)

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code != 0:
        return

    (battery_level, is_charging) = get_battery_level()
    if battery_level is not None:
        payload="{\"state\": \"on\"}" if is_charging else "{\"state\": \"off\"}"
        print(f"Publish: level: {battery_level}%, is_charging: {is_charging} {payload}")

        client.publish(MQTT_BATTERY_LEVEL_TOPIC, payload=battery_level)
        client.publish(MQTT_IS_CHARGING_TOPIC, payload="{\"state\":\"ON\"}" if is_charging else "{\"state\":\"OFF\"}")

    client.disconnect()

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

if __name__ == "__main__":
    main()
