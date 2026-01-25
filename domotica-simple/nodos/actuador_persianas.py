#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import json
import time
import threading
from datetime import datetime
import argparse

class ActuadorPersianas:
    def __init__(self, nodo_id):
        self.nodo_id = nodo_id
        self.posicion = 50  # 0-100%
        self.movimiento = False
        self.velocidad = 10  # % por segundo
        
        self.client = mqtt.Client(client_id=nodo_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
    
    def on_connect(self, client, userdata, flags, rc):
        print(f"✅ Actuador {self.nodo_id} conectado a MQTT")
        self.client.subscribe(f"casa/actuador/persianas/comandos", qos=2)
        self.publicar_estado()
    
    def on_message(self, client, userdata, msg):
        try:
            comando = json.loads(msg.payload.decode())
            accion = comando.get("accion")
            
            if accion == "subir":
                porcentaje = comando.get("porcentaje", 100)
                self.mover_a(porcentaje, "subiendo")
                
            elif accion == "bajar":
                porcentaje = comando.get("porcentaje", 0)
                self.mover_a(porcentaje, "bajando")
                
            elif accion == "parar":
                self.movimiento = False
                print(f"⏹️  [{self.nodo_id}] Movimiento detenido")
                
            elif accion == "estado":
                self.publicar_estado()
            
            print(f"📨 [{self.nodo_id}] Comando procesado: {accion}")
            
        except Exception as e:
            print(f"❌ Error procesando comando: {e}")
    
    def mover_a(self, objetivo, direccion):
        if self.movimiento:
            print(f"⚠️  [{self.nodo_id}] Ya hay un movimiento en curso")
            return
        
        def movimiento_thread():
            self.movimiento = True
            
            while self.movimiento and self.posicion != objetivo:
                if objetivo > self.posicion:
                    self.posicion += 1
                else:
                    self.posicion -= 1
                
                self.posicion = max(0, min(100, self.posicion))
                
                # Publicar progreso
                self.publicar_estado()
                
                # Simular tiempo de movimiento
                time.sleep(1 / self.velocidad)
                
                if self.posicion == objetivo:
                    break
            
            self.movimiento = False
            print(f"🪟 [{self.nodo_id}] Persianas {direccion} al {self.posicion}%")
            self.publicar_estado()
            self.publicar_evento(direccion)
        
        # Iniciar movimiento en hilo separado
        thread = threading.Thread(target=movimiento_thread, daemon=True)
        thread.start()
    
    def publicar_estado(self):
        estado = {
            "actuador_id": self.nodo_id,
            "tipo": "persianas",
            "posicion": self.posicion,
            "movimiento": self.movimiento,
            "velocidad": self.velocidad,
            "timestamp": datetime.now().isoformat()
        }
        
        self.client.publish(f"casa/actuador/persianas/estado", json.dumps(estado), retain=True)
    
    def publicar_evento(self, evento):
        datos = {
            "actuador_id": self.nodo_id,
            "evento": evento,
            "posicion": self.posicion,
            "timestamp": datetime.now().isoformat()
        }
        
        self.client.publish(f"casa/eventos/persianas", json.dumps(datos))
    
    def run(self):
        self.client.connect("mqtt", 1883, 60)
        self.client.loop_forever()

def main():
    parser = argparse.ArgumentParser(description='Actuador de Persianas Domótica')
    parser.add_argument('--id', required=True, help='ID único del actuador')
    args = parser.parse_args()
    
    print(f"🪟 Actuador de Persianas iniciado: {args.id}")
    
    actuador = ActuadorPersianas(args.id)
    actuador.run()

if __name__ == "__main__":
    main()