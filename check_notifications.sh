#!/bin/bash

# Este script deve ser executado como uma cron job diária para enviar notificações
# Adicione ao crontab com:
# 0 9,15 * * * /home/iago/casamento_iago_e_duda/check_notifications.sh
# Isso enviará notificações duas vezes ao dia: às 9h e às 15h

DATA=$(date +"%Y-%m-%d %H:%M:%S")
echo "====== Iniciando verificação de notificações em $DATA ======"

cd /home/iago/casamento_iago_e_duda
python3 send_notifications.py >> notificacoes.log 2>&1

echo "====== Verificação concluída ======"
