#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
import argparse

class ActuadorLuces:
    def __init__(self, nodo_id, zona):
        self.nodo_id = nodo_id
        self.zona = zona
        self.estado = "off"
        self.intensidad = 0
        
        self.client = mqtt.Client(client_id=nodo_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
    def on_connect(self, client, userdata, flags, rc):
        print(f"✅ Actuador {self.nodo_id} conectado a MQTT")
        # Suscribirse a comandos
        self.client.subscribe(f"casa/actuador/luces/comandos", qos=2)
        self.client.subscribe(f"casa/actuador/luces/{self.zona}/comandos", qos=2)
        
        # Publicar estado inicial
        self.publicar_estado()
    
    def on_message(self, client, userdata, msg):
        try:
            comando = json.loads(msg.payload.decode())
            
            # Verificar si el comando es para esta zona
            if comando.get("zona") == self.zona or comando.get("luz", "").endswith(self.zona):
                accion = comando.get("accion")
                
                if accion == "encender":
                    intensidad = comando.get("intensidad", 100)
                    self.encender(intensidad)
                    
                elif accion == "apagar":
                    self.apagar()
                    
                elif accion == "intensidad":
                    intensidad = comando.get("valor", 50)
                    self.ajustar_intensidad(intensidad)
                
                print(f"📨 [{self.nodo_id}] Comando procesado: {accion}")
                
        except Exception as e:
            print(f"❌ Error procesando comando: {e}")
    
    def encender(self, intensidad=100):
        self.estado = "on"
        self.intensidad = max(0, min(100, intensidad))
        print(f"💡 [{self.nodo_id}] Luz ENCENDIDA al {self.intensidad}%")
        self.publicar_estado()
        self.publicar_evento("encendido")
    
    def apagar(self):
        self.estado = "off"
        self.intensidad = 0
        print(f"💡 [{self.nodo_id}] Luz APAGADA")
        self.publicar_estado()
        self.publicar_evento("apagado")
    
    def ajustar_intensidad(self, intensidad):
        self.intensidad = max(0, min(100, intensidad))
        if self.intensidad > 0:
            self.estado = "on"
        else:
            self.estado = "off"
            
        print(f"💡 [{self.nodo_id}] Intensidad ajustada: {self.intensidad}%")
        self.publicar_estado()
    
    def publicar_estado(self):
        estado = {
            "actuador_id": self.nodo_id,
            "tipo": "luces",
            "estado": self.estado,
            "intensidad": self.intensidad,
            "zona": self.zona,
            "timestamp": datetime.now().isoformat()
        }
        
        self.client.publish(f"casa/actuador/luces/estado/{self.zona}", json.dumps(estado), retain=True)
    
    def publicar_evento(self, evento):
        datos = {
            "actuador_id": self.nodo_id,
            "evento": evento,
            "intensidad": self.intensidad,
            "zona": self.zona,
            "timestamp": datetime.now().isoformat()
        }
        
        self.client.publish(f"casa/eventos/luces/{self.zona}", json.dumps(datos))
    
    def run(self):
        self.client.connect("mqtt", 1883, 60)
        self.client.loop_forever()

def main():
    parser = argparse.ArgumentParser(description='Actuador de Luces Domótica')
    parser.add_argument('--zona', required=True, help='Zona del actuador')
    parser.add_argument('--id', required=True, help='ID único del actuador')
    args = parser.parse_args()
    
    print(f"💡 Actuador de Luces iniciado: {args.id} en zona {args.zona}")
    
    actuador = ActuadorLuces(args.id, args.zona)
    actuador.run()

if __name__ == "__main__":
    main()