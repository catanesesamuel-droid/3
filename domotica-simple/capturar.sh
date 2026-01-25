#!/bin/bash
#
# SCRIPT SIMPLE DE CAPTURA - UN SOLO COMANDO
#

echo "=============================================="
echo "  CAPTURANDO TRÁFICO MQTT (TCP)"
echo "=============================================="
echo ""
echo "Puerto: 1883 (MQTT)"
echo "Archivo: captura.pcap"
echo ""
echo "Presiona Ctrl+C para detener"
echo "=============================================="
echo ""

# Capturar TODO el tráfico MQTT
docker exec network-analyzer tcpdump -i eth0 -w /capturas/captura.pcap 'tcp port 1883' -v

echo ""
echo "✅ Captura guardada en: capturas/captura.pcap"
echo ""
echo "Para ver con Wireshark:"
echo "  wireshark capturas/captura.pcap"
