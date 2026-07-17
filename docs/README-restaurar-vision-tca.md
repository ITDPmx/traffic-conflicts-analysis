# Restaurar vision-tca

Última actualización: 2026-07-17

## Qué pasó

La instancia original `vision-tca` (`i-02a33facac910baba`, g4dn.xlarge) fue **terminada** para ahorrar costo de cómputo/storage. Se decidió **no conservar la AMI ni el snapshot** (`ami-01e68421a4f372d6d` / `snap-091464624ebcc1617` — borrados). El único respaldo que existe es un `.tar.gz` en S3 con el código, config, llaves y datos irremplazables — **no es una imagen arrancable**. Restaurar significa reconstruir el entorno desde cero y luego reponer estos datos encima.

## Dónde está el respaldo

```
s3://tca-itdp-tec-prod/backups/vision-tca/vision-tca-backup-20260717.tar.gz
```
- Tamaño exacto: 1,033,922,381 bytes (987 MB), verificado byte a byte contra el original.
- Contiene: `.aws`, `.ssh`, `.config`, `.bashrc`, `.profile`, `BEV-API/`, `traffic-conflicts-analysis/` (código completo, incluye `weights/`, `host_shared_data/` con videos y CSVs históricos, y los `.env` de `BEV-API`/`TTC-API` **con credenciales sin rotar**), `is_running.*`, `run.*`, `private.pem`, `public.pem`, `environment_backup.yml` (export de conda), `homography_matrix.txt`, `target_dim.txt`.
- **NO contiene**: el sistema operativo, drivers NVIDIA, Docker, ni el entorno conda instalado (solo su definición) — todo eso se reinstala.
- **NO contiene**: imágenes Docker ya construidas — se reconstruyen desde los Dockerfile del repo.

## Datos de red confirmados

No se capturaron antes de terminar la instancia, pero se reconstruyeron a partir de la consola y la lista de security groups de la cuenta:

- **VPC**: `vpc-0b681fad058316a17` (único VPC real de la cuenta, confirmado también en `testVM`)
- **Security group**: `sg-0e05e96666786c9b0` (`launch-wizard-2` — coincide por nombre con el que tenía `vision-tca` en el inventario original)
- **Availability Zone**: `us-east-1f` (`use1-az5`)
- **Subnet**: `subnet-06214470f9fa6c4ca` (CIDR `172.31.64.0/20`) — única subnet en ese VPC/AZ, confirmada, sin ambigüedad.

## Pendiente crítico — resolver ANTES de restaurar

- [ ] **Rotar credenciales** de los `.env` de `BEV-API` y `TTC-API` — se incluyeron en el backup en texto plano, deben considerarse expuestas.
- [ ] **Revisar `.aws/credentials`** dentro del backup — son credenciales estáticas viejas. Al restaurar, mejor usar un IAM role nuevo en la instancia (como tenía antes: rol `EC2SSM`) en vez de reponer estas credenciales estáticas.

## Pasos para restaurar

### 1. Lanzar la instancia nueva

```bash
aws ec2 run-instances \
  --image-id ami-04a81a99f5ec58529 \
  --instance-type g4dn.xlarge \
  --key-name vision \
  --iam-instance-profile Name=EC2SSM \
  --security-group-ids sg-0e05e96666786c9b0 \
  --subnet-id subnet-06214470f9fa6c4ca \
  --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=128,VolumeType=gp3}'
```

Nota: `ami-04a81a99f5ec58529` es la AMI base de la que se construyó originalmente `vision-tca` — confirmado por su nombre (`ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-20240701.1`), es un Ubuntu 24.04 genérico de Canonical. **No trae drivers NVIDIA preinstalados** — hay que instalarlos manualmente en el siguiente paso, no lo saltes asumiendo que ya vienen.

Verifica que el key pair `vision` sigue existiendo en la cuenta (los key pairs no se borran al terminar una instancia):
```bash
aws ec2 describe-key-pairs --key-names vision
```

### 2. Verificar/instalar dependencias base

La AMI base es Ubuntu genérico — asume que necesitas instalar los tres desde cero:

```bash
nvidia-smi                          # va a fallar en una instancia recién lanzada, es esperado
docker --version                    # probablemente no instalado
which conda || echo "falta miniconda"
```

**Driver NVIDIA**: el instalador que se usó originalmente (`NVIDIA-Linux-x86_64-550.90.07-grid-aws.run`) **no** se incluyó en el backup — descárgalo de nuevo del sitio de NVIDIA, misma versión (550.90.07, variante GRID para AWS) para mantener compatibilidad con lo que espera el resto del entorno.

Instala Docker + Docker Compose plugin y Miniconda antes de continuar al paso 4.

### 3. Recrear el usuario `vision` y bajar el backup

