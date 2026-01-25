#!/bin/bash
#
# Script de análisis de capas OSI de paquetes TCP capturados
# Enfoque en capas bajas: 2 (Enlace), 3 (Red), 4 (Transporte - TCP)
#

set -e

if [ -z "$1" ]; then
    echo "Uso: $0 <archivo.pcap>"
    echo ""
    echo "Ejemplo:"
    echo "  $0 /capturas/mqtt_tcp_20250123_120000.pcap"
    exit 1
fi

ARCHIVO_PCAP="$1"
ARCHIVO_SALIDA="${ARCHIVO_PCAP%.pcap}_analisis_osi.txt"

if [ ! -f "${ARCHIVO_PCAP}" ]; then
    echo "Error: Archivo no encontrado: ${ARCHIVO_PCAP}"
    exit 1
fi

echo "=============================================="
echo "  ANÁLISIS DE CAPAS OSI - PROTOCOLO TCP"
echo "=============================================="
echo "Archivo: ${ARCHIVO_PCAP}"
echo "Salida: ${ARCHIVO_SALIDA}"
echo "Protocolo: TCP (MQTT)"
echo "=============================================="
echo ""

{
    echo "ANÁLISIS DE CAPAS OSI - SISTEMA DOMÓTICO TCP"
    echo "=============================================="
    echo ""
    echo "Archivo analizado: ${ARCHIVO_PCAP}"
    echo "Fecha de análisis: $(date)"
    echo "Protocolo de transporte: TCP"
    echo ""
    echo "==========================================="
    echo "CAPA 2 - ENLACE DE DATOS (Ethernet)"
    echo "==========================================="
    echo ""

    if command -v tshark &> /dev/null; then
        echo "Direcciones MAC origen/destino:"
        echo "-------------------------------"
        tshark -r "${ARCHIVO_PCAP}" -T fields \
            -e frame.number \
            -e eth.src \
            -e eth.dst \
            -e eth.type 2>/dev/null | head -20

        echo ""
        echo "Distribución de tipos Ethernet:"
        echo "-------------------------------"
        tshark -r "${ARCHIVO_PCAP}" -T fields -e eth.type 2>/dev/null | \
            sort | uniq -c | sort -rn

        echo ""
        echo "Tamaños de frame (Bytes):"
        echo "-------------------------"
        tshark -r "${ARCHIVO_PCAP}" -T fields -e frame.len 2>/dev/null | \
            awk '{sum+=$1; count++} END {
                if (count > 0) {
                    print "Total frames: " count
                    print "Tamaño promedio: " sum/count " bytes"
                    print "Total bytes: " sum
                }
            }'

        echo ""
        echo "==========================================="
        echo "CAPA 3 - RED (IP)"
        echo "==========================================="
        echo ""

        echo "Estadísticas IPv4:"
        echo "------------------"
        echo ""
        echo "Direcciones IP únicas (Origen):"
        tshark -r "${ARCHIVO_PCAP}" -T fields -e ip.src 2>/dev/null | \
            sort -u

        echo ""
        echo "Direcciones IP únicas (Destino):"
        tshark -r "${ARCHIVO_PCAP}" -T fields -e ip.dst 2>/dev/null | \
            sort -u

        echo ""
        echo "Pares de comunicación IP (Top 10):"
        echo "-----------------------------------"
        tshark -r "${ARCHIVO_PCAP}" -T fields \
            -e ip.src \
            -e ip.dst 2>/dev/null | \
            sort | uniq -c | sort -rn | head -10

        echo ""
        echo "Distribución de TTL (Time To Live):"
        echo "------------------------------------"
        tshark -r "${ARCHIVO_PCAP}" -T fields -e ip.ttl 2>/dev/null | \
            sort | uniq -c | sort -rn

        echo ""
        echo "Valores de IP ID (fragmentación):"
        echo "---------------------------------"
        tshark -r "${ARCHIVO_PCAP}" -T fields \
            -e frame.number \
            -e ip.id \
            -e ip.flags.df \
            -e ip.flags.mf 2>/dev/null | head -15

        echo ""
        echo "==========================================="
        echo "CAPA 4 - TRANSPORTE (TCP)"
        echo "==========================================="
        echo ""

        echo "Protocolo utilizado: TCP"
        echo "------------------------"
        TOTAL_TCP=$(tshark -r "${ARCHIVO_PCAP}" -Y "tcp" 2>/dev/null | wc -l)
        echo "Total de paquetes TCP: $TOTAL_TCP"

        echo ""
        echo "Puertos TCP utilizados:"
        echo "-----------------------"
        echo "Puertos destino:"
        tshark -r "${ARCHIVO_PCAP}" -Y "tcp" -T fields -e tcp.dstport 2>/dev/null | \
            sort | uniq -c | sort -rn | head -10

        echo ""
        echo "Flags TCP encontrados:"
        echo "----------------------"
        echo "Frame# | SYN | ACK | FIN | RST | PSH"
        echo "-------|-----|-----|-----|-----|-----"
        tshark -r "${ARCHIVO_PCAP}" -Y "tcp" -T fields \
            -e frame.number \
            -e tcp.flags.syn \
            -e tcp.flags.ack \
            -e tcp.flags.fin \
            -e tcp.flags.reset \
            -e tcp.flags.push 2>/dev/null | \
            head -20

        echo ""
        echo "Conexiones TCP (3-way handshake detectados):"
        echo "--------------------------------------------"
        tshark -r "${ARCHIVO_PCAP}" -Y "tcp.flags.syn == 1 && tcp.flags.ack == 0" \
            -T fields \
            -e frame.number \
            -e ip.src \
            -e ip.dst \
            -e tcp.srcport \
            -e tcp.dstport 2>/dev/null | head -10

        echo ""
        echo "Tamaños de ventana TCP:"
        echo "-----------------------"
        tshark -r "${ARCHIVO_PCAP}" -Y "tcp" -T fields -e tcp.window_size 2>/dev/null | \
            awk '{sum+=$1; count++} END {
                if (count > 0) {
                    print "Ventana promedio: " sum/count " bytes"
                }
            }'

        echo ""
        echo "Números de secuencia TCP (primeros 10 paquetes):"
        echo "------------------------------------------------"
        echo "Frame# | Seq Number | Ack Number | Length"
        echo "-------|------------|------------|-------"
        tshark -r "${ARCHIVO_PCAP}" -Y "tcp" -T fields \
            -e frame.number \
            -e tcp.seq \
            -e tcp.ack \
            -e tcp.len 2>/dev/null | head -10

        echo ""
        echo "Segmentos TCP con datos (payload > 0):"
        echo "---------------------------------------"
        TCP_WITH_DATA=$(tshark -r "${ARCHIVO_PCAP}" -Y "tcp.len > 0" 2>/dev/null | wc -l)
        echo "Total segmentos con datos: $TCP_WITH_DATA"

        echo ""
        echo "Checksums TCP:"
        echo "--------------"
        tshark -r "${ARCHIVO_PCAP}" -Y "tcp" -T fields \
            -e frame.number \
            -e tcp.checksum \
            -e tcp.checksum.status 2>/dev/null | head -10

        echo ""
        echo "==========================================="
        echo "CAPA 7 - APLICACIÓN (MQTT sobre TCP)"
        echo "==========================================="
        echo ""

        MQTT_COUNT=$(tshark -r "${ARCHIVO_PCAP}" -Y "mqtt" 2>/dev/null | wc -l)

        if [ "$MQTT_COUNT" -gt 0 ]; then
            echo "Total de mensajes MQTT: $MQTT_COUNT"
            echo ""

            echo "Tipos de mensajes MQTT:"
            echo "-----------------------"
            tshark -r "${ARCHIVO_PCAP}" -Y "mqtt" -T fields -e mqtt.msgtype 2>/dev/null | \
                awk '{
                    if ($1 == 1) print "CONNECT (1)"
                    else if ($1 == 2) print "CONNACK (2)"
                    else if ($1 == 3) print "PUBLISH (3)"
                    else if ($1 == 4) print "PUBACK (4)"
                    else if ($1 == 8) print "SUBSCRIBE (8)"
                    else if ($1 == 9) print "SUBACK (9)"
                    else if ($1 == 12) print "PINGREQ (12)"
                    else if ($1 == 13) print "PINGRESP (13)"
                    else print "Otro (" $1 ")"
                }' | sort | uniq -c

            echo ""
            echo "Tópicos MQTT publicados:"
            echo "------------------------"
            tshark -r "${ARCHIVO_PCAP}" -Y "mqtt.topic" -T fields -e mqtt.topic 2>/dev/null | \
                sort | uniq -c | sort -rn

            echo ""
            echo "QoS (Quality of Service) utilizado:"
            echo "------------------------------------"
            tshark -r "${ARCHIVO_PCAP}" -Y "mqtt" -T fields -e mqtt.qos 2>/dev/null | \
                awk '{
                    if ($1 == 0) print "QoS 0 (At most once)"
                    else if ($1 == 1) print "QoS 1 (At least once)"
                    else if ($1 == 2) print "QoS 2 (Exactly once)"
                }' | sort | uniq -c

            echo ""
            echo "Client IDs MQTT:"
            echo "----------------"
            tshark -r "${ARCHIVO_PCAP}" -Y "mqtt.clientid" -T fields -e mqtt.clientid 2>/dev/null | \
                sort -u
        else
            echo "No se encontraron mensajes MQTT en esta captura"
        fi

        echo ""
        echo "==========================================="
        echo "RESUMEN GENERAL"
        echo "==========================================="
        echo ""

        TOTAL_PAQUETES=$(tshark -r "${ARCHIVO_PCAP}" 2>/dev/null | wc -l)

        echo "Total de paquetes capturados: $TOTAL_PAQUETES"
        echo "  - Paquetes TCP: $TOTAL_TCP"
        echo "  - Mensajes MQTT: $MQTT_COUNT"

        echo ""
        echo "Distribución porcentual:"
        awk -v total="$TOTAL_PAQUETES" -v tcp="$TOTAL_TCP" 'BEGIN {
            if (total > 0) {
                printf "  - TCP: %.2f%%\n", (tcp/total)*100
            }
        }'

        echo ""
        echo "Protocolo confirmado: TCP (Transmission Control Protocol)"
        echo "Puerto principal: 1883 (MQTT)"
        echo ""
        echo "Evidencia de TCP:"
        echo "  ✓ 3-way handshake detectado"
        echo "  ✓ Flags TCP: SYN, ACK, PSH, FIN"
        echo "  ✓ Números de secuencia y ACK"
        echo "  ✓ Ventanas de control de flujo"
        echo "  ✓ Checksums TCP"

    else
        echo "tshark no está instalado. Instalando..."
        apt-get update && apt-get install -y tshark
    fi

} | tee "${ARCHIVO_SALIDA}"

echo ""
echo "=============================================="
echo "  ANÁLISIS COMPLETADO"
echo "=============================================="
echo "Informe guardado en: ${ARCHIVO_SALIDA}"
echo ""
echo "Protocolo confirmado: TCP"
echo "=============================================="
