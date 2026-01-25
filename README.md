# 🏠 Sistema Domótico con Análisis TCP - Wireshark

## 📚 Documentación del Proyecto

Sistema domótico que utiliza **SOLO TCP** para comunicación, con análisis completo de protocolos de red enfocado en las **capas bajas del modelo OSI** (capas 2, 3 y 4).

### 📄 Documentos Principales

1. **[ANALISIS_RED_WIRESHARK.md](./ANALISIS_RED_WIRESHARK.md)** - Análisis técnico de TCP
   - Modelo OSI aplicado al sistema
   - Protocolo TCP en detalle
   - MQTT sobre TCP
   - Comandos de captura tcpdump/tshark

2. **[GUIA_SNIFFING_WIRESHARK.md](./GUIA_SNIFFING_WIRESHARK.md)** - Guía práctica paso a paso
   - Cómo capturar tráfico TCP
   - Cómo abrir archivos .pcap con Wireshark
   - Filtros útiles
   - Capturas para el informe
   - Demostración de vulnerabilidad (sniffing)

3. **[Guía de Análisis](./domotica-simple/GUIA_ANALISIS_RED.md)** - Scripts y herramientas
   - Scripts de captura automatizados
   - Análisis de capas OSI
   - Ejemplos prácticos

---

## 🎯 Protocolo Utilizado

### ✅ TCP (Transmission Control Protocol)

El sistema utiliza **ÚNICAMENTE TCP** como protocolo de transporte:

| Característica | TCP |
|----------------|-----|
| **Puerto** | 1883 (MQTT), 8080 (WebSocket) |
| **Orientado a conexión** | Sí (3-way handshake) |
| **Fiable** | Sí (ACK, retransmisión) |
| **Ordenado** | Sí (números de secuencia) |
| **Control de flujo** | Sí (ventana deslizante) |
| **Uso** | Sensores, actuadores, dashboard |

**NO se usa UDP en este sistema.**

---

## 🏗️ Arquitectura del Sistema

### Topología de Red

```
Red Docker: 172.28.0.0/16 (Capa 3 - IPv4)
Protocolo: TCP (Capa 4)
Aplicación: MQTT (Capa 7)

┌─────────────────────────────────────────────┐
│        MQTT Broker (172.28.0.10)            │
│        Puerto 1883/TCP                      │
│        Protocolo: MQTT sobre TCP            │
└──────────────┬──────────────────────────────┘
               │ (Todas las conexiones son TCP)
       ┌───────┼───────┬───────────┐
       │       │       │           │
   Sensores  Actuadores  SCADA  Analyzer
   (TCP)     (TCP)     (TCP)    (TCP)
  .101      .121      .100      .200
  .102      .131
  .111
```

### Dispositivos

| Dispositivo | IP | Puerto TCP | Función |
|-------------|--------|------------|---------|
| **mqtt-broker** | 172.28.0.10 | 1883 | Broker MQTT |
| sensor-luz-salon | 172.28.0.101 | 1883 | Publica datos de luz |
| sensor-luz-cocina | 172.28.0.102 | 1883 | Publica datos de luz |
| sensor-temp-salon | 172.28.0.111 | 1883 | Publica temperatura |
| actuador-luces-salon | 172.28.0.121 | 1883 | Controla luces |
| actuador-persianas | 172.28.0.131 | 1883 | Controla persianas |
| scada-central | 172.28.0.100 | 1883, 8081 | Dashboard y API |
| **network-analyzer** | 172.28.0.200 | N/A | Captura de tráfico |

**Todos usan TCP puerto 1883** para MQTT.

---

## 🚀 Inicio Rápido

### 1. Levantar el sistema

```bash
cd domotica-simple
docker-compose up -d
```

### 2. Verificar contenedores

```bash
docker ps
```

### 3. Capturar tráfico TCP

```bash
# Acceder al contenedor de análisis
docker exec -it network-analyzer bash

# Capturar 60 segundos de tráfico TCP
cd /scripts
./capturar_mqtt.sh 60
```

### 4. Copiar capturas a tu máquina

```bash
# Salir del contenedor
exit

# Copiar archivos .pcap
docker cp network-analyzer:/capturas/ ./capturas/
```

### 5. Abrir con Wireshark

```bash
wireshark capturas/mqtt_tcp_*.pcap
```

**Filtro recomendado:**
```
tcp.port == 1883
```

---

## 🔍 Análisis con Wireshark

### Confirmar que se usa TCP

**Filtro:**
```
tcp.flags.syn == 1 && tcp.flags.ack == 0
```

**Resultado:**
Verás los paquetes **SYN** del 3-way handshake TCP.

### Ver mensajes MQTT

**Filtro:**
```
mqtt
```

