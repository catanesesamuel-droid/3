#!/usr/bin/env python3
"""
Generador de PCAP con tráfico MQTT simulado
Crea un archivo de captura de red realista para análisis con Wireshark
"""

from scapy.all import *
import json
from datetime import datetime

# Configuración de IPs del sistema domótico
BROKER_IP = "172.28.0.10"
SENSOR_TEMP_IP = "172.28.0.111"
SENSOR_LUZ_SALON_IP = "172.28.0.101"
SENSOR_LUZ_COCINA_IP = "172.28.0.102"
ACTUADOR_LUCES_IP = "172.28.0.121"
ACTUADOR_PERSIANAS_IP = "172.28.0.131"
SCADA_IP = "172.28.0.100"

BROKER_MAC = "02:42:ac:1c:00:0a"
SENSOR_TEMP_MAC = "02:42:ac:1c:00:6f"
SENSOR_LUZ_SALON_MAC = "02:42:ac:1c:00:65"
SENSOR_LUZ_COCINA_MAC = "02:42:ac:1c:00:66"
ACTUADOR_LUCES_MAC = "02:42:ac:1c:00:79"
ACTUADOR_PERSIANAS_MAC = "02:42:ac:1c:00:83"
SCADA_MAC = "02:42:ac:1c:00:64"

MQTT_PORT = 1883

paquetes = []
seq_num = 1000
ack_num = 1000
timestamp = 0.0

def siguiente_seq():
    global seq_num
    seq_num += 1
    return seq_num

def siguiente_ack():
    global ack_num
    ack_num += 1
    return ack_num

def siguiente_tiempo(delta=0.001):
    global timestamp
    timestamp += delta
    return timestamp

# ============================================
# 1. TCP 3-WAY HANDSHAKE (Sensor Temp -> Broker)
# ============================================
print("Generando 3-way handshake TCP...")

# SYN
pkt = Ether(src=SENSOR_TEMP_MAC, dst=BROKER_MAC) / \
      IP(src=SENSOR_TEMP_IP, dst=BROKER_IP, ttl=64) / \
      TCP(sport=45678, dport=MQTT_PORT, flags='S', seq=siguiente_seq(), window=29200)
pkt.time = siguiente_tiempo()
paquetes.append(pkt)

# SYN-ACK
pkt = Ether(src=BROKER_MAC, dst=SENSOR_TEMP_MAC) / \
      IP(src=BROKER_IP, dst=SENSOR_TEMP_IP, ttl=64) / \
      TCP(sport=MQTT_PORT, dport=45678, flags='SA', seq=siguiente_seq(), ack=seq_num+1, window=28960)
pkt.time = siguiente_tiempo(0.002)
paquetes.append(pkt)

# ACK
pkt = Ether(src=SENSOR_TEMP_MAC, dst=BROKER_MAC) / \
      IP(src=SENSOR_TEMP_IP, dst=BROKER_IP, ttl=64) / \
      TCP(sport=45678, dport=MQTT_PORT, flags='A', seq=seq_num, ack=ack_num+1, window=29200)
pkt.time = siguiente_tiempo(0.001)
paquetes.append(pkt)

# ============================================
# 2. MQTT CONNECT
# ============================================
print("Generando MQTT CONNECT...")

mqtt_connect = b'\x10\x1a\x00\x04MQTT\x04\x02\x00<\x00\x10sensor_temp_salon'
pkt = Ether(src=SENSOR_TEMP_MAC, dst=BROKER_MAC) / \
      IP(src=SENSOR_TEMP_IP, dst=BROKER_IP, ttl=64) / \
      TCP(sport=45678, dport=MQTT_PORT, flags='PA', seq=siguiente_seq(), ack=ack_num, window=29200) / \
      Raw(load=mqtt_connect)
pkt.time = siguiente_tiempo(0.01)
paquetes.append(pkt)

# MQTT CONNACK
mqtt_connack = b'\x20\x02\x00\x00'
pkt = Ether(src=BROKER_MAC, dst=SENSOR_TEMP_MAC) / \
      IP(src=BROKER_IP, dst=SENSOR_TEMP_IP, ttl=64) / \
      TCP(sport=MQTT_PORT, dport=45678, flags='PA', seq=siguiente_seq(), ack=seq_num+len(mqtt_connect), window=28960) / \
      Raw(load=mqtt_connack)
pkt.time = siguiente_tiempo(0.005)
paquetes.append(pkt)

# ============================================
# 3. MQTT PUBLISH - Temperatura
# ============================================
print("Generando MQTT PUBLISH (temperatura)...")

topic = "casa/sensor/temperatura/salon"
payload = {
    "sensor_id": "sensor_temp_salon",
    "tipo": "temperatura",
    "valor": 23.5,
    "unidad": "°C",
    "zona": "salon",
    "timestamp": "2025-01-25T10:30:45.123456"
}
payload_json = json.dumps(payload).encode()

