# Crowd Counting Dashboard
El frontend y el backend se corren al mismo tiempo.
## Frontend
### Requerimientos

 - [Node.js](https://nodejs.org/en/download)
 - [React](https://es.react.dev/)
 - [Yarn](https://yarnpkg.com/)

### Instalación
Desde la consola cambiar de directorio:

    cd src/dashboard
Instalar modulos de yarn

    yarn install
### Como correr
Cambiar el url del backend en `.env`:

    REACT_APP_BACKEND_URL=http://localhost:8000
    
En la carpeta `src/dashboard` correr:

    yarn start

  
## Backend
### Requerimientos

 - [Docker](https://www.docker.com/)
 - [Python](https://www.python.org/)
### Como correr

Desde la consola cambiar de directorio:

    cd src/backend
Correr daemon de Docker, despues correr el siguiente comando en la consola:

    docker build --tag app . && docker run --publish 8000:5000 app

