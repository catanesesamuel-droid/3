#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime
import argparse

def main():
    parser = argparse.ArgumentParser(description='Sensor de Temperatura Domótica')
    parser.add_argument('--zona', required=True, help='Zona del sensor')
    parser.add_argument('--id', required=True, help='ID único del sensor')
    args = parser.parse_args()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=args.id)

    def on_connect(client, userdata, flags, rc):
        print(f"✅ Sensor {args.id} conectado a MQTT")
    
    client.on_connect = on_connect
    client.connect("mqtt", 1883, 60)
    client.loop_start()
    
    print(f"🌡️  Sensor de Temperatura iniciado: {args.id} en zona {args.zona}")
    
    # Temperatura base por hora del día
    temp_base = {
        "noche": 19.0,    # 0-6h
        "mañana": 21.0,   # 6-12h
        "tarde": 24.0,    # 12-18h
        "noche_tarde": 22.0  # 18-24h
    }
    
    try:
        while True:
            hora = datetime.now().hour
            
            # Determinar franja horaria
            if 0 <= hora < 6:
                base = temp_base["noche"]
            elif 6 <= hora < 12:
                base = temp_base["mañana"]
            elif 12 <= hora < 18:
                base = temp_base["tarde"]
            else:
                base = temp_base["noche_tarde"]
            
            # Simular temperatura con variación
            temperatura = base + random.uniform(-2, 2)
            humedad = 50 + random.uniform(-10, 10)
            
            datos_temp = {
                "sensor_id": args.id,
                "tipo": "temperatura",
                "valor": round(temperatura, 1),
                "unidad": "°C",
                "zona": args.zona,
                "timestamp": datetime.now().isoformat()
            }
            
            datos_hum = {
                "sensor_id": args.id,
                "tipo": "humedad",
                "valor": round(humedad, 1),
                "unidad": "%",
                "zona": args.zona,
                "timestamp": datetime.now().isoformat()
            }
            
            # Publicar en MQTT
            client.publish(f"casa/sensor/temperatura/{args.zona}", json.dumps(datos_temp), qos=1)
            client.publish(f"casa/sensor/humedad/{args.zona}", json.dumps(datos_hum), qos=1)
            
            print(f"📤 [{args.id}] Temp: {round(temperatura, 1)}°C, Hum: {round(humedad, 1)}%")
            
            time.sleep(10)  # Publicar cada 10 segundos
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Apagando sensor {args.id}...")
        client.disconnect()

if __name__ == "__main__":
    main()