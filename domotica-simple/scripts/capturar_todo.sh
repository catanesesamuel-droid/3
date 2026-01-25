#!/bin/bash
#
# Script de captura de tráfico TCP MQTT de la red domótica
# Análisis completo de protocolo TCP: 3-way handshake, mensajes MQTT, etc.
#

set -e

DURACION=${1:-120}
ARCHIVO_SALIDA="/capturas/mqtt_red_completa_$(date +%Y%m%d_%H%M%S).pcap"

echo "=============================================="
echo "  CAPTURA DE TRÁFICO TCP (MQTT)"
echo "=============================================="
echo "Protocolo: TCP"
echo "Puerto: 1883 (MQTT)"
echo "Red: 172.28.0.0/16"
echo "Duración: ${DURACION} segundos"
echo "Archivo: ${ARCHIVO_SALIDA}"
echo "=============================================="
echo ""

# Capturar tráfico TCP de la red Docker
echo "[*] Iniciando captura de tráfico TCP MQTT..."
echo "[*] Capturando: Conexiones TCP, Handshakes, Mensajes MQTT..."
timeout ${DURACION} tcpdump -i eth0 \
    -w "${ARCHIVO_SALIDA}" \
    -s 0 \
    'tcp port 1883 or tcp port 8080' \
    -vv

echo ""
echo "[✓] Captura completada: ${ARCHIVO_SALIDA}"
echo ""

# Análisis exhaustivo
if command -v tshark &> /dev/null; then
    echo "=============================================="
    echo "  ANÁLISIS DE LA CAPTURA TCP"
    echo "=============================================="

    echo ""
    echo "[*] Total de paquetes capturados:"
    tshark -r "${ARCHIVO_SALIDA}" | wc -l

    echo ""
    echo "[*] Jerarquía de protocolos:"
    tshark -r "${ARCHIVO_SALIDA}" -q -z io,phs

    echo ""
    echo "[*] Conexiones TCP (3-way handshake detectados):"
    tshark -r "${ARCHIVO_SALIDA}" -Y "tcp.flags.syn == 1 && tcp.flags.ack == 0" \
        -T fields \
        -e frame.number \
        -e ip.src \
        -e ip.dst \
        -e tcp.srcport \
        -e tcp.dstport 2>/dev/null | head -10

    echo ""
    echo "[*] Estadísticas de conexiones TCP:"
    tshark -r "${ARCHIVO_SALIDA}" -q -z conv,tcp | head -15

    echo ""
    echo "[*] Endpoints IPv4:"
    tshark -r "${ARCHIVO_SALIDA}" -q -z endpoints,ip | head -20

    echo ""
    echo "[*] Mensajes MQTT detectados:"
    MQTT_COUNT=$(tshark -r "${ARCHIVO_SALIDA}" -Y "mqtt" 2>/dev/null | wc -l)
    echo "Total: $MQTT_COUNT mensajes"

    echo ""
    echo "[*] Tipos de mensajes MQTT:"
    tshark -r "${ARCHIVO_SALIDA}" -Y "mqtt" -T fields -e mqtt.msgtype 2>/dev/null | \
        awk '{
            if ($1 == 1) print "CONNECT"
            else if ($1 == 2) print "CONNACK"
            else if ($1 == 3) print "PUBLISH"
            else if ($1 == 4) print "PUBACK"
            else if ($1 == 8) print "SUBSCRIBE"
            else if ($1 == 9) print "SUBACK"
            else if ($1 == 12) print "PINGREQ"
            else if ($1 == 13) print "PINGRESP"
            else print "Otro (" $1 ")"
        }' | sort | uniq -c

    echo ""
    echo "[*] Tópicos MQTT publicados:"
    tshark -r "${ARCHIVO_SALIDA}" -Y "mqtt.topic" -T fields -e mqtt.topic 2>/dev/null | \
        sort | uniq -c | sort -rn | head -10

    echo ""
    echo "[*] Generando informe completo..."
    {
        echo "ANÁLISIS DE RED TCP - SISTEMA DOMÓTICO"
        echo "========================================"
        echo ""
        echo "Fecha: $(date)"
        echo "Archivo: ${ARCHIVO_SALIDA}"
        echo "Protocolo: TCP (MQTT)"
        echo ""
        echo "JERARQUÍA DE PROTOCOLOS:"
        echo "------------------------"
        tshark -r "${ARCHIVO_SALIDA}" -q -z io,phs
        echo ""
        echo "CONEXIONES TCP:"
        echo "---------------"
        tshark -r "${ARCHIVO_SALIDA}" -q -z conv,tcp
        echo ""
        echo "MENSAJES MQTT:"
        echo "--------------"
        echo "Total de mensajes: $MQTT_COUNT"
        echo ""
        echo "Tipos de mensajes:"
        tshark -r "${ARCHIVO_SALIDA}" -Y "mqtt" -T fields -e mqtt.msgtype 2>/dev/null | \
            awk '{
                if ($1 == 1) print "CONNECT"
                else if ($1 == 2) print "CONNACK"
                else if ($1 == 3) print "PUBLISH"
                else if ($1 == 4) print "PUBACK"
                else if ($1 == 8) print "SUBSCRIBE"
                else if ($1 == 9) print "SUBACK"
                else if ($1 == 12) print "PINGREQ"
                else if ($1 == 13) print "PINGRESP"
                else print "Otro"
            }' | sort | uniq -c
    } > "${ARCHIVO_SALIDA%.pcap}_informe.txt"

    echo "[✓] Informe guardado: ${ARCHIVO_SALIDA%.pcap}_informe.txt"
fi

echo ""
echo "=============================================="
echo "  CAPTURA Y ANÁLISIS FINALIZADO"
echo "=============================================="
echo "Archivos generados:"
echo "  - ${ARCHIVO_SALIDA}"
echo "  - ${ARCHIVO_SALIDA%.pcap}_informe.txt"
echo ""
echo "Para análisis detallado con Wireshark:"
echo "  1. docker cp network-analyzer:${ARCHIVO_SALIDA} ."
echo "  2. Abrir con Wireshark"
echo ""
echo "Filtros útiles en Wireshark:"
echo "  - tcp.port == 1883         (Todo el tráfico MQTT)"
echo "  - mqtt                      (Solo mensajes MQTT)"
echo "  - tcp.flags.syn == 1       (3-way handshake)"
echo "  - mqtt.msgtype == 3        (Mensajes PUBLISH)"
echo "  - Follow TCP Stream        (Ver contenido completo)"
echo "=============================================="
