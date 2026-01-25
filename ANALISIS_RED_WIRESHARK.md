# Análisis de Red TCP con Wireshark - Sistema Domótico

## 1. INTRODUCCIÓN

Este documento proporciona un análisis del protocolo **TCP** utilizado en el sistema domótico mediante **MQTT**, con énfasis en las **capas bajas del modelo OSI** (capas 2, 3 y 4).

El sistema utiliza **ÚNICAMENTE TCP** como protocolo de transporte, lo cual garantiza:
- ✅ Comunicación fiable entre dispositivos
- ✅ Entrega garantizada de mensajes
- ✅ Control de flujo y congestión
- ✅ Orden secuencial de paquetes

## 2. MODELO OSI IMPLEMENTADO

### 2.1 Capas del Sistema

```
┌──────────────────────────────────────────────────────┐
│ Capa 7 - Aplicación    │ MQTT, HTTP, JSON            │
├──────────────────────────────────────────────────────┤
│ Capa 6 - Presentación  │ JSON, UTF-8                 │
├──────────────────────────────────────────────────────┤
│ Capa 5 - Sesión        │ Sesiones MQTT persistentes  │
├──────────────────────────────────────────────────────┤
│ Capa 4 - Transporte    │ TCP (Puerto 1883, 8080)    │ ⬅ FOCO
├──────────────────────────────────────────────────────┤
│ Capa 3 - Red           │ IPv4 (172.28.0.0/16)       │ ⬅ FOCO
├──────────────────────────────────────────────────────┤
│ Capa 2 - Enlace Datos  │ Ethernet (Docker bridge)   │ ⬅ FOCO
├──────────────────────────────────────────────────────┤
│ Capa 1 - Física        │ Interfaz virtual           │
└──────────────────────────────────────────────────────┘
```

### 2.2 Topología de Red

```
Red: 172.28.0.0/16 (Capa 3)
Protocolo: TCP (Capa 4)
Aplicación: MQTT (Capa 7)

                    MQTT Broker
                   172.28.0.10:1883
                        (TCP)
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    Sensores        Actuadores        SCADA
   (TCP/MQTT)      (TCP/MQTT)      (TCP/MQTT)
  172.28.0.101    172.28.0.121    172.28.0.100
  172.28.0.102    172.28.0.131
  172.28.0.111
```

## 3. PROTOCOLO TCP (Transmission Control Protocol)

### 3.1 Características de TCP

El sistema utiliza **TCP exclusivamente** porque:

| Característica | Descripción |
|----------------|-------------|
| **Orientado a conexión** | Establece sesión mediante 3-way handshake |
| **Fiable** | Garantiza entrega con ACK y retransmisión |
| **Ordenado** | Números de secuencia mantienen orden |
| **Control de flujo** | Ventana deslizante regula velocidad |
| **Control de errores** | Checksums detectan corrupción |

### 3.2 Estructura del Segmento TCP

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Puerto Origen        |       Puerto Destino (1883)   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Número de Secuencia                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                 Número de Acuse de Recibo (ACK)               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Offset|Res|Flags (SYN,ACK,PSH,FIN)|      Ventana             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|           Checksum            |         Puntero Urgente       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Opciones (opcional)                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                     DATOS (MQTT)                              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### 3.3 3-Way Handshake (Establecimiento de Conexión)

**Cada vez que un sensor se conecta al broker MQTT, ocurre este proceso:**

```
Sensor (172.28.0.111)              Broker MQTT (172.28.0.10:1883)
        │                                    │
        │─────── SYN (seq=x) ───────────────>│  Paquete 1
        │                                    │
        │<────── SYN-ACK (seq=y, ack=x+1) ───│  Paquete 2
        │                                    │
        │─────── ACK (ack=y+1) ──────────────>│  Paquete 3
        │                                    │
        │    ✅ CONEXIÓN TCP ESTABLECIDA      │
        │                                    │
        │─────── MQTT CONNECT ───────────────>│  Paquete 4
        │                                    │
        │<────── MQTT CONNACK ───────────────│  Paquete 5
```

