# TCA Dashboard

Este dashboard sirve para subir, visualizar, descargar, y analizar videos de tráfico. Permite interactuar con el sistema de análisis de conflictos de tráfico, y visualizar los resultados de la inferencia.

## Environment

Para correr el proyecto se necesita establecer variables de entorno, utilizadas para la autenticación, para indicar recursos de AWS, y para indicar la base de datos a utilizar.

El archivo `.env.example` contiene las variables de entorno necesarias para correr el proyecto. Para correr el proyecto, se debe copiar el archivo `.env.example` a `.env`, y completar las variables de entorno con los valores correspondientes. El archivo `src/env.js` contiene las validaciones que se realizan a cada variable de entorno y desde donde puede ser accedida cada una.

La base de datos utilizada es postgresql. Se puede modificar el tipo de la base de datos, pero podría implicar cambios en el código. Para cambiar la base de datos se tendría que modificar el archivo `schema.prisma`, que genera el cliente ORM de Prisma que se usa a lo largo del proyecto.

Nota: en caso de agregar más variables de entorno, se debe agregar la validación correspondiente en `src/env.js` y especificarlas en `amplify.yml`.

## API

La API de este proyecto se encuentra en el directorio `src/app/api/`. La api cuenta con los siguientes endpoints que son llamados desde AWS:

- `default_matrix`: Dado un id de un video, retorna si se debería usar la matriz por defecto (preferencia asignada por usuario a la hora de subir el video).
- `progress`: Actualiza el progreso de procesamiento de un video. Recibe el id del video y el progreso actual.
- `email_data`: Dado un id de un video, retorna datos básicos para enviar un correo electrónico (email de usuario, nombre).


## Deploy

La plataforma utiliza AWS Amplify para el deploy. El archivo `amplify.yml` contiene la configuración necesaria para el deploy. Asimismo, la imagen utilizada para el deploy es: `public.ecr.aws/docker/library/node:20.16-bookworm`. Esta imagen puede ser especificada desde `amplify > Proyecto > Hosting > Build settings > Build Image Settings`. No se utilizó la imagen default porque algunas dependencias del proyecto no eran compatibles con la versión de node default.