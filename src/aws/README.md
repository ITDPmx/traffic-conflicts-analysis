# Configurar AWS functions

En este proyecto, las lambda functions fueron utilizadas para integrar la página web con el backend de la aplicación.

Las siguientes 3 lambdas fueron creadas:

1. start_instance: Prende la máquina ec2 donde se procesa un video, cuando un archivo es subido al bucket mediante la página web. También, envía la request a la api que es levantada dentro del ec2.
2. email: Una vez se suben los archivos con los datos procesados, esta función envía un correo a la persona que subió el video, a la cual corresponden los datos procesados.
3. Excel: Esta función genera un excel que contiene los datos de la inferencia, en un formato dado. Al final, se descartó esta opción ya que el formato contaba con diferentes datos a los obtenidos durante el procesamiento. Integrarlo implicaría recabar los datos, formatearlos, y generar el excel, que tendría que ser subido a un bucket para poder compartirlo con el usuario.

## Aspectos relevantes para trabajar con lambdas

- La manera actual de subir código a AWS es mediante archivos .zip. Cada function cuenta con un `deploy.sh` que se puede ejecutar para generar el .zip con el código fuente.
- Cada lambda function necesita de ciertos permisos, dependiendo de los servicios con los que interactue.
  - Si se corre una lambda sin permisos, la consola de aws informará de los permisos necesarios, los cuales tienen que ser configurados en el rol de la lambda.
  - Se pueden consultar los roles de las lambdas en la consola de aws, en la sección de IAM.
    - Entrar a la función de lambda, entrar a configuración, y en la sección de permisos, se puede ver el rol que tiene asignado. Haciendo clic en el rol, se puede ver la política y todos los permisos que tiene.
- La función de email tiene algunos archivos en el .gitignore, ya que contiene información sensible. Estos archivos son necesarios para que la función pueda enviar correos electrónicos. La función cuenta con un README.md que explica cómo configurar estos archivos.

## Triggers

- Las lambdas pueden ser disparadas por diferentes eventos. En este caso, las lambdas son disparadas por eventos de S3.
- Para configurar un trigger, se debe ir a la sección de la lambda en la consola de aws, y en la sección de triggers, se puede configurar el evento que dispara la función mediate la GUI.
- En este caso, las lambdas son disparadas por eventos de S3, que son generados cuando un archivo es subido al bucket. El nombre del bucket y del archivo son pasados como argumentos a la función.

