#!/bin/bash

# Script para iniciar el sistema de domótica completo

echo "🏠 SISTEMA DE DOMÓTICA COMPLETO"
echo "================================"
echo ""

# Dar permisos de ejecución
echo "🔧 Configurando permisos..."
chmod +x scada_central.py
chmod +x nodos/*.py
chmod +x scripts/*.sh

# Construir e iniciar contenedores
echo "🚀 Iniciando contenedores Docker..."
docker compose down  # Detener si ya está corriendo
docker compose up -d --build

echo ""
echo "✅ Sistema iniciado correctamente!"
echo ""
echo "🌐 SERVICIOS DISPONIBLES:"
echo "   Dashboard SCADA:     http://localhost:8081"
echo "   API REST:           http://localhost:5000/api/status"
echo "   MQTT Broker:        localhost:1883"
echo "   MQTT WebSocket:     ws://localhost:8080"
echo "   Alarma UDP:         localhost:9999"
echo ""
echo "📊 COMANDOS ÚTILES:"
echo "   Ver logs:           docker compose logs -f"
echo "   Ver contenedores:   docker compose ps"
echo "   Detener sistema:    docker compose down"
echo "   Reiniciar:          docker compose restart"
echo ""
echo "🎛️  COMANDOS MQTT DE EJEMPLO:"
echo "   Encender luz:       mosquitto_pub -h localhost -t 'casa/actuador/luces/comandos' -m '{\"tipo\":\"luces\",\"accion\":\"encender\",\"luz\":\"salon_principal\",\"intensidad\":80}'"
echo "   Subir persianas:    mosquitto_pub -h localhost -t 'casa/actuador/persianas/comandos' -m '{\"tipo\":\"persianas\",\"accion\":\"subir\",\"porcentaje\":75}'"
echo "   Armar alarma:       mosquitto_pub -h localhost -t 'casa/alarma/comandos' -m '{\"tipo\":\"alarma\",\"accion\":\"armar\"}'"
echo ""
echo "📡 MONITORIZAR:"
echo "   mosquitto_sub -h localhost -t 'casa/#' -v"
echo ""

# Esperar a que los servicios se inicien
echo "⏳ Esperando a que los servicios se inicialicen..."
sleep 10

# Mostrar estado de los contenedores
echo ""
echo "📊 ESTADO DE CONTENEDORES:"
docker compose ps