#!/usr/bin/env python3
import socket
import json
import threading
import time
import paho.mqtt.client as mqtt
from datetime import datetime

class AlarmServer:
    def __init__(self):
        self.armada = False
        self.alerta_activa = False
        self.sensores = {}
        
        # Socket UDP
        self.udp_port = 9999
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', self.udp_port))
        self.sock.settimeout(1)
        
        # Cliente MQTT
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="alarm_server")
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        
    def on_mqtt_connect(self, client, userdata, flags, rc):
        print(f"✅ Servidor de alarma conectado a MQTT")
        self.mqtt_client.subscribe("casa/alarma/comandos", qos=2)
        self.publicar_estado()
    
    def on_mqtt_message(self, client, userdata, msg):
        try:
            comando = json.loads(msg.payload.decode())
            accion = comando.get("accion")
            
            if accion == "armar":
                self.armar_alarma()
                
            elif accion == "desarmar":
                self.desarmar_alarma()
                
            elif accion == "estado":
                self.publicar_estado()
                
            elif accion == "test":
                print("🔊 Test de alarma realizado")
                self.mqtt_client.publish(
                    "casa/alarma/test",
                    json.dumps({"resultado": "ok", "timestamp": datetime.now().isoformat()})
                )
                
        except Exception as e:
            print(f"❌ Error procesando comando MQTT: {e}")
    
    def armar_alarma(self):
        self.armada = True
        self.alerta_activa = False
        print("🔒 ALARMA ARMADA")
        self.mqtt_client.publish("casa/alarma/estado", "ARMADA", retain=True)
        
        # Notificar a todos
        self.mqtt_client.publish(
            "casa/eventos/alarma",
            json.dumps({
                "evento": "armada",
                "timestamp": datetime.now().isoformat()
            })
        )
    
    def desarmar_alarma(self):
        self.armada = False
        self.alerta_activa = False
        print("🔓 ALARMA DESARMADA")
        self.mqtt_client.publish("casa/alarma/estado", "DESARMADA", retain=True)
        
        # Desactivar sirena
        self.mqtt_client.publish(
            "casa/actuador/sirena/comandos",
            json.dumps({"accion": "desactivar"})
        )
    
    def procesar_mensaje_udp(self, data, addr):
        try:
            mensaje = json.loads(data.decode())
            sensor_id = mensaje.get('sensor_id')
            tipo = mensaje.get('tipo')
            
            print(f"📨 [UDP] {sensor_id}: {tipo}")
            
            # Registrar sensor activo
            self.sensores[sensor_id] = time.time()
            
            if tipo == "trigger" and self.armada:
                self.activar_alerta(sensor_id, mensaje.get('motivo', 'Intrusión detectada'))
                
            # Publicar en MQTT
            self.mqtt_client.publish(
                f"casa/alarma/sensores/{sensor_id}",
                json.dumps({
                    **mensaje,
                    "timestamp": datetime.now().isoformat()
                })
            )
            
        except Exception as e:
            print(f"❌ Error procesando mensaje UDP: {e}")
    
    def activar_alerta(self, sensor_id, motivo):
        if not self.alerta_activa:
            self.alerta_activa = True
            print(f"🚨 ALERTA ACTIVADA! Sensor: {sensor_id}, Motivo: {motivo}")
            
            # Publicar alerta MQTT
            alerta = {
                "tipo": "intrusion",
                "sensor": sensor_id,
                "motivo": motivo,
                "timestamp": datetime.now().isoformat(),
                "accion": "REQUIERE ATENCIÓN"
            }
            
            self.mqtt_client.publish(
                "casa/alertas/alarma",
                json.dumps(alerta),
                qos=2
            )
            
            # Activar sirena (simulada)
            self.mqtt_client.publish(
                "casa/actuador/sirena/comandos",
                json.dumps({"accion": "activar"})
            )
    
    def publicar_estado(self):
        estado = {
            "armada": self.armada,
            "alerta_activa": self.alerta_activa,
            "sensores_activos": len(self.sensores),
            "timestamp": datetime.now().isoformat()
        }
        self.mqtt_client.publish("casa/alarma/estado_detallado", json.dumps(estado))
    
    def verificar_sensores(self):
        """Verifica que los sensores estén activos"""
        while True:
            time.sleep(30)
            ahora = time.time()
            
            for sensor_id, ultimo_contacto in list(self.sensores.items()):
                if ahora - ultimo_contacto > 60:  # 60 segundos sin contacto
                    print(f"⚠️  Sensor {sensor_id} inactivo")
                    del self.sensores[sensor_id]
                    
                    self.mqtt_client.publish(
                        "casa/alertas/sensor_inactivo",
                        json.dumps({
                            "sensor": sensor_id,
                            "timestamp": datetime.now().isoformat()
                        })
                    )
    
    def run(self):
        # Conectar a MQTT
        self.mqtt_client.connect("mqtt", 1883, 60)
        self.mqtt_client.loop_start()
        
        # Iniciar verificación de sensores
        verificacion_thread = threading.Thread(target=self.verificar_sensores, daemon=True)
        verificacion_thread.start()
        
        print(f"🚨 Servidor de alarma iniciado en puerto UDP {self.udp_port}")
        print("📡 Esperando mensajes UDP...")
        
        try:
            while True:
                try:
                    data, addr = self.sock.recvfrom(1024)
                    self.procesar_mensaje_udp(data, addr)
                except socket.timeout:
                    continue
                    
        except KeyboardInterrupt:
            print("\n⏹️  Apagando servidor de alarma...")
            self.sock.close()
            self.mqtt_client.disconnect()

if __name__ == "__main__":
    alarm_server = AlarmServer()
    alarm_server.run()