#!/bin/bash
set -e
VERSION=$(date +%s)
docker build -t quay.io/dhtech/gaas-portal:dev-$VERSION .
docker push quay.io/dhtech/gaas-portal:dev-$VERSION
kubectl --record deployment.apps/gaas-portal set image deployment.v1.apps/gaas-portal gaas-portal=quay.io/dhtech/gaas-portal:dev-$VERSION
