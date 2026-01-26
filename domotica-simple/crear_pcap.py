#!/usr/bin/env python3
"""
Crea un archivo PCAP válido con tráfico MQTT simulado
Sin dependencias externas - solo Python estándar
"""

import struct
import time
import json

def crear_pcap_header():
    """Crea la cabecera global del archivo PCAP"""
    # magic_number, version_major, version_minor, thiszone, sigfigs, snaplen, network
    return struct.pack('IHHiIII',
                      0xa1b2c3d4,  # magic number
                      2, 4,         # version 2.4
                      0, 0,         # timezone, sigfigs
                      65535,        # snaplen
                      1)            # Ethernet

def crear_pcap_packet(timestamp, data):
    """Crea un paquete PCAP"""
    ts_sec = int(timestamp)
    ts_usec = int((timestamp - ts_sec) * 1000000)
    packet_len = len(data)

    # ts_sec, ts_usec, incl_len, orig_len
    header = struct.pack('IIII', ts_sec, ts_usec, packet_len, packet_len)
    return header + data

def eth_header(dst_mac, src_mac, ethertype=0x0800):
    """Crea cabecera Ethernet"""
    dst = bytes.fromhex(dst_mac.replace(':', ''))
    src = bytes.fromhex(src_mac.replace(':', ''))
    return dst + src + struct.pack('!H', ethertype)

def ip_header(src_ip, dst_ip, protocol, payload_len):
    """Crea cabecera IP"""
    version_ihl = 0x45  # IPv4, header length 20
    dscp_ecn = 0
    total_len = 20 + payload_len
    identification = 0x1234
    flags_fragment = 0x4000  # Don't Fragment
    ttl = 64

    # Checksum temporal
    src = list(map(int, src_ip.split('.')))
    dst = list(map(int, dst_ip.split('.')))

    header = struct.pack('!BBHHHBBH4s4s',
                        version_ihl, dscp_ecn, total_len,
                        identification, flags_fragment,
                        ttl, protocol, 0,  # checksum placeholder
                        bytes(src), bytes(dst))

    # Calcular checksum
    checksum = calcular_checksum(header)
    header = struct.pack('!BBHHHBBH4s4s',
                        version_ihl, dscp_ecn, total_len,
                        identification, flags_fragment,
                        ttl, protocol, checksum,
                        bytes(src), bytes(dst))
    return header

def tcp_header(src_port, dst_port, seq, ack, flags, window=29200):
    """Crea cabecera TCP"""
    data_offset = 5 << 4  # 5 words = 20 bytes

    header = struct.pack('!HHIIBBHHH',
                        src_port, dst_port,
                        seq, ack,
                        data_offset, flags,
                        window,
                        0,  # checksum placeholder
                        0)  # urgent pointer
    return header