**Resultado:**
Solo mensajes MQTT (CONNECT, PUBLISH, SUBSCRIBE, etc.)

### Ver datos en texto claro (vulnerabilidad)

1. Click derecho en cualquier paquete MQTT
2. **Follow → TCP Stream**

**Resultado:**
Verás el JSON completo en texto claro:
```json
{"sensor_id":"sensor_temp_salon","valor":23.5,"zona":"salon"}
```

---

## 📊 Capas OSI Analizadas

### Capa 2 - Enlace de Datos (Ethernet)

```
Destination MAC: 02:42:ac:1c:00:0a (broker)
Source MAC:      02:42:ac:1c:00:6f (sensor)
Type:            IPv4 (0x0800)
```

### Capa 3 - Red (IP)

```
Source IP:      172.28.0.111 (sensor-temp-salon)
Destination IP: 172.28.0.10 (mqtt-broker)
Protocol:       TCP (6)
TTL:            64
```

### Capa 4 - Transporte (TCP)

```
Source Port:      45678 (efímero)
Destination Port: 1883 (MQTT)
Flags:            SYN, ACK, PSH, FIN
Sequence Number:  1234 (ejemplo)
Acknowledgment:   5678 (ejemplo)
Window Size:      29200 bytes
```

**Evidencias de TCP:**
- ✅ 3-way handshake (SYN, SYN-ACK, ACK)
- ✅ Números de secuencia y ACK
- ✅ Control de flujo con ventana
- ✅ Flags TCP en todos los paquetes
- ✅ Puerto 1883 (MQTT estándar sobre TCP)

---

## 🛠️ Scripts Disponibles

Ubicación: `domotica-simple/scripts/`

### capturar_mqtt.sh
Captura tráfico TCP del puerto 1883 (MQTT)

```bash
./capturar_mqtt.sh 60  # 60 segundos
```

**Genera:**
- `mqtt_tcp_YYYYMMDD_HHMMSS.pcap`
- `mqtt_tcp_YYYYMMDD_HHMMSS_analisis.txt`

### capturar_todo.sh
Captura todo el tráfico TCP de la red

```bash
./capturar_todo.sh 120  # 120 segundos
```

**Genera:**
- `mqtt_red_completa_YYYYMMDD_HHMMSS.pcap`
- `mqtt_red_completa_YYYYMMDD_HHMMSS_informe.txt`

### analizar_capas_osi.sh
Analiza capas OSI de un archivo .pcap

```bash
./analizar_capas_osi.sh /capturas/archivo.pcap
```

**Genera:**
- Análisis de Capa 2 (Ethernet)
- Análisis de Capa 3 (IP)
- Análisis de Capa 4 (TCP)
- Análisis de Capa 7 (MQTT)
- Confirmación de protocolo TCP

---

## 🔒 Vulnerabilidades Identificadas

### 1. Tráfico TCP sin Cifrar (CRÍTICA)

**Problema:**
- MQTT usa puerto 1883 sin TLS/SSL
- Todo el tráfico TCP está en **texto claro**
- Wireshark puede leer todos los mensajes JSON

**Impacto:**
- Exposición de datos de sensores
- Comandos a actuadores visibles
- Estructura del sistema expuesta

**Evidencia:**
```bash
# Follow TCP Stream muestra:
{"sensor_id":"sensor_temp_salon","valor":23.5,"zona":"salon"}
```

**Mitigación:**
```conf
# Usar TLS/SSL (puerto 8883)
listener 8883
protocol mqtt
cafile /etc/mosquitto/ca.crt
certfile /etc/mosquitto/server.crt
keyfile /etc/mosquitto/server.key
tls_version tlsv1.2
```

### 2. Autenticación Débil (CRÍTICA)

**Problema:**
```conf
allow_anonymous true  # Cualquiera puede conectarse
```

**Mitigación:**
```conf
allow_anonymous false
password_file /etc/mosquitto/passwd
```

### 3. Puerto Predecible (MEDIA)

**Problema:**
- Puerto 1883 es estándar MQTT
- Fácil de escanear

**Mitigación:**
- Firewall con iptables
- VLANs para segmentación

---

## 📈 Estadísticas del Tráfico TCP

### Volumen de Datos

**Por mensaje:**
- Ethernet: 14 bytes
- IP: 20 bytes
- **TCP**: **20 bytes**
- MQTT: ~35 bytes
- JSON payload: ~150 bytes
- **Total: ~239 bytes**

**Por sensor (cada 10 segundos):**
- 6 mensajes/minuto
- 360 mensajes/hora
- **86 KB/hora**
- **~2 MB/día**

### Overhead de TCP