```bash
sudo useradd -m -s /bin/bash vision
sudo -u vision aws s3 cp s3://tca-itdp-tec-prod/backups/vision-tca/vision-tca-backup-20260717.tar.gz /home/vision/
```

(Si el usuario `vision` no tiene todavía credenciales/role para acceder al bucket, corre el `cp` como `ubuntu`/`root` con el IAM role de la instancia en su lugar.)

### 4. Extraer el backup

```bash
sudo tar -xzvf /home/vision/vision-tca-backup-20260717.tar.gz -C /home/vision/
sudo chown -R vision:vision /home/vision
```

### 5. Recrear el entorno conda

```bash
sudo -u vision bash -c 'conda env create -f /home/vision/environment_backup.yml'
```

### 6. Reponer los datos del volumen de Docker compartido

El `docker volume` `src_shared_data` no existe todavía en la instancia nueva — se recrea solo al levantar los contenedores, pero hay que reponer su contenido:

```bash
cd /home/vision/traffic-conflicts-analysis/src
sudo docker compose up -d        # crea el volumen vacío
sudo docker compose down
sudo cp /home/vision/homography_matrix.txt /var/lib/docker/volumes/src_shared_data/_data/
sudo cp /home/vision/target_dim.txt /var/lib/docker/volumes/src_shared_data/_data/
```

### 7. Reconstruir y levantar los contenedores

```bash
cd /home/vision/traffic-conflicts-analysis/src
sudo -u vision docker compose build
sudo -u vision docker compose up -d
```

Verifica con `is_running.py`/`is_running.bash` (en `/home/vision/`) que el servicio responde, tal como lo hace `services_up()` en la lambda `StartInstance`.

### 8. Rotar credenciales expuestas

Ahora que el entorno está arriba, rota:
- Lo que esté en `src/BEV-API/.env` y `src/TTC-API/.env`
- Considera reemplazar `.aws/credentials` estático por el IAM role `EC2SSM` adjunto en el paso 1

### 9. Actualizar el Instance ID en las 4 Lambdas

La instancia nueva va a tener un **Instance ID distinto** a `i-02a33facac910baba`. El pipeline no funciona hasta actualizar este ID (hardcodeado) en:

| Lambda | Dónde está el ID |
|---|---|
| `StartInstance` | `constants.py` → variable `instance_ids` |
| `StartEC2Instances` | variable `instances` en el handler |
| `EmailSender` | variable `instance_ids` en el handler |
| `ExecuteCommandEc2` | variable `instance_id` en `lambda_handler` |

Después de editar y redesplegar las 4, prueba con `ExecuteCommandEc2` (comando `ls /home/vision`) para confirmar que el nuevo ID responde antes de probar el flujo completo.

### 10. Prueba end-to-end

Sube un video de prueba a `s3://tca-itdp-tec-prod/videos/` y confirma que:
1. `StartInstance` enciende la instancia nueva y llama a la API.
2. El procesamiento sube resultados a `processed_videos/` y `csvs/`.
3. `EmailSender` se dispara con el CSV resumen y envía el correo.

## No olvidar

- **El frontend (dashboard) corre en AWS Amplify, no en la instancia EC2 — es un pendiente aparte, no cubierto por los pasos de arriba.**
  - App: `traffic-conflicts-analysis` (App ID `d859limxqstjl`), dominio custom `tca.mexico.itdp.org`.
  - Rama `main`: estado **`Failed`**, último deployment hace 2 años. El dashboard puede no estar sirviendo una versión funcional ahora mismo, sin relación con el estado de `vision-tca`.
  - **Está conectada al repo `CentroFuturoCiudades/traffic-conflicts-analysis`, no a `ITDPmx/traffic-conflicts-analysis`.** Cambios en el repo de ITDPmx no disparan un redeploy de esta app.
  - Diagnóstico:
    ```bash
    aws amplify list-jobs --app-id d859limxqstjl --branch-name main --max-results 5
    aws amplify get-job --app-id d859limxqstjl --branch-name main --job-id <JOB_ID>
    ```
- **La hosted zone `tca.mexico.itdp.org` no requiere ninguna acción en este proceso — ni borrarla, ni repuntar registros.** Sus 5 registros (A alias, NS, SOA, CNAME de validación ACM, `www` CNAME) apuntan todos a CloudFront — sirven el dashboard/frontend, que es infraestructura separada de `vision-tca`. El pipeline nunca resuelve la instancia por DNS: `StartInstance` obtiene su IP pública llamando directo a la API de EC2 (`get_ip()`), no por nombre de dominio. Restaurar la instancia con una IP nueva no afecta ni requiere tocar esta zona.
- Considera volver a activar `disableApiTermination` en la instancia nueva una vez confirmado que todo funciona, para evitar el mismo bloqueo que tuvimos al terminar la anterior.