**Flags TCP importantes:**
- **SYN** (Synchronize): Inicia conexión
- **ACK** (Acknowledge): Confirma recepción
- **PSH** (Push): Datos para aplicación inmediatamente
- **FIN** (Finish): Cierra conexión

### 3.4 Flujo Completo MQTT sobre TCP

```
Sensor Temp               MQTT Broker              Actuador Luces
   │                           │                          │
   │──── TCP SYN ─────────────>│                          │
   │<─── TCP SYN-ACK ──────────│                          │
   │──── TCP ACK ─────────────>│                          │
   │                           │                          │
   │──── MQTT CONNECT ────────>│                          │
   │<─── MQTT CONNACK ─────────│                          │
   │                           │<──── MQTT SUBSCRIBE ─────│
   │                           │      (casa/sensor/temp/#)│
   │                           │──── MQTT SUBACK ────────>│
   │                           │                          │
   │─── MQTT PUBLISH ─────────>│                          │
   │    casa/sensor/temp/salon │                          │
   │    {"valor": 23.5}        │                          │
   │<──── TCP ACK ─────────────│                          │
   │                           │                          │
   │                           │──── MQTT PUBLISH ───────>│
   │                           │     casa/sensor/temp/salon│
   │                           │<──── TCP ACK ────────────│
```

## 4. MQTT SOBRE TCP

### 4.1 Por qué MQTT usa TCP

MQTT requiere TCP porque:

1. **Mensajes no pueden perderse** - Los comandos de control deben llegar
2. **Orden importa** - Los eventos deben procesarse en secuencia
3. **QoS niveles** - Quality of Service 1 y 2 requieren ACKs
4. **Sesiones persistentes** - Mantiene estado entre cliente y broker

### 4.2 Puertos TCP Utilizados

| Puerto | Protocolo | Uso |
|--------|-----------|-----|
| **1883** | MQTT | Comunicación con sensores/actuadores |
| **8080** | WebSocket | Dashboard web |

### 4.3 Tipos de Mensajes MQTT

| Tipo | Código | Descripción | Requiere ACK TCP |
|------|--------|-------------|------------------|
| CONNECT | 1 | Cliente se conecta | Sí |
| CONNACK | 2 | Broker acepta conexión | Sí |
| PUBLISH | 3 | Publicar mensaje | Sí |
| PUBACK | 4 | Confirmar PUBLISH (QoS 1) | Sí |
| SUBSCRIBE | 8 | Suscribirse a tópico | Sí |
| SUBACK | 9 | Confirmar suscripción | Sí |
| PINGREQ | 12 | Mantener conexión viva | Sí |
| PINGRESP | 13 | Respuesta a ping | Sí |

**Todos los mensajes MQTT viajan sobre TCP**, garantizando entrega.

## 5. CAPTURA Y ANÁLISIS CON WIRESHARK

### 5.1 Comandos de Captura

**Capturar tráfico TCP/MQTT:**
```bash
docker exec -it network-analyzer bash
cd /scripts
./capturar_mqtt.sh 60  # 60 segundos de captura
```

**Captura completa de red:**
```bash
./capturar_todo.sh 120  # 2 minutos
```

**Analizar capas OSI:**
```bash
./analizar_capas_osi.sh /capturas/mqtt_tcp_*.pcap
```

### 5.2 Filtros de Wireshark

**Filtros básicos:**
```
tcp.port == 1883          # Todo el tráfico MQTT
mqtt                       # Solo mensajes MQTT
tcp.flags.syn == 1        # Inicios de conexión (SYN)
tcp.flags.syn == 1 && tcp.flags.ack == 0  # Solo SYN (handshake paso 1)
```

**Filtros avanzados:**
```
mqtt.msgtype == 3         # Solo PUBLISH
mqtt.msgtype == 1         # Solo CONNECT
tcp.len > 0               # Solo segmentos con datos
tcp.analysis.retransmission  # Retransmisiones
```

**Follow TCP Stream:**
```
Click derecho en paquete → Follow → TCP Stream
```
Esto muestra toda la conversación TCP, **incluyendo el contenido MQTT en texto claro**.

### 5.3 Ejemplo de Captura TCP - 3-way Handshake

