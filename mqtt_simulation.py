import paho.mqtt.client as mqtt

MQTT_BROKER = "mqtt.eclipseprojects.io"
MQTT_TOPIC = "room/occupancy"

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    if message == "Occupied":
        print("🔆 Lights ON (People Detected)")
    else:
        print("💡 Lights OFF (Room Empty)")

client = mqtt.Client()
client.connect(MQTT_BROKER, 1883, 60)
client.subscribe(MQTT_TOPIC)

client.on_message = on_message
print("Listening for occupancy updates...")

client.loop_forever()
