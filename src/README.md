
## Despliegue de servicios en servidor con GPU

* Clona repositorio y descargar pesos
```bash
git clone https://github.com/CentroFuturoCiudades/traffic-conflicts-analysis.git
cd traffic-conflicts-analysis/src/TTC-API/
wget https://tca-itdp-tec-prod.s3.amazonaws.com/weights.zip
unzip weights.zip
```
* Construir y levantar servicios
```bash
cd ..
docker compose down
docker compose up -d --build
```
