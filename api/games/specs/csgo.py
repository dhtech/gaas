from kubernetes import client
from games.defaults import (
    GameSpec, 
    Param, 
    ParamException, 
    ParamTypes
)

class CSGoGameSpec(GameSpec):

    id="csgo"
    name="Counter Strike: Global Offensive"
    params=[Param(
        id="SV_HOSTNAME",
        type=ParamTypes.STRING,
        name="Server Hostname",
        description="Shows up in server list",
    ), Param(
        id="SV_PASSWORD",
        type=ParamTypes.STRING,
        optional=True,
        name="Server Password",
        description="Password for the server",
    ), Param(
        id="RCON_PASSWORD",
        type=ParamTypes.STRING,
        name="Server Admin Password",
        description="Password for the RCON server",
    ), Param(
        id="SERVER_TOKEN",
        type=ParamTypes.STRING,
        name="Steam server token (get at tinyurl.com/nt8to3l)",
        description="Create on here https://steamcommunity.com/dev/managegameservers",
    )]

    def get_param_constraints(self):
        return {
            "SV_HOSTNAME": [(lambda v: len(v) > 5, "Steam server name needs to be more than 5 chars.")],
            "SV_PASSWORD": [],
            "RCON_PASSWORD": [(lambda v: len(v) > 10, "RCON Password must be at least 10 characters.")],
            "SERVER_TOKEN": [(lambda v: len(v) == 32, "Steam server token needs to be exactly 32 characters.")]
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
        )])
        for e in env:
            if e.name == "SV_HOSTNAME":
                e.value = "[dhtech] " + e.value
        return [client.V1Container(
            env=env,
            image= "rctl/gaas-csgo",
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