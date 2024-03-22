#!/bin/bash

echo "Limpiando el log del cron"

rm -f log.cron

touch log.cron

chmod 777 log.cron

echo "Archivo log.cron limpio"
echo "Proceso finalizado"
