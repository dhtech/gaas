#!/bin/bash
VERSION=$(date +%s)
docker build -t rctl/gaas-api:$VERSION .
docker push rctl/gaas-api:$VERSION
kubectl --record deployment.apps/gaas-api set image deployment.v1.apps/gaas-api gaas-api=rctl/gaas-api:$VERSION

