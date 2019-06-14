from kubernetes import client
from games.defaults import (
    GameSpec, 
    Param, 
    ParamException, 
    ParamTypes
)

class NginxGameSpec(GameSpec):

    id="nginx"
    name="A nginx server (not really a game)"

    def make_deployment(self, params):
        return [client.V1Container(
            env=[client.V1EnvVar(
                name=k,
                value=str(v)
            ) for k, v in params.items()],
            image="nginx:1.17.0",
            name="nginx",
            resources=client.V1ResourceRequirements(
                limits={
                    "cpu": "500m",
                    "memory": "1G"
                },
                requests={
                    "cpu": "100m",
                    "memory": "500M"
                }
            ),
            ports=[client.V1ContainerPort(
                container_port=80,
                protocol="TCP"
            )]
        )]

    def make_service(self, params):
        return [client.V1ServicePort(
            port=80,
            target_port=80,
        )]