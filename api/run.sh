#!/bin/bash
KUBE_CONFIG="c:/wsl/projects/gaas-kubeconfig.yaml:/root/.kube/config"
docker build -t=gaas:dev . && docker run -p 80:80 --rm -it -v $KUBE_CONFIG gaas:dev
