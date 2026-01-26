#!/bin/bash
#
# Genera un archivo PCAP con tráfico MQTT simulado (más simple)
#

mkdir -p capturas

# Crear archivo hexdump de tráfico TCP/MQTT
cat > /tmp/mqtt_packets.txt << 'EOF'
# 3-way handshake TCP (SYN)
0000   02 42 ac 1c 00 0a 02 42 ac 1c 00 6f 08 00 45 00
0010   00 3c 12 34 40 00 40 06 7a 3c ac 1c 00 6f ac 1c
0020   00 0a b2 4e 07 5b 00 00 03 e8 00 00 00 00 a0 02
0030   72 10 4a 3b 00 00 02 04 05 b4 04 02 08 0a 00 01
0040   e2 40 00 00 00 00 01 03 03 07

# 3-way handshake TCP (SYN-ACK)
0000   02 42 ac 1c 00 6f 02 42 ac 1c 00 0a 08 00 45 00
0010   00 3c 00 00 40 00 40 06 8c 70 ac 1c 00 0a ac 1c
0020   00 6f 07 5b b2 4e 00 00 04 56 00 00 03 e9 a0 12
0030   71 20 5f 2e 00 00 02 04 05 b4 04 02 08 0a 00 01
0040   e2 41 00 01 e2 40 01 03 03 07

# 3-way handshake TCP (ACK)
0000   02 42 ac 1c 00 0a 02 42 ac 1c 00 6f 08 00 45 00
0010   00 34 12 35 40 00 40 06 7a 43 ac 1c 00 6f ac 1c
0020   00 0a b2 4e 07 5b 00 00 03 e9 00 00 04 57 80 10
0030   72 10 3d 2f 00 00 01 01 08 0a 00 01 e2 41 00 01
0040   e2 41

# MQTT CONNECT
0000   02 42 ac 1c 00 0a 02 42 ac 1c 00 6f 08 00 45 00
0010   00 60 12 36 40 00 40 06 7a 15 ac 1c 00 6f ac 1c
0020   00 0a b2 4e 07 5b 00 00 03 e9 00 00 04 57 80 18
0030   72 10 8f 3a 00 00 01 01 08 0a 00 01 e2 50 00 01
0040   e2 41 10 1a 00 04 4d 51 54 54 04 02 00 3c 00 10
0050   73 65 6e 73 6f 72 5f 74 65 6d 70 5f 73 61 6c 6f
0060   6e

# MQTT CONNACK
0000   02 42 ac 1c 00 6f 02 42 ac 1c 00 0a 08 00 45 00
0010   00 38 00 00 40 00 40 06 8c 88 ac 1c 00 0a ac 1c
0020   00 6f 07 5b b2 4e 00 00 04 57 00 00 04 15 80 18
0030   71 20 aa 56 00 00 01 01 08 0a 00 01 e2 55 00 01
0040   e2 50 20 02 00 00

# MQTT PUBLISH - Temperatura {"sensor_id":"sensor_temp_salon","valor":23.5}
0000   02 42 ac 1c 00 0a 02 42 ac 1c 00 6f 08 00 45 00
0010   00 dc 12 37 40 00 40 06 79 98 ac 1c 00 6f ac 1c
0020   00 0a b2 4e 07 5b 00 00 04 15 00 00 04 59 80 18
0030   72 10 f5 4e 00 00 01 01 08 0a 00 01 e3 00 00 01
0040   e2 55 30 a2 01 00 1d 63 61 73 61 2f 73 65 6e 73
0050   6f 72 2f 74 65 6d 70 65 72 61 74 75 72 61 2f 73
0060   61 6c 6f 6e 7b 22 73 65 6e 73 6f 72 5f 69 64 22
0070   3a 22 73 65 6e 73 6f 72 5f 74 65 6d 70 5f 73 61
0080   6c 6f 6e 22 2c 22 74 69 70 6f 22 3a 22 74 65 6d
0090   70 65 72 61 74 75 72 61 22 2c 22 76 61 6c 6f 72
00a0   22 3a 32 33 2e 35 2c 22 75 6e 69 64 61 64 22 3a
00b0   22 c2 b0 43 22 2c 22 7a 6f 6e 61 22 3a 22 73 61
00c0   6c 6f 6e 22 2c 22 74 69 6d 65 73 74 61 6d 70 22
00d0   3a 22 32 30 32 35 2d 30 31 2d 32 35 54 31 30 3a
00e0   33 30 3a 34 35 22 7d

# TCP ACK del broker
0000   02 42 ac 1c 00 6f 02 42 ac 1c 00 0a 08 00 45 00
0010   00 34 00 00 40 00 40 06 8c 8c ac 1c 00 0a ac 1c
0020   00 6f 07 5b b2 4e 00 00 04 59 00 00 05 05 80 10
0030   71 20 7e 3f 00 00 01 01 08 0a 00 01 e3 02 00 01
0040   e3 00

# MQTT PUBLISH - Luz {"sensor_id":"sensor_luz_salon","valor":450}
0000   02 42 ac 1c 00 0a 02 42 ac 1c 00 65 08 00 45 00
0010   00 b8 12 38 40 00 40 06 79 cb ac 1c 00 65 ac 1c
0020   00 0a b2 4f 07 5b 00 00 05 20 00 00 05 78 80 18
0030   72 10 c8 9a 00 00 01 01 08 0a 00 01 e5 50 00 01
0040   e3 02 30 7e 00 17 63 61 73 61 2f 73 65 6e 73 6f
0050   72 2f 6c 75 7a 2f 73 61 6c 6f 6e 7b 22 73 65 6e
0060   73 6f 72 5f 69 64 22 3a 22 73 65 6e 73 6f 72 5f
0070   6c 75 7a 5f 73 61 6c 6f 6e 22 2c 22 74 69 70 6f
0080   22 3a 22 6c 75 7a 22 2c 22 76 61 6c 6f 72 22 3a
0090   34 35 30 2c 22 75 6e 69 64 61 64 22 3a 22 6c 75
00a0   78 22 2c 22 65 73 74 61 64 6f 22 3a 22 6c 75 6d
00b0   69 6e 6f 73 6f 22 2c 22 7a 6f 6e 61 22 3a 22 73
00c0   61 6c 6f 6e 22 7d
EOF

echo "Generando archivo PCAP desde hexdump..."
text2pcap /tmp/mqtt_packets.txt capturas/captura.pcap

if [ $? -eq 0 ]; then
    echo "✅ Archivo PCAP generado: capturas/captura.pcap"
    echo ""
    echo "Para abrir con Wireshark:"
    echo "  wireshark capturas/captura.pcap"
    echo ""
    echo "Filtros útiles:"
    echo "  - tcp.port == 1883"
    echo "  - mqtt"
    echo "  - tcp.flags.syn == 1"
else
    echo "❌ Error generando PCAP. Instalando text2pcap..."
    sudo apt-get update && sudo apt-get install -y wireshark-common
    text2pcap /tmp/mqtt_packets.txt capturas/captura.pcap
fi
