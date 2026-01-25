# Guía de Sniffing con Wireshark - Sistema Domótico TCP

## 🎯 Objetivo

Esta guía muestra cómo **capturar y analizar el tráfico TCP** del sistema domótico usando Wireshark, demostrando que el sistema usa **SOLO TCP** y que los datos viajan en texto claro (vulnerabilidad).

---

## 🚀 Paso 1: Levantar el Sistema

```bash
cd domotica-simple
docker-compose up -d
```

Verifica que los contenedores estén activos:
```bash
docker ps
```

Deberías ver:
- `mqtt-broker` (172.28.0.10) - Puerto TCP 1883
- `sensor-luz-salon`, `sensor-luz-cocina`, `sensor-temp-salon`
- `actuador-luces-salon`, `actuador-persianas`
- `network-analyzer` (172.28.0.200) - Herramienta de captura

---

## 📡 Paso 2: Capturar Tráfico TCP

### Opción A: Script Automático (Recomendado)

```bash
# Acceder al contenedor de análisis
docker exec -it network-analyzer bash

# Ejecutar captura de 60 segundos
cd /scripts
./capturar_mqtt.sh 60
```

Esto generará:
- `/capturas/mqtt_tcp_YYYYMMDD_HHMMSS.pcap`
- `/capturas/mqtt_tcp_YYYYMMDD_HHMMSS_analisis.txt`

### Opción B: Manual con tcpdump

```bash
docker exec -it network-analyzer bash
tcpdump -i eth0 -w /capturas/captura_manual.pcap 'tcp port 1883' -v -s 0
# Ctrl+C para detener después de 1-2 minutos
```

---

## 💻 Paso 3: Copiar Captura a tu Máquina

```bash
# Salir del contenedor (Ctrl+D)
exit

# Copiar archivos a tu máquina local
docker cp network-analyzer:/capturas/ ./capturas_wireshark/
```

Ahora tendrás los archivos `.pcap` en tu máquina local.

---

## 🔍 Paso 4: Abrir con Wireshark

1. **Abrir Wireshark** en tu máquina
2. **File → Open**
3. Seleccionar el archivo `.pcap`

---

## 📊 Paso 5: Análisis Básico

### Ver Todos los Paquetes TCP

Filtro:
```
tcp.port == 1883
```

Resultado: Verás **TODOS** los paquetes TCP del sistema MQTT.

### Identificar el 3-Way Handshake

Filtro:
```
tcp.flags.syn == 1 && tcp.flags.ack == 0
```

Busca los 3 paquetes del handshake:
1. **SYN** - Cliente solicita conexión
2. **SYN-ACK** - Servidor acepta
3. **ACK** - Cliente confirma

**Esto prueba que usas TCP.**

### Ver Solo Mensajes MQTT

Filtro:
```
mqtt
```

Resultado: Solo paquetes que contienen mensajes MQTT (CONNECT, PUBLISH, SUBSCRIBE, etc.)

### Ver Solo Mensajes PUBLISH

Filtro:
```
mqtt.msgtype == 3
```

Resultado: Solo mensajes que publican datos de sensores.

---

## 🕵️ Paso 6: Demostrar Vulnerabilidad (Sniffing)

### Follow TCP Stream

1. Click derecho en **cualquier paquete MQTT**
2. **Follow → TCP Stream**

**¡Verás todo el tráfico en texto claro!**

Ejemplo de lo que verás:
```
{"sensor_id":"sensor_temp_salon","tipo":"temperatura","valor":23.5,"unidad":"°C","zona":"salon","timestamp":"2025-01-23T10:30:45.123456"}
```

**Esto demuestra que:**
- ❌ Los datos NO están cifrados
- ❌ Cualquiera puede leer los valores de los sensores
- ❌ Se pueden ver comandos a actuadores
- ❌ La estructura del sistema está expuesta

---

## 📸 Paso 7: Capturas para el Informe

### Captura 1: 3-Way Handshake TCP

**Qué mostrar:**
- Los 3 paquetes del handshake (SYN, SYN-ACK, ACK)
- Flags TCP visibles
- Números de secuencia
- Puertos (origen efímero, destino 1883)

**Filtro:**
```
tcp.flags.syn == 1
```

**Descripción para el informe:**
> "Se puede observar el establecimiento de conexión TCP mediante el 3-way handshake, confirmando que el sistema utiliza TCP como protocolo de transporte."

---

### Captura 2: Mensaje MQTT PUBLISH

**Qué mostrar:**
- Paquete TCP con flag PSH
- Cabecera MQTT con tipo PUBLISH
- Tópico MQTT
- Payload JSON

**Filtro:**
```
mqtt.msgtype == 3
```

**Cómo hacerlo:**
1. Aplicar filtro
2. Seleccionar un paquete
3. Expandir: `Frame → Ethernet II → IP → TCP → MQTT`

**Descripción para el informe:**
> "El análisis muestra un mensaje MQTT PUBLISH transportado sobre TCP (puerto 1883), incluyendo el tópico y el payload JSON con datos del sensor de temperatura."

---

### Captura 3: TCP Stream (Vulnerabilidad)

**Qué mostrar:**
- Follow TCP Stream completo
- JSON en texto claro
- Varios mensajes consecutivos

**Cómo hacerlo:**
1. Click derecho en paquete MQTT
2. Follow → TCP Stream
3. Captura de pantalla mostrando JSON legible

