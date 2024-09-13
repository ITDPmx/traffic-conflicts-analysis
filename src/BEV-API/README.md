# Birds Eye View API

API to transform image into birds eye view

## Run

1. Build docker image:

``` bash
docker build -t birds-eye-view .
```

2. Run docker

``` bash
docker run -it --gpus all -u $(id -u):$(id -g) --rm -p 8000:8000  -v $(pwd):/app -w /app --env DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix birds-eye-view /bin/bash
```

3. Run API
```bash
python3 main.py
```

## Development
Based on [SAmmarAbbas/birds-eye-view](https://github.com/SAmmarAbbas/birds-eye-view/tree/master)

And development from [Emiliano Flores](https://github.com/EmilianoHFlores)