# MQTT PUBLISH header
mqtt_publish = b'\x30'  # PUBLISH, QoS 0
remaining_length = 2 + len(topic) + len(payload_json)
mqtt_publish += bytes([remaining_length])
mqtt_publish += len(topic).to_bytes(2, 'big')
mqtt_publish += topic.encode()
mqtt_publish += payload_json

pkt = Ether(src=SENSOR_TEMP_MAC, dst=BROKER_MAC) / \
      IP(src=SENSOR_TEMP_IP, dst=BROKER_IP, ttl=64) / \
      TCP(sport=45678, dport=MQTT_PORT, flags='PA', seq=siguiente_seq(), ack=ack_num, window=29200) / \
      Raw(load=mqtt_publish)
pkt.time = siguiente_tiempo(0.5)
paquetes.append(pkt)

# ACK del broker
pkt = Ether(src=BROKER_MAC, dst=SENSOR_TEMP_MAC) / \
      IP(src=BROKER_IP, dst=SENSOR_TEMP_IP, ttl=64) / \
      TCP(sport=MQTT_PORT, dport=45678, flags='A', seq=siguiente_seq(), ack=seq_num+len(mqtt_publish), window=28960)
pkt.time = siguiente_tiempo(0.002)
paquetes.append(pkt)

# ============================================
# 4. Conexión desde Sensor Luz Salón
# ============================================
print("Generando tráfico Sensor Luz Salón...")

# Handshake rápido
pkt = Ether(src=SENSOR_LUZ_SALON_MAC, dst=BROKER_MAC) / \
      IP(src=SENSOR_LUZ_SALON_IP, dst=BROKER_IP, ttl=64) / \
      TCP(sport=45679, dport=MQTT_PORT, flags='S', seq=siguiente_seq(), window=29200)
pkt.time = siguiente_tiempo(1.0)
paquetes.append(pkt)

pkt = Ether(src=BROKER_MAC, dst=SENSOR_LUZ_SALON_MAC) / \
      IP(src=BROKER_IP, dst=SENSOR_LUZ_SALON_IP, ttl=64) / \
      TCP(sport=MQTT_PORT, dport=45679, flags='SA', seq=siguiente_seq(), ack=seq_num+1, window=28960)
pkt.time = siguiente_tiempo(0.002)
paquetes.append(pkt)

pkt = Ether(src=SENSOR_LUZ_SALON_MAC, dst=BROKER_MAC) / \
      IP(src=SENSOR_LUZ_SALON_IP, dst=BROKER_IP, ttl=64) / \
      TCP(sport=45679, dport=MQTT_PORT, flags='A', seq=seq_num, ack=ack_num+1, window=29200)
pkt.time = siguiente_tiempo(0.001)
paquetes.append(pkt)

# MQTT PUBLISH - Luz
topic = "casa/sensor/luz/salon"
payload = {
    "sensor_id": "sensor_luz_salon",
    "tipo": "luz",
    "valor": 450,
    "unidad": "lux",
    "estado": "luminoso",
    "zona": "salon",
    "timestamp": "2025-01-25T10:30:46.234567"
}
payload_json = json.dumps(payload).encode()

mqtt_publish = b'\x30'
remaining_length = 2 + len(topic) + len(payload_json)
mqtt_publish += bytes([remaining_length])
mqtt_publish += len(topic).to_bytes(2, 'big')
mqtt_publish += topic.encode()
mqtt_publish += payload_json

pkt = Ether(src=SENSOR_LUZ_SALON_MAC, dst=BROKER_MAC) / \
      IP(src=SENSOR_LUZ_SALON_IP, dst=BROKER_IP, ttl=64) / \
      TCP(sport=45679, dport=MQTT_PORT, flags='PA', seq=siguiente_seq(), ack=ack_num, window=29200) / \
      Raw(load=mqtt_publish)
pkt.time = siguiente_tiempo(0.5)
paquetes.append(pkt)

# ============================================
# 5. Conexión desde SCADA - SUBSCRIBE
# ============================================
print("Generando tráfico SCADA (SUBSCRIBE)...")

# Handshake
pkt = Ether(src=SCADA_MAC, dst=BROKER_MAC) / \
      IP(src=SCADA_IP, dst=BROKER_IP, ttl=64) / \
      TCP(sport=45680, dport=MQTT_PORT, flags='S', seq=siguiente_seq(), window=29200)
pkt.time = siguiente_tiempo(2.0)
paquetes.append(pkt)

pkt = Ether(src=BROKER_MAC, dst=SCADA_MAC) / \
      IP(src=BROKER_IP, dst=SCADA_IP, ttl=64) / \
      TCP(sport=MQTT_PORT, dport=45680, flags='SA', seq=siguiente_seq(), ack=seq_num+1, window=28960)
pkt.time = siguiente_tiempo(0.002)
paquetes.append(pkt)

pkt = Ether(src=SCADA_MAC, dst=BROKER_MAC) / \
      IP(src=SCADA_IP, dst=BROKER_IP, ttl=64) / \
      TCP(sport=45680, dport=MQTT_PORT, flags='A', seq=seq_num, ack=ack_num+1, window=29200)