def calcular_checksum(data):
    """Calcula checksum IP/TCP"""
    if len(data) % 2 == 1:
        data += b'\x00'

    s = sum(struct.unpack('!%dH' % (len(data) // 2), data))
    s = (s >> 16) + (s & 0xffff)
    s += s >> 16
    return ~s & 0xffff

# Configuración
BROKER_MAC = "02:42:ac:1c:00:0a"
SENSOR_TEMP_MAC = "02:42:ac:1c:00:6f"
SENSOR_LUZ_MAC = "02:42:ac:1c:00:65"

BROKER_IP = "172.28.0.10"
SENSOR_TEMP_IP = "172.28.0.111"
SENSOR_LUZ_IP = "172.28.0.101"

MQTT_PORT = 1883

# Crear archivo PCAP
pcap_data = crear_pcap_header()
timestamp = time.time()

print("Generando tráfico MQTT simulado...")

# ========================================
# 1. TCP 3-way handshake (SYN)
# ========================================
print("  [1] TCP SYN")
eth = eth_header(BROKER_MAC, SENSOR_TEMP_MAC)
ip = ip_header(SENSOR_TEMP_IP, BROKER_IP, 6, 20)  # protocol 6 = TCP
tcp = tcp_header(45678, MQTT_PORT, 1000, 0, 0x02, 29200)  # SYN flag

packet = eth + ip + tcp
pcap_data += crear_pcap_packet(timestamp, packet)
timestamp += 0.002

# ========================================
# 2. TCP SYN-ACK
# ========================================
print("  [2] TCP SYN-ACK")
eth = eth_header(SENSOR_TEMP_MAC, BROKER_MAC)
ip = ip_header(BROKER_IP, SENSOR_TEMP_IP, 6, 20)
tcp = tcp_header(MQTT_PORT, 45678, 2000, 1001, 0x12, 28960)  # SYN+ACK flags

packet = eth + ip + tcp
pcap_data += crear_pcap_packet(timestamp, packet)
timestamp += 0.001

# ========================================
# 3. TCP ACK
# ========================================
print("  [3] TCP ACK")
eth = eth_header(BROKER_MAC, SENSOR_TEMP_MAC)
ip = ip_header(SENSOR_TEMP_IP, BROKER_IP, 6, 20)
tcp = tcp_header(45678, MQTT_PORT, 1001, 2001, 0x10, 29200)  # ACK flag

packet = eth + ip + tcp
pcap_data += crear_pcap_packet(timestamp, packet)
timestamp += 0.5

# ========================================
# 4. MQTT CONNECT
# ========================================
print("  [4] MQTT CONNECT")
mqtt_connect = b'\x10\x1a\x00\x04MQTT\x04\x02\x00<\x00\x10sensor_temp_salon'

eth = eth_header(BROKER_MAC, SENSOR_TEMP_MAC)
ip = ip_header(SENSOR_TEMP_IP, BROKER_IP, 6, 20 + len(mqtt_connect))
tcp = tcp_header(45678, MQTT_PORT, 1001, 2001, 0x18, 29200)  # PSH+ACK

packet = eth + ip + tcp + mqtt_connect
pcap_data += crear_pcap_packet(timestamp, packet)
timestamp += 0.01

# ========================================
# 5. MQTT CONNACK
# ========================================
print("  [5] MQTT CONNACK")
mqtt_connack = b'\x20\x02\x00\x00'

eth = eth_header(SENSOR_TEMP_MAC, BROKER_MAC)
ip = ip_header(BROKER_IP, SENSOR_TEMP_IP, 6, 20 + len(mqtt_connack))
tcp = tcp_header(MQTT_PORT, 45678, 2001, 1001 + len(mqtt_connect), 0x18, 28960)

packet = eth + ip + tcp + mqtt_connack
pcap_data += crear_pcap_packet(timestamp, packet)
timestamp += 1.0

# ========================================
# 6. MQTT PUBLISH - Temperatura
# ========================================
print("  [6] MQTT PUBLISH (temperatura)")
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

# Construir mensaje MQTT PUBLISH
mqtt_msg = b'\x30'  # PUBLISH, QoS 0
remaining_len = 2 + len(topic) + len(payload_json)
mqtt_msg += bytes([remaining_len])
mqtt_msg += struct.pack('!H', len(topic)) + topic.encode()
mqtt_msg += payload_json

eth = eth_header(BROKER_MAC, SENSOR_TEMP_MAC)
ip = ip_header(SENSOR_TEMP_IP, BROKER_IP, 6, 20 + len(mqtt_msg))
tcp = tcp_header(45678, MQTT_PORT, 1001 + len(mqtt_connect), 2001 + len(mqtt_connack), 0x18, 29200)

packet = eth + ip + tcp + mqtt_msg
pcap_data += crear_pcap_packet(timestamp, packet)
timestamp += 0.002

# ========================================
# 7. TCP ACK
# ========================================
print("  [7] TCP ACK")
eth = eth_header(SENSOR_TEMP_MAC, BROKER_MAC)
ip = ip_header(BROKER_IP, SENSOR_TEMP_IP, 6, 20)
tcp = tcp_header(MQTT_PORT, 45678, 2001 + len(mqtt_connack), 1001 + len(mqtt_connect) + len(mqtt_msg), 0x10, 28960)

packet = eth + ip + tcp
pcap_data += crear_pcap_packet(timestamp, packet)
timestamp += 2.0

# ========================================
# 8. MQTT PUBLISH - Luz
# ========================================
print("  [8] MQTT PUBLISH (luz)")
topic = "casa/sensor/luz/salon"
payload = {
    "sensor_id": "sensor_luz_salon",
    "tipo": "luz",
    "valor": 450,
    "unidad": "lux",
    "estado": "luminoso",
    "zona": "salon",
    "timestamp": "2025-01-25T10:30:47.234567"
}
payload_json = json.dumps(payload).encode()

mqtt_msg = b'\x30'
remaining_len = 2 + len(topic) + len(payload_json)
mqtt_msg += bytes([remaining_len])
mqtt_msg += struct.pack('!H', len(topic)) + topic.encode()
mqtt_msg += payload_json

eth = eth_header(BROKER_MAC, SENSOR_LUZ_MAC)
ip = ip_header(SENSOR_LUZ_IP, BROKER_IP, 6, 20 + len(mqtt_msg))
tcp = tcp_header(45679, MQTT_PORT, 3000, 4000, 0x18, 29200)

packet = eth + ip + tcp + mqtt_msg
pcap_data += crear_pcap_packet(timestamp, packet)
timestamp += 0.002

# ========================================
# 9. Más mensajes MQTT PUBLISH
# ========================================
for i in range(3):
    print(f"  [{9+i}] MQTT PUBLISH (temperatura {i+2})")
    topic = "casa/sensor/temperatura/salon"
    payload = {
        "sensor_id": "sensor_temp_salon",
        "tipo": "temperatura",
        "valor": 23.5 + (i * 0.2),
        "unidad": "°C",
        "zona": "salon",
        "timestamp": f"2025-01-25T10:3{1+i}:00.000000"
    }
    payload_json = json.dumps(payload).encode()

    mqtt_msg = b'\x30'
    remaining_len = 2 + len(topic) + len(payload_json)
    mqtt_msg += bytes([remaining_len])
    mqtt_msg += struct.pack('!H', len(topic)) + topic.encode()
    mqtt_msg += payload_json

    eth = eth_header(BROKER_MAC, SENSOR_TEMP_MAC)
    ip = ip_header(SENSOR_TEMP_IP, BROKER_IP, 6, 20 + len(mqtt_msg))
    tcp = tcp_header(45678, MQTT_PORT, 5000 + i*200, 6000 + i*200, 0x18, 29200)

    packet = eth + ip + tcp + mqtt_msg
    pcap_data += crear_pcap_packet(timestamp, packet)
    timestamp += 10.0

# Guardar archivo
output_file = 'capturas/captura.pcap'
with open(output_file, 'wb') as f:
    f.write(pcap_data)

print(f"\n✅ Archivo PCAP generado: {output_file}")
print(f"📊 Total de paquetes: 12")
print("\n🔍 Para abrir con Wireshark:")
print("   wireshark capturas/captura.pcap")
print("\n📌 Filtros útiles:")
print("   - tcp.port == 1883")
print("   - mqtt")
print("   - tcp.flags.syn == 1")
print("   - mqtt.msgtype == 3")
print("\n💡 Follow TCP Stream para ver JSON en texto claro")
