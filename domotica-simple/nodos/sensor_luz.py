#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime
import argparse

def main():
    parser = argparse.ArgumentParser(description='Sensor de Luz Domótica')
    parser.add_argument('--zona', required=True, help='Zona del sensor (salon, cocina, etc)')
    parser.add_argument('--id', required=True, help='ID único del sensor')
    args = parser.parse_args()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=args.id)

    def on_connect(client, userdata, flags, rc):
        print(f"✅ Sensor {args.id} conectado a MQTT")
    
    client.on_connect = on_connect
    client.connect("mqtt", 1883, 60)
    client.loop_start()
    
    print(f"💡 Sensor de Luz iniciado: {args.id} en zona {args.zona}")
    
    try:
        while True:
            # Simular lectura de sensor LDR
            hora = datetime.now().hour
            
            if 6 <= hora <= 18:  # Día
                valor_base = random.randint(200, 500)
            else:  # Noche
                valor_base = random.randint(600, 900)
            
            # Variación aleatoria
            valor = valor_base + random.randint(-50, 50)
            valor = max(0, min(1000, valor))
            
            # Determinar estado
            if valor > 700:
                estado = "oscuro"
            elif valor < 300:
                estado = "luminoso"
            else:
                estado = "normal"
            
            datos = {
                "sensor_id": args.id,
                "tipo": "luz",
                "valor": valor,
                "unidad": "lux_relativo",
                "estado": estado,
                "zona": args.zona,
                "timestamp": datetime.now().isoformat()
            }
            
            # Publicar en MQTT
            topic = f"casa/sensor/luz/{args.zona}"
            client.publish(topic, json.dumps(datos), qos=1)
            
            print(f"📤 [{args.id}] Luz: {valor} ({estado})")
            
            time.sleep(5)  # Publicar cada 5 segundos
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Apagando sensor {args.id}...")
        client.disconnect()

if __name__ == "__main__":
    main()