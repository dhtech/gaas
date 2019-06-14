#!/bin/bash
set -e
VERSION=$(date +%s)
docker build -t quay.io/dhtech/gaas-api:dev-$VERSION .
docker push quay.io/dhtech/gaas-api:dev-$VERSION
kubectl --record deployment.apps/gaas-api set image deployment.v1.apps/gaas-api gaas-api=quay.io/dhtech/gaas-api:dev-$VERSION