**Descripción para el informe:**
> "Mediante la funcionalidad 'Follow TCP Stream' de Wireshark se evidencia que el tráfico MQTT viaja sin cifrar, permitiendo la lectura completa de los datos en texto claro. Esto representa una vulnerabilidad crítica del sistema."

---

### Captura 4: Jerarquía de Protocolos

**Qué mostrar:**
- Statistics → Protocol Hierarchy

**Descripción para el informe:**
> "La jerarquía de protocolos confirma que el 100% del tráfico de capa de transporte es TCP, sin presencia de UDP. El sistema utiliza exclusivamente TCP para la comunicación."

---

## 📋 Análisis de Capas OSI

### Capa 2 - Enlace de Datos

En Wireshark, expande:
```
Frame → Ethernet II
```

Información visible:
- **Destination MAC**: 02:42:ac:1c:00:0a (broker)
- **Source MAC**: 02:42:ac:1c:00:6f (sensor)
- **Type**: IPv4 (0x0800)

### Capa 3 - Red

Expande:
```
Frame → Internet Protocol Version 4
```

Información visible:
- **Source**: 172.28.0.111 (sensor-temp-salon)
- **Destination**: 172.28.0.10 (mqtt-broker)
- **Protocol**: TCP (6)
- **TTL**: 64

### Capa 4 - Transporte

Expande:
```
Frame → Transmission Control Protocol
```

Información visible:
- **Source Port**: 45678 (efímero)
- **Destination Port**: 1883 (MQTT)
- **Flags**: SYN, ACK, PSH, FIN
- **Sequence Number**: 1234 (ejemplo)
- **Acknowledgment Number**: 5678 (ejemplo)
- **Window Size**: 29200

**Evidencias de TCP:**
- ✅ 3-way handshake
- ✅ Flags TCP (SYN, ACK, PSH, FIN)
- ✅ Números de secuencia y ACK
- ✅ Control de flujo (ventana)
- ✅ Checksums

### Capa 7 - Aplicación

Expande:
```
Frame → MQ Telemetry Transport Protocol
```

Información visible:
- **Message Type**: PUBLISH (3)
- **QoS Level**: 0
- **Topic**: casa/sensor/temperatura/salon
- **Payload**: JSON con datos del sensor

---

## 🎓 Filtros Útiles de Wireshark

### Básicos

```
tcp                       # Todo el tráfico TCP
tcp.port == 1883          # Solo puerto MQTT
mqtt                       # Solo mensajes MQTT
ip.addr == 172.28.0.10    # Solo tráfico del broker
```

### Análisis de Conexión TCP

```
tcp.flags.syn == 1 && tcp.flags.ack == 0  # Paso 1 handshake (SYN)
tcp.flags.syn == 1 && tcp.flags.ack == 1  # Paso 2 handshake (SYN-ACK)
tcp.flags.fin == 1                         # Cierre de conexión
```

### Análisis de MQTT

```
mqtt.msgtype == 1         # CONNECT
mqtt.msgtype == 2         # CONNACK
mqtt.msgtype == 3         # PUBLISH
mqtt.msgtype == 8         # SUBSCRIBE
mqtt.topic contains "temperatura"  # Tópicos de temperatura
```

### Análisis de Datos

```
tcp.len > 0               # Paquetes con datos (no solo ACK)
tcp.analysis.retransmission  # Retransmisiones TCP
```

---

## 📊 Estadísticas en Wireshark

### Protocol Hierarchy

**Menú:** Statistics → Protocol Hierarchy

**Qué muestra:**
- Distribución de protocolos
- % de tráfico por protocolo
- Confirma que todo es TCP

### Conversations

**Menú:** Statistics → Conversations → TCP

**Qué muestra:**
- Conexiones TCP entre IPs
- Puertos utilizados
- Cantidad de datos transferidos

### Endpoints

**Menú:** Statistics → Endpoints → IPv4

**Qué muestra:**
- Dispositivos en la red
- IPs y puertos
- Volumen de tráfico por dispositivo

---

## ✅ Checklist para el Informe

- [ ] Captura del 3-way handshake TCP
- [ ] Captura de mensaje MQTT PUBLISH
- [ ] Follow TCP Stream mostrando JSON en claro
- [ ] Protocol Hierarchy (confirma 100% TCP)
- [ ] Análisis de cada capa OSI (2, 3, 4)
- [ ] Tabla con flags TCP encontrados
- [ ] Descripción de puertos utilizados
- [ ] Demostración de vulnerabilidad

---

## 🔒 Conclusión

**Protocolo confirmado: TCP**

**Evidencias:**
1. ✅ 3-way handshake en todas las conexiones
2. ✅ Puerto 1883 (MQTT estándar sobre TCP)
3. ✅ Flags TCP (SYN, ACK, PSH, FIN)
4. ✅ Números de secuencia y ACK
5. ✅ Protocol Hierarchy muestra 100% TCP

**Vulnerabilidad:**
❌ Tráfico sin cifrar - Datos legibles con Follow TCP Stream

**Mitigación:**
🔒 Implementar TLS/SSL (puerto 8883)

---

**Asignatura:** Ciberseguridad en Desarrollos Tecnológicos Innovadores
**Protocolo:** TCP (Transmission Control Protocol)
**Herramienta:** Wireshark
