import json
import subprocess
import time
import paho.mqtt.client as mqtt

MQTT_BROKER = "homelab"
MQTT_PORT = 1883
MQTT_BATTERY_STATE_TOPIC = "heroloverpc/mouse/battery/state"

UTILITY_PATH = "C:/Users/anton/Projects/my/razer-mouse-battery/build/Release/razer-mouse-battery.exe"

def get_battery_state():
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

        result = subprocess.run(UTILITY_PATH, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, startupinfo=startupinfo)
        data = json.loads(result.stdout)

        status = data.get("Status")
        is_idle = data.get("IsIdle")
        if status == "OK" and not is_idle:
            return result.stdout

    except Exception as e:
        print(f"Error: {e}")

    return None

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code != 0:
        return

    payload = get_battery_state()
    if payload is not None:
        print(f"Publish: {payload}")

        client.publish(MQTT_BATTERY_STATE_TOPIC, payload=payload)

    client.disconnect()

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

if __name__ == "__main__":
    main()