pkt.time = siguiente_tiempo(0.001)
paquetes.append(pkt)

# MQTT SUBSCRIBE a casa/sensor/#
topic = "casa/sensor/#"
mqtt_subscribe = b'\x82'  # SUBSCRIBE
remaining_length = 2 + 2 + len(topic) + 1  # packet_id + topic_len + topic + qos
mqtt_subscribe += bytes([remaining_length])
mqtt_subscribe += b'\x00\x01'  # Packet ID
mqtt_subscribe += len(topic).to_bytes(2, 'big')
mqtt_subscribe += topic.encode()
mqtt_subscribe += b'\x01'  # QoS 1

pkt = Ether(src=SCADA_MAC, dst=BROKER_MAC) / \
      IP(src=SCADA_IP, dst=BROKER_IP, ttl=64) / \
      TCP(sport=45680, dport=MQTT_PORT, flags='PA', seq=siguiente_seq(), ack=ack_num, window=29200) / \
      Raw(load=mqtt_subscribe)
pkt.time = siguiente_tiempo(0.1)
paquetes.append(pkt)

# MQTT SUBACK
mqtt_suback = b'\x90\x03\x00\x01\x01'  # SUBACK with QoS 1 granted
pkt = Ether(src=BROKER_MAC, dst=SCADA_MAC) / \
      IP(src=BROKER_IP, dst=SCADA_IP, ttl=64) / \
      TCP(sport=MQTT_PORT, dport=45680, flags='PA', seq=siguiente_seq(), ack=seq_num+len(mqtt_subscribe), window=28960) / \
      Raw(load=mqtt_suback)
pkt.time = siguiente_tiempo(0.003)
paquetes.append(pkt)

# ============================================
# 6. Actuador recibe comando (Broker -> Actuador)
# ============================================
print("Generando comando a actuador de luces...")

# El broker reenvía un comando al actuador
topic = "casa/actuador/luces/comandos"
payload = {
    "tipo": "luces",
    "accion": "encender",
    "luz": "salon_principal",
    "intensidad": 100,
    "timestamp": "2025-01-25T10:30:48.567890"
}
payload_json = json.dumps(payload).encode()

mqtt_publish = b'\x30'
remaining_length = 2 + len(topic) + len(payload_json)
mqtt_publish += bytes([remaining_length])
mqtt_publish += len(topic).to_bytes(2, 'big')
mqtt_publish += topic.encode()
mqtt_publish += payload_json

pkt = Ether(src=BROKER_MAC, dst=ACTUADOR_LUCES_MAC) / \
      IP(src=BROKER_IP, dst=ACTUADOR_LUCES_IP, ttl=64) / \
      TCP(sport=MQTT_PORT, dport=45681, flags='PA', seq=siguiente_seq(), ack=ack_num, window=28960) / \
      Raw(load=mqtt_publish)
pkt.time = siguiente_tiempo(0.5)
paquetes.append(pkt)

# ============================================
# 7. Más tráfico periódico de sensores
# ============================================
print("Generando tráfico periódico...")

for i in range(3):
    # Sensor temperatura cada 10 segundos
    payload = {
        "sensor_id": "sensor_temp_salon",
        "tipo": "temperatura",
        "valor": 23.5 + (i * 0.3),
        "unidad": "°C",
        "zona": "salon",
        "timestamp": f"2025-01-25T10:3{1+i}:00.000000"
    }
    payload_json = json.dumps(payload).encode()

    topic = "casa/sensor/temperatura/salon"
    mqtt_publish = b'\x30'
    remaining_length = 2 + len(topic) + len(payload_json)
    mqtt_publish += bytes([remaining_length])
    mqtt_publish += len(topic).to_bytes(2, 'big')
    mqtt_publish += topic.encode()
    mqtt_publish += payload_json

    pkt = Ether(src=SENSOR_TEMP_MAC, dst=BROKER_MAC) / \
          IP(src=SENSOR_TEMP_IP, dst=BROKER_IP, ttl=64) / \
          TCP(sport=45678, dport=MQTT_PORT, flags='PA', seq=siguiente_seq(), ack=ack_num, window=29200) / \
          Raw(load=mqtt_publish)
    pkt.time = siguiente_tiempo(10.0)
    paquetes.append(pkt)

# ============================================
# Guardar PCAP
# ============================================
print(f"\nGenerando archivo PCAP con {len(paquetes)} paquetes...")
wrpcap('/home/user/ciber-desarrollo-domotica/domotica-simple/capturas/captura.pcap', paquetes)
print("✅ Archivo guardado: capturas/captura.pcap")
print(f"📊 Total de paquetes: {len(paquetes)}")
print("\n🔍 Para abrir con Wireshark:")
print("   wireshark capturas/captura.pcap")
print("\n📌 Filtros útiles:")
print("   - tcp.port == 1883")
print("   - mqtt")
print("   - tcp.flags.syn == 1")
print("   - mqtt.msgtype == 3")