```
═══════════════════════════════════════════════════════════
Frame 1: Sensor → Broker (SYN)
═══════════════════════════════════════════════════════════
Ethernet II
  Destination: 02:42:ac:1c:00:0a (broker)
  Source:      02:42:ac:1c:00:6f (sensor)
  Type:        IPv4 (0x0800)

Internet Protocol Version 4
  Source:      172.28.0.111 (sensor-temp-salon)
  Destination: 172.28.0.10 (mqtt-broker)
  Protocol:    TCP (6)
  TTL:         64

Transmission Control Protocol
  Source Port:      45678
  Destination Port: 1883 (mqtt)
  Flags:            SYN ← INICIA CONEXIÓN
  Sequence Number:  0 (relative)
  Window Size:      29200

═══════════════════════════════════════════════════════════
Frame 2: Broker → Sensor (SYN-ACK)
═══════════════════════════════════════════════════════════
TCP
  Source Port:      1883
  Destination Port: 45678
  Flags:            SYN, ACK ← ACEPTA CONEXIÓN
  Sequence Number:  0
  Acknowledgment:   1 ← CONFIRMA RECEPCIÓN DEL SYN

═══════════════════════════════════════════════════════════
Frame 3: Sensor → Broker (ACK)
═══════════════════════════════════════════════════════════
TCP
  Flags:            ACK ← CONFIRMA RECEPCIÓN DEL SYN-ACK
  Acknowledgment:   1

✅ CONEXIÓN TCP ESTABLECIDA
═══════════════════════════════════════════════════════════
```

### 5.4 Ejemplo de Captura - Mensaje MQTT PUBLISH

```
═══════════════════════════════════════════════════════════
Frame 15: Sensor publica temperatura
═══════════════════════════════════════════════════════════
CAPA 2 - Ethernet
  Source: 02:42:ac:1c:00:6f
  Dest:   02:42:ac:1c:00:0a

CAPA 3 - IP
  Source:      172.28.0.111
  Destination: 172.28.0.10
  Protocol:    TCP (6)

CAPA 4 - TCP
  Source Port: 45678
  Dest Port:   1883
  Flags:       PSH, ACK ← DATOS PARA APLICACIÓN
  Seq:         1234
  Ack:         5678
  Payload:     180 bytes

CAPA 7 - MQTT
  Message Type: PUBLISH (3)
  QoS Level:    0 (At most once)
  Topic:        casa/sensor/temperatura/salon
  Payload:
  {
    "sensor_id": "sensor_temp_salon",
    "tipo": "temperatura",
    "valor": 23.5,
    "unidad": "°C",
    "zona": "salon",
    "timestamp": "2025-01-23T10:30:45.123456"
  }

⚠️ VULNERABILIDAD: Payload visible en texto claro
═══════════════════════════════════════════════════════════
```

## 6. ANÁLISIS DE CAPAS OSI

### Capa 2 - Enlace de Datos (Ethernet)

**Información visible:**
- Direcciones MAC de contenedores Docker
- Tipo de frame: IPv4 (0x0800)
- Tamaños de frame (14 bytes de cabecera)

**Comando tshark:**
```bash
tshark -r captura.pcap -T fields -e eth.src -e eth.dst -e eth.type
```

### Capa 3 - Red (IP)

**Información visible:**
- Red: 172.28.0.0/16
- IPs de dispositivos
- TTL: 64 (típico de Linux)
- Protocolo: TCP (6)
- Fragmentación: Don't Fragment (DF)

**Comando tshark:**
```bash
tshark -r captura.pcap -T fields -e ip.src -e ip.dst -e ip.proto -e ip.ttl
```

### Capa 4 - Transporte (TCP)

**Información visible:**
- Puertos: 1883 (MQTT), 8080 (WebSocket)
- Flags: SYN, ACK, PSH, FIN, RST
- Números de secuencia y ACK
- Ventana TCP (control de flujo)
- Checksums
- MSS (Maximum Segment Size): 1460 bytes

**Comando tshark:**
```bash
tshark -r captura.pcap -Y "tcp" \
  -T fields -e tcp.srcport -e tcp.dstport -e tcp.flags
```

