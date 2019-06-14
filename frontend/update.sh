#!/bin/bash
VERSION=$(date +%s)
docker build -t rctl/gaas-portal:$VERSION .
docker push rctl/gaas-portal:$VERSION
kubectl --record deployment.apps/gaas-portal set image deployment.v1.apps/gaas-portal gaas-portal=rctl/gaas-portal:$VERSION