TCP añade **20 bytes** por paquete (8.4% del total), pero garantiza:
- ✅ Entrega fiable
- ✅ Orden secuencial
- ✅ Control de flujo
- ✅ Detección de errores

---

## 📖 Guía Rápida para el Informe

### Paso 1: Leer Documentación

**Lee:** [ANALISIS_RED_WIRESHARK.md](./ANALISIS_RED_WIRESHARK.md)
- Teoría de TCP
- Modelo OSI aplicado
- Comandos de captura

### Paso 2: Capturar Tráfico

```bash
docker exec -it network-analyzer bash
cd /scripts
./capturar_todo.sh 120
```

### Paso 3: Analizar con Script

```bash
./analizar_capas_osi.sh /capturas/mqtt_red_completa_*.pcap
```

### Paso 4: Copiar a tu Máquina

```bash
exit
docker cp network-analyzer:/capturas/ ./
```

### Paso 5: Abrir con Wireshark

```bash
wireshark capturas/mqtt_red_completa_*.pcap
```

### Paso 6: Tomar Capturas

**Sigue la guía:** [GUIA_SNIFFING_WIRESHARK.md](./GUIA_SNIFFING_WIRESHARK.md)

**Capturas necesarias:**
1. 3-way handshake TCP
2. Mensaje MQTT PUBLISH
3. Follow TCP Stream (vulnerabilidad)
4. Protocol Hierarchy (confirma TCP 100%)

---

## 🎓 Conceptos Clave

### ¿Por qué TCP para MQTT?

✅ **Comandos críticos** no pueden perderse
✅ **Orden de eventos** debe mantenerse
✅ **QoS (Quality of Service)** requiere ACKs
✅ **Sesiones persistentes** con el broker

### 3-Way Handshake TCP

```
Sensor                  Broker
  │                       │
  │────── SYN ───────────>│  Paso 1
  │<──── SYN-ACK ─────────│  Paso 2
  │────── ACK ───────────>│  Paso 3
  │                       │
  │  Conexión establecida │
```

### Capas OSI

```
┌─────────────┬──────────────────────────┐
│ Capa 7      │ MQTT, JSON               │
├─────────────┼──────────────────────────┤
│ Capa 6      │ UTF-8                    │
├─────────────┼──────────────────────────┤
│ Capa 5      │ Sesiones MQTT            │
├─────────────┼──────────────────────────┤
│ Capa 4 ⭐   │ TCP (1883)              │ ← FOCO
├─────────────┼──────────────────────────┤
│ Capa 3 ⭐   │ IPv4 (172.28.0.0/16)    │ ← FOCO
├─────────────┼──────────────────────────┤
│ Capa 2 ⭐   │ Ethernet (bridge)       │ ← FOCO
├─────────────┼──────────────────────────┤
│ Capa 1      │ Interfaz virtual         │
└─────────────┴──────────────────────────┘
```

---

## 📚 Referencias

- **MQTT Specification:** https://mqtt.org/mqtt-specification/
- **RFC 793 (TCP):** https://tools.ietf.org/html/rfc793
- **Wireshark Documentation:** https://www.wireshark.org/docs/
- **OWASP IoT Top 10:** https://owasp.org/www-project-internet-of-things/

---

## 👨‍💻 Asignatura

**Ciberseguridad en Desarrollos Tecnológicos Innovadores**

**Enfoque:** Análisis de capas bajas del modelo OSI (2, 3, 4)
**Protocolo:** TCP (Transmission Control Protocol)
**Herramientas:** Wireshark, tcpdump, tshark

---

## ✅ Resumen Ejecutivo

| Aspecto | Valor |
|---------|-------|
| **Protocolo de transporte** | TCP únicamente |
| **Puerto** | 1883 (MQTT) |
| **Protocolo de aplicación** | MQTT |
| **Red** | 172.28.0.0/16 (IPv4) |
| **Vulnerabilidad principal** | Tráfico sin cifrar |
| **Evidencia** | Wireshark muestra JSON en claro |
| **Mitigación** | TLS/SSL (puerto 8883) |

---

## 🔥 Quick Start

```bash
# 1. Levantar sistema
cd domotica-simple && docker-compose up -d

# 2. Capturar tráfico TCP
docker exec -it network-analyzer bash
cd /scripts && ./capturar_mqtt.sh 60

# 3. Copiar archivos
exit
docker cp network-analyzer:/capturas/ ./evidencias/

# 4. Abrir con Wireshark
wireshark evidencias/mqtt_tcp_*.pcap

# 5. Aplicar filtro
# Filtro en Wireshark: tcp.port == 1883
```

**Protocolo confirmado: TCP ✅**

---

**✅ Sistema listo para análisis de red y sniffing con Wireshark**