## 7. VULNERABILIDADES DE TCP SIN CIFRAR

### 7.1 Problema Crítico: Tráfico en Texto Claro

**El sistema actual usa TCP sin TLS/SSL**, lo que significa:

❌ **Todo el tráfico MQTT es visible** con un simple sniff:
```bash
tcpdump -i eth0 -A 'tcp port 1883'
```

❌ **Datos expuestos:**
- Valores de sensores (temperaturas, luz)
- Comandos a actuadores (encender luces, subir persianas)
- Tópicos MQTT (estructura del sistema)
- Client IDs (identificación de dispositivos)

### 7.2 Demostración de Sniffing

**Atacante captura tráfico:**
```
10:30:45 IP 172.28.0.111.45678 > 172.28.0.10.1883: Flags [P.]
MQTT PUBLISH casa/sensor/temperatura/salon
{"sensor_id":"sensor_temp_salon","valor":23.5,"zona":"salon"}
```

**Información obtenida:**
- Hay un sensor de temperatura en el salón
- La temperatura actual es 23.5°C
- El tópico MQTT es predecible
- No hay autenticación visible

### 7.3 Mitigación: TLS/SSL

**Para proteger el tráfico TCP, implementar TLS:**

```conf
# mosquitto.conf
listener 8883
protocol mqtt
cafile /etc/mosquitto/ca.crt
certfile /etc/mosquitto/server.crt
keyfile /etc/mosquitto/server.key
require_certificate true
tls_version tlsv1.2
```

**Con TLS, Wireshark mostrará:**
```
Application Data (encrypted)
```

En lugar de JSON legible.

## 8. ESTADÍSTICAS DEL TRÁFICO TCP

### 8.1 Volumen por Sensor

**Cada mensaje MQTT sobre TCP:**
- Ethernet: 14 bytes
- IP: 20 bytes
- TCP: 20 bytes (mínimo)
- MQTT header: ~5 bytes
- Topic: ~30 bytes
- JSON payload: ~150 bytes
**Total: ~239 bytes por mensaje**

**Frecuencia: 1 mensaje cada 10 segundos**
- 6 mensajes/minuto × 239 bytes = 1,434 bytes/min
- 86 KB/hora por sensor
- **~2 MB/día por sensor**

### 8.2 Overhead de TCP

| Componente | Bytes | % del total |
|------------|-------|-------------|
| Ethernet | 14 | 5.9% |
| IP | 20 | 8.4% |
| **TCP** | **20** | **8.4%** |
| MQTT | 35 | 14.6% |
| Payload | 150 | 62.7% |
| **Total** | **239** | **100%** |

**TCP overhead: 8.4%** - Aceptable para garantizar fiabilidad

## 9. CONCLUSIONES

### Protocolo Confirmado: TCP

✅ **El sistema usa ÚNICAMENTE TCP** como protocolo de transporte

**Evidencias:**
1. **3-way handshake** visible en todas las conexiones
2. **Flags TCP** (SYN, ACK, PSH, FIN) en todos los paquetes
3. **Números de secuencia** y ACKs confirmando entrega
4. **Puerto 1883** (MQTT estándar sobre TCP)
5. **Retransmisiones TCP** cuando hay pérdida de paquetes

### Ventajas de TCP para IoT Domótico

✅ **Fiabilidad:** Comandos críticos no se pierden
✅ **Orden:** Eventos se procesan en secuencia
✅ **QoS:** MQTT puede implementar niveles de servicio
✅ **Sesiones persistentes:** Reconexión automática

### Vulnerabilidad Crítica

❌ **Tráfico sin cifrar** - Datos legibles con Wireshark
❌ **Autenticación débil** - `allow_anonymous: true`
❌ **Puerto predecible** - 1883 es estándar MQTT

### Recomendación

🔒 **Implementar TLS/SSL** para cifrar todo el tráfico TCP

---

**Asignatura:** Ciberseguridad en Desarrollos Tecnológicos Innovadores
**Enfoque:** Análisis de capas OSI 2, 3, 4 con énfasis en TCP
**Herramientas:** Wireshark, tcpdump, tshark
**Protocolo:** TCP (Transmission Control Protocol)
