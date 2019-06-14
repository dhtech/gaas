from kubernetes import client
from games.defaults import (
    GameSpec, 
    Param, 
    ParamException, 
    ParamTypes
)

class CSSGameSpec(GameSpec):

    id="css"
    name="Counter Strike: Source"
    params=[Param(
        id="SV_HOSTNAME",
        type=ParamTypes.STRING,
        name="Server Hostname",
        description="Shows up in server list",
    ), Param(
        id="SV_PASSWORD",
        type=ParamTypes.STRING,
        name="Server Password",
        description="Password for the server",
        optional=True,
    ), Param(
        id="RCON_PASSWORD",
        type=ParamTypes.STRING,
        name="Server Admin Password",
        description="Password for the RCON server",
    ), Param(
        id="BOT_QUOTA",
        type=ParamTypes.INT,
        name="Number of bots",
        description="Number of bots",
        default=0,
    )]

    def get_param_constraints(self):
        return {
            "SV_HOSTNAME": [(lambda v: len(v) > 5, "Steam server name needs to be more than 5 chars.")],
            "SV_PASSWORD": [],
            "RCON_PASSWORD": [(lambda v: len(v) > 10, "RCON Password must be at least 10 characters.")],
            "BOT_QUOTA": [
                (lambda v: int(v) >= 0, "Number of bots needs to be bigger or equal to 0."),
                (lambda v: int(v) < 10, "Number of bots cannot be bigger than 10.")
            ],
        }


    def make_deployment(self, params):
        env=[client.V1EnvVar(
                name=k,
                value=str(v)
        ) for k, v in params.items()]
        env.extend([client.V1EnvVar(
            name="LAN",
            value="0"
        ), client.V1EnvVar(
            name="MAP",
            value="de_dust2"
        ), client.V1EnvVar(
            name="BOT_QUOTA_MODE",
            value="fill"
        )])
        for e in env:
            if e.name == "SV_HOSTNAME":
                e.value = "[dhtech] " + e.value
        return [client.V1Container(
            env=env,
            image="rctl/gaas-css:1560416579",
            name="csgo",
            resources=client.V1ResourceRequirements(
                limits={
                    "cpu": "4",
                    "memory": "32G"
                },
                requests={
                    "cpu": "2",
                    "memory": "16G"
                }
            ),
            ports=[client.V1ContainerPort(
                container_port=27015,
                protocol="UDP"
            ), client.V1ContainerPort(
                container_port=27020,
                protocol="UDP"
            ), client.V1ContainerPort(
                container_port=27015,
                protocol="TCP"
            ), client.V1ContainerPort(
                container_port=27020,
                protocol="TCP"
            )]
        )]

    def make_service(self, params):
        return [client.V1ServicePort(
                name="port1",
                port=27015,
                target_port=27015,
                protocol="UDP"
            ), client.V1ServicePort(
                name="port2",
                port=27020,
                target_port=27020,
                protocol="UDP"
            ),client.V1ServicePort(
                name="port3",
                port=27015,
                target_port=27015,
                protocol="TCP"
            ), client.V1ServicePort(
                name="port4",
                port=27020,
                target_port=27020,
                protocol="TCP"
            )]