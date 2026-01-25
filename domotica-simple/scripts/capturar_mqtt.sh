#!/bin/bash
#
# Script de captura de tráfico MQTT (TCP puerto 1883)
# Análisis de capa de transporte (TCP) y aplicación (MQTT)
#

set -e

DURACION=${1:-60}
ARCHIVO_SALIDA="/capturas/mqtt_tcp_$(date +%Y%m%d_%H%M%S).pcap"

echo "========================================="
echo "  CAPTURA DE TRÁFICO MQTT (TCP)"
echo "========================================="
echo "Protocolo: TCP"
echo "Puerto: 1883"
echo "Duración: ${DURACION} segundos"
echo "Archivo: ${ARCHIVO_SALIDA}"
echo "========================================="
echo ""

# Capturar tráfico MQTT
echo "[*] Iniciando captura de tráfico MQTT..."
timeout ${DURACION} tcpdump -i eth0 \
    -w "${ARCHIVO_SALIDA}" \
    'tcp port 1883' \
    -v

echo ""
echo "[✓] Captura completada: ${ARCHIVO_SALIDA}"
echo ""

# Análisis básico con tshark si está disponible
if command -v tshark &> /dev/null; then
    echo "========================================="
    echo "  ANÁLISIS BÁSICO DE LA CAPTURA"
    echo "========================================="

    echo ""
    echo "[*] Estadísticas de protocolos:"
    tshark -r "${ARCHIVO_SALIDA}" -q -z io,phs

    echo ""
    echo "[*] Número de paquetes capturados:"
    tshark -r "${ARCHIVO_SALIDA}" | wc -l

    echo ""
    echo "[*] Mensajes MQTT capturados:"
    tshark -r "${ARCHIVO_SALIDA}" -Y "mqtt" -T fields \
        -e frame.number \
        -e ip.src \
        -e ip.dst \
        -e mqtt.msgtype \
        -e mqtt.topic 2>/dev/null | head -20

    echo ""
    echo "[*] Generando resumen en texto..."
    tshark -r "${ARCHIVO_SALIDA}" -V > "${ARCHIVO_SALIDA%.pcap}_analisis.txt"
    echo "[✓] Resumen guardado: ${ARCHIVO_SALIDA%.pcap}_analisis.txt"
fi

echo ""
echo "========================================="
echo "  CAPTURA FINALIZADA"
echo "========================================="
echo "Archivo PCAP: ${ARCHIVO_SALIDA}"
echo ""
echo "Para analizar con Wireshark:"
echo "  1. Copiar archivo a tu máquina local"
echo "  2. Abrir con Wireshark"
echo "  3. Aplicar filtro: tcp.port == 1883 || mqtt"
echo "========================================="
