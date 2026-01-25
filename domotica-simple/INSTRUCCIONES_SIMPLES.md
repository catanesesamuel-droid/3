# 🚀 Instrucciones SIMPLES

## Paso 1: Levantar el sistema

```bash
docker-compose down
docker-compose up -d
```

Espera 30 segundos a que todo arranque.

## Paso 2: Ver el dashboard

Abre tu navegador:

```
http://localhost:8081
```

Deberías ver el panel de control con:
- Estado de sensores (temperatura, luz)
- Botones para controlar luces
- Botones para persianas

## Paso 3: Verificar que funciona

```bash
# Ver logs del dashboard
docker logs scada-central

# Ver logs de un sensor
docker logs sensor-temp-salon

# Ver mensajes MQTT en tiempo real
docker exec mqtt-broker mosquitto_sub -v -t '#'
```

Deberías ver mensajes como:
```
casa/sensor/temperatura/salon {"valor":23.5,...}
casa/sensor/luz/salon {"valor":450,...}
```

## Paso 4: Capturar tráfico con WIRESHARK

**UN SOLO COMANDO:**

```bash
./capturar.sh
```

Eso es todo. Presiona Ctrl+C cuando quieras parar.

El archivo se guarda en: `capturas/captura.pcap`

## Paso 5: Abrir con Wireshark

```bash
wireshark capturas/captura.pcap
```

**Filtro recomendado:**
```
tcp.port == 1883
```

## Paso 6: Ver datos en claro (VULNERABILIDAD)

En Wireshark:
1. Click derecho en cualquier paquete MQTT
2. **Follow → TCP Stream**

Verás el JSON en texto claro:
```json
{"sensor_id":"sensor_temp_salon","valor":23.5,"zona":"salon"}
```

---

## ❌ Problemas comunes

### El dashboard no abre (localhost:8081)

```bash
# Ver si está corriendo
docker ps | grep scada

# Ver los errores
docker logs scada-central
```

### No captura tráfico

```bash
# Verificar que network-analyzer está activo
docker ps | grep network-analyzer

# Si no está, reinicia:
docker-compose restart network-analyzer
```

### Los sensores no envían datos

```bash
# Reiniciar todos los sensores
docker-compose restart
```

---

## 🎯 Para el informe

1. **Captura del 3-way handshake:**
   - Filtro: `tcp.flags.syn == 1`

2. **Captura de mensaje MQTT:**
   - Filtro: `mqtt.msgtype == 3`

3. **Follow TCP Stream:**
   - Demuestra que los datos van sin cifrar

4. **Protocol Hierarchy:**
   - Statistics → Protocol Hierarchy
   - Confirma que es 100% TCP

---

**Protocolo:** TCP puerto 1883 (MQTT)
**Herramienta:** Wireshark
