# FileCharger

## Cron builder

You can set on debian console:

crontab -e

And to run the logic every 10 minutes, set:

*/10 * * * * /full/path/to/project/FileCharger/cron.sh >> /full/path/to/project/FileCharger/Public/cron/log.cron

## Docker cron

If you prepare you're docker to play like an Application Container, then:

1) You can set a docker CRON shell like:

*/10 * * * * docker run -v /local/path/to/App:/docker/path/to/AppsContainer DOCKER_IMAGE_NAME sh App/docker.sh >> /local/path/to/cron/log.cron

2) Or a docker CRON executable

*/10 * * * * docker run -v /local/path/to/App:/docker/path/to/AppsContainer DOCKER_IMAGE_NAME python3 app.py >> /local/path/to/cron/log.cron

## Cron notes

*) Check that shell files like [cron.sh] has execution permissions

*) Check that CRON log files like [Public/cron/log.cron] has read/write permissions

*) Open and edit [cron.sh] to change the [cd /full/path/to/project/FileCharger/] instruction, for point to YOUR right path project directory

## Cron references

https://es.wikipedia.org/wiki/Cron_(Unix)
