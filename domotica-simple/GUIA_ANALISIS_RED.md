# Guía de Análisis de Red con Wireshark

## 📋 Contenido

1. [Introducción](#introducción)
2. [Requisitos previos](#requisitos-previos)
3. [Inicio rápido](#inicio-rápido)
4. [Scripts disponibles](#scripts-disponibles)
5. [Captura de tráfico](#captura-de-tráfico)
6. [Análisis con Wireshark](#análisis-con-wireshark)
7. [Ejemplos prácticos](#ejemplos-prácticos)
8. [Filtros útiles de Wireshark](#filtros-útiles-de-wireshark)

## 🎯 Introducción

Esta guía proporciona instrucciones detalladas para capturar y analizar el tráfico de red del sistema domótico, con énfasis en las **capas bajas del modelo OSI** (capas 2, 3 y 4):

- **Capa 2 (Enlace de datos)**: Ethernet, direcciones MAC
- **Capa 3 (Red)**: IPv4, direcciones IP, enrutamiento
- **Capa 4 (Transporte)**: TCP (MQTT) y UDP (Alarma)

## ✅ Requisitos previos

1. **Docker y Docker Compose** instalados
2. **Wireshark** instalado en tu máquina local (descarga desde [wireshark.org](https://www.wireshark.org/))
3. Sistema domótico desplegado y en ejecución

## 🚀 Inicio rápido

### Paso 1: Iniciar el sistema

```bash
cd domotica-simple
docker-compose up -d
```

### Paso 2: Verificar que el contenedor de análisis está activo

```bash
docker ps | grep network-analyzer
```

Deberías ver:
```
network-analyzer   172.28.0.200   ...
```

### Paso 3: Acceder al contenedor de análisis

```bash
docker exec -it network-analyzer bash
```

### Paso 4: Ejecutar una captura de prueba

Dentro del contenedor:
```bash
cd /scripts
./capturar_mqtt.sh 30
```

Esto capturará tráfico MQTT durante 30 segundos.

## 📜 Scripts disponibles

Todos los scripts están en el directorio `/scripts` dentro del contenedor `network-analyzer`:

### 1. `capturar_mqtt.sh`

Captura tráfico del protocolo MQTT (TCP puerto 1883).

**Uso:**
```bash
./capturar_mqtt.sh [duración_en_segundos]
```

**Ejemplo:**
```bash
./capturar_mqtt.sh 60  # Captura durante 60 segundos
```

**Análisis:**
- Protocolo TCP
- Puerto 1883
- Mensajes MQTT (CONNECT, PUBLISH, SUBSCRIBE, etc.)
- Comunicación entre sensores/actuadores y broker

### 2. `capturar_udp_alarma.sh`

Captura tráfico del sistema de alarma (UDP puerto 9999).

**Uso:**
```bash
./capturar_udp_alarma.sh [duración_en_segundos]
```

**Ejemplo:**
```bash
./capturar_udp_alarma.sh 60  # Captura durante 60 segundos
```

**Análisis:**
- Protocolo UDP
- Puerto 9999
- Mensajes de sensores de alarma (JSON en payload)
- Sin establecimiento de conexión

### 3. `capturar_todo.sh`

Captura TODO el tráfico de la red domótica (172.28.0.0/16).

**Uso:**
```bash
./capturar_todo.sh [duración_en_segundos]
```

**Ejemplo:**
```bash
./capturar_todo.sh 120  # Captura durante 2 minutos
```

**Análisis:**
- Todo el tráfico de la red Docker
- TCP, UDP, ICMP, ARP
- Todos los dispositivos IoT
- Análisis completo de protocolos

### 4. `analizar_capas_osi.sh`

Analiza un archivo PCAP y genera un informe detallado de las capas OSI.

**Uso:**
```bash
./analizar_capas_osi.sh <archivo.pcap>
```

**Ejemplo:**
```bash
./analizar_capas_osi.sh /capturas/mqtt_tcp_20250123_120000.pcap
```

**Genera:**
- Análisis de Capa 2 (Ethernet): direcciones MAC, tipos de frame
- Análisis de Capa 3 (IP): direcciones IP, TTL, fragmentación
- Análisis de Capa 4 (TCP/UDP): puertos, flags, ventanas, checksums
- Análisis de Capa 7 (MQTT): tipos de mensajes, tópicos, QoS

## 📡 Captura de tráfico

### Escenario 1: Analizar comunicación MQTT

**Objetivo:** Capturar y analizar la comunicación entre un sensor de temperatura y el broker MQTT.

```bash
# 1. Acceder al contenedor
docker exec -it network-analyzer bash

# 2. Iniciar captura (60 segundos)
cd /scripts
./capturar_mqtt.sh 60

# 3. Mientras captura, los sensores estarán enviando datos automáticamente

# 4. Al finalizar, copiar el archivo a tu máquina
exit
docker cp network-analyzer:/capturas/mqtt_tcp_XXXXXXXX.pcap .
```

### Escenario 2: Analizar sistema de alarma UDP

**Objetivo:** Capturar mensajes UDP del sistema de alarma.

```bash
# 1. Acceder al contenedor
docker exec -it network-analyzer bash

# 2. Iniciar captura
cd /scripts
./capturar_udp_alarma.sh 60

# 3. En otra terminal, activar la alarma para generar tráfico
docker exec -it scada-central bash
# Luego usar el dashboard web o enviar comandos MQTT

# 4. Copiar archivo capturado
exit
docker cp network-analyzer:/capturas/udp_alarma_XXXXXXXX.pcap .
```

### Escenario 3: Captura completa del sistema

**Objetivo:** Análisis exhaustivo de toda la red domótica.

```bash
# 1. Acceder al contenedor
docker exec -it network-analyzer bash

# 2. Captura completa (2 minutos)
cd /scripts
./capturar_todo.sh 120

# 3. Analizar con el script de capas OSI
./analizar_capas_osi.sh /capturas/red_completa_XXXXXXXX.pcap

# 4. Copiar archivos generados
exit
docker cp network-analyzer:/capturas/ ./capturas_analisis/
```

## 🔍 Análisis con Wireshark

### Abrir archivo PCAP

1. Abrir Wireshark
2. File → Open
3. Seleccionar el archivo `.pcap` copiado

### Vista recomendada

**Configurar columnas:**
1. View → Time Display Format → Seconds Since Beginning of Capture
2. Edit → Preferences → Appearance → Columns
3. Añadir columnas personalizadas:
   - Source Port: `%Cus:tcp.srcport:0:R`
   - Dest Port: `%Cus:tcp.dstport:0:R`
   - MQTT Topic: `%Cus:mqtt.topic:0:R`

### Analizar Capa 2 (Ethernet)

**Ver direcciones MAC:**
```
Frame → Ethernet II → Source / Destination
```

**Filtro para analizar capa 2:**
```
eth
```

### Analizar Capa 3 (IP)

**Ver cabecera IP:**
```
Frame → Internet Protocol Version 4
```

**Información relevante:**
- Version: 4
- Header Length: 20 bytes (típicamente)
- TTL: 64 (valor común en Linux)
- Protocol: 6 (TCP) o 17 (UDP)
- Source/Destination IP

**Filtro para IPs específicas:**
```
ip.addr == 172.28.0.10  # Broker MQTT
ip.src == 172.28.0.111  # Sensor temperatura salón
```

### Analizar Capa 4 (TCP)

**Ver cabecera TCP:**
```
Frame → Transmission Control Protocol
```

**Información relevante:**
- Source/Destination Port
- Sequence Number
- Acknowledgment Number
- Flags (SYN, ACK, FIN, PSH)
- Window Size
- Checksum

**Analizar 3-way handshake:**

1. Filtro: `tcp.flags.syn == 1`
2. Buscar secuencia:
   - Paquete 1: SYN (syn=1, ack=0)
   - Paquete 2: SYN-ACK (syn=1, ack=1)
   - Paquete 3: ACK (syn=0, ack=1)

**Follow TCP Stream:**
```
Click derecho en paquete → Follow → TCP Stream
```

### Analizar Capa 4 (UDP)

**Ver cabecera UDP:**
```
Frame → User Datagram Protocol
```

**Información relevante:**
- Source/Destination Port (9999 para alarma)
- Length
- Checksum

**Ver payload JSON:**
```
Click en paquete → Data → Texto en ASCII
```

### Analizar MQTT (Capa 7)

**Ver mensajes MQTT:**
```
Frame → MQ Telemetry Transport Protocol
```

**Filtrar por tipo de mensaje:**
```
mqtt.msgtype == 1   # CONNECT
mqtt.msgtype == 3   # PUBLISH
mqtt.msgtype == 8   # SUBSCRIBE
```

**Ver tópicos:**
```
MQTT → Topic
```

## 💡 Ejemplos prácticos

### Ejemplo 1: Verificar que MQTT usa TCP

1. Capturar tráfico MQTT
2. Aplicar filtro: `tcp.port == 1883`
3. Observar:
   - **3-way handshake** (SYN, SYN-ACK, ACK)
   - **Números de secuencia** incrementales
   - **ACKs** confirmando recepción
   - **Retransmisiones** si hay pérdida de paquetes

**Conclusión:** MQTT opera sobre TCP, garantizando entrega fiable.

### Ejemplo 2: Verificar que Alarma usa UDP

1. Capturar tráfico de alarma
2. Aplicar filtro: `udp.port == 9999`
3. Observar:
   - **No hay handshake** (sin SYN, SYN-ACK)
   - **Envío directo** de datagramas
   - **No hay ACKs**
   - **Payload JSON** visible directamente

**Conclusión:** Sistema de alarma usa UDP para baja latencia.

### Ejemplo 3: Analizar seguridad del tráfico

1. Capturar tráfico MQTT
2. Follow TCP Stream
3. Observar que el **contenido está en texto claro**:
   ```json
   {"sensor_id": "sensor_temp_salon", "valor": 23.5, ...}
   ```

**Conclusión:** **Vulnerabilidad crítica** - tráfico sin cifrar.

### Ejemplo 4: Identificar dispositivos por IP

1. Aplicar filtro: `ip.addr == 172.28.0.0/16`
2. Statistics → Endpoints → IPv4
3. Ver tabla de dispositivos:

| IP | Descripción |
|----|-------------|
| 172.28.0.10 | MQTT Broker |
| 172.28.0.101 | Sensor Luz Salón |
| 172.28.0.111 | Sensor Temp Salón |
| 172.28.0.121 | Actuador Luces |
| 172.28.0.151 | Alarm Server |
| 172.28.0.200 | Network Analyzer |

## 🎯 Filtros útiles de Wireshark

### Filtros básicos

```bash
# Todo el tráfico MQTT
tcp.port == 1883
mqtt

# Tráfico UDP de alarma
udp.port == 9999

# Tráfico de un dispositivo específico
ip.addr == 172.28.0.111

# Solo mensajes PUBLISH de MQTT
mqtt.msgtype == 3

# Tópicos específicos
mqtt.topic contains "temperatura"
mqtt.topic == "casa/sensor/temperatura/salon"

# Paquetes con payload JSON
data contains "sensor_id"
```

### Filtros de capa de transporte

```bash
# Conexiones TCP (SYN)
tcp.flags.syn == 1 && tcp.flags.ack == 0

# Retransmisiones TCP
tcp.analysis.retransmission

# Paquetes con datos (no solo ACK)
tcp.len > 0

# UDP con longitud específica
udp.length > 100
```

### Filtros de capa de red

```bash
# Tráfico entre dos IPs
ip.src == 172.28.0.111 && ip.dst == 172.28.0.10

# TTL específico
ip.ttl == 64

# Fragmentación IP
ip.flags.mf == 1
```

### Filtros avanzados

```bash
# MQTT PUBLISH con QoS 1
mqtt.msgtype == 3 && mqtt.qos == 1

# Combinación TCP y MQTT
tcp.port == 1883 && mqtt

# Paquetes grandes
frame.len > 500

# Estadísticas por conversación
tcp.stream eq 0
```

## 📊 Generar estadísticas

### Desde Wireshark GUI

**Jerarquía de protocolos:**
```
Statistics → Protocol Hierarchy
```

**Conversaciones:**
```
Statistics → Conversations → IPv4 / TCP / UDP
```

**Endpoints:**
```
Statistics → Endpoints → IPv4
```

**Gráficos de I/O:**
```
Statistics → I/O Graph
```

### Desde línea de comandos (tshark)

```bash
# Jerarquía de protocolos
tshark -r captura.pcap -q -z io,phs

# Conversaciones TCP
tshark -r captura.pcap -q -z conv,tcp

# Tópicos MQTT
tshark -r captura.pcap -Y "mqtt.topic" -T fields -e mqtt.topic | sort | uniq -c
```

## 📝 Documentar hallazgos

### Plantilla de análisis

Para cada captura, documentar:

1. **Información básica:**
   - Fecha y hora de captura
   - Duración
   - Total de paquetes capturados

2. **Capa 2 (Enlace de datos):**
   - Direcciones MAC origen/destino
   - Tipos de frame Ethernet

3. **Capa 3 (Red):**
   - Rango de IPs utilizadas
   - Dispositivos identificados
   - TTL observado

4. **Capa 4 (Transporte):**
   - Protocolos utilizados (TCP/UDP)
   - Puertos abiertos
   - Análisis de handshakes
   - Retransmisiones detectadas

5. **Vulnerabilidades encontradas:**
   - Tráfico sin cifrar
   - Puertos expuestos
   - Autenticación débil

6. **Capturas de pantalla:**
   - Handshake TCP
   - Payload JSON visible
   - Jerarquía de protocolos

## 🔒 Aspectos de seguridad a analizar

### Vulnerabilidades del protocolo

- [ ] Tráfico MQTT en texto claro (puerto 1883)
- [ ] Mensajes UDP sin autenticación
- [ ] Payloads JSON legibles
- [ ] Puertos predecibles

### Ataques posibles

- [ ] **Sniffing:** Capturar credenciales y datos
- [ ] **Man-in-the-Middle:** Interceptar y modificar mensajes
- [ ] **Replay Attack:** Reenviar paquetes UDP capturados
- [ ] **DoS:** Saturar puertos 1883 o 9999

### Mitigaciones recomendadas

- [ ] Implementar TLS para MQTT (puerto 8883)
- [ ] Autenticación con certificados X.509
- [ ] Cifrado de payloads JSON
- [ ] VLANs para segmentar red IoT

## 📚 Recursos adicionales

- [Documentación oficial de Wireshark](https://www.wireshark.org/docs/)
- [MQTT Protocol Specification](https://mqtt.org/mqtt-specification/)
- [Modelo OSI - Wikipedia](https://es.wikipedia.org/wiki/Modelo_OSI)
- [RFC 793 - TCP](https://tools.ietf.org/html/rfc793)
- [RFC 768 - UDP](https://tools.ietf.org/html/rfc768)

---

**Última actualización:** 2025-01-23
**Asignatura:** Ciberseguridad en Desarrollos Tecnológicos Innovadores
