import uuid
import ipaddress
from kubernetes import client
from games.enabled import get_game_by_id

NAMESPACE="default"
EXTERNAL_PREFIX="77.80.229.128/25"

def list(u_ip):
    services = client.CoreV1Api().list_service_for_all_namespaces(
        watch=False,
        label_selector="app=gaas"
    )
    deployments = client.AppsV1Api().list_deployment_for_all_namespaces(
        watch=False,
        label_selector="app=gaas"
    )
    pods = client.CoreV1Api().list_pod_for_all_namespaces(
        watch=False,
        label_selector="app=gaas"
    )
    servers={}
    for service in services.items:
        uid=service.metadata.labels["server"]
        candelete=False
        ip=service.spec.external_i_ps[0]
        game=service.metadata.labels["game"]
        name=get_game_by_id(game).name
        servers[uid] = {
            "uid":service.metadata.labels["server"],
            "game": game,
            "gamename": name,
            "ip": ip,
            "ports": [
                "{}/{}".format(port.protocol, port.port) 
                for port in service.spec.ports
            ]
        }
    for deploy in deployments.items:
        uid=deploy.metadata.labels["server"]
        if uid not in servers:
            continue
        if deploy.metadata.labels["creator"] == u_ip:
            servers[uid]["candelete"] = "yes"
        print(deploy.metadata.labels)
        for container in deploy.spec.template.spec.containers:
            if container.env:
                servers[uid]["env"]={
                    env.name: env.value
                    for env in container.env
                }
    for pod in pods.items:
        uid=pod.metadata.labels["server"]
        if uid not in servers:
            continue
        servers[uid]["pods"]=[{
            "ready": status.ready,
            "image": status.image,
            "restart_count": status.restart_count,
            "state": status.state.waiting.reason if status.state.waiting is not None else None,
        } for status in pod.status.container_statuses]
    
    return servers


def delete(uid, ip):
    deployment = client.AppsV1Api().read_namespaced_deployment_status(
        name="gaas-{}".format(uid),
        namespace=NAMESPACE,
    )
    if deployment.metadata.labels["creator"] != ip:
        raise Exception("You did not create this job")
    client.AppsV1Api().delete_namespaced_deployment(
        name="gaas-{}".format(uid),
        namespace=NAMESPACE,
    )
    client.CoreV1Api().delete_namespaced_service(
        name="gaas-{}".format(uid),
        namespace=NAMESPACE,
    )


def add(ip, game_id, params):
    game=get_game_by_id(game_id)
    game.validate_params(params)
    uid=uuid.uuid4().hex[:12]
    name="gaas-{}".format(uid)
    labels={
        "app": "gaas",
        "game": game_id,
        "server": uid,
        "creator": ip,
    }
    metadata=client.V1ObjectMeta(
        labels=labels,
        name=name,
    )
    ip_ext=alloc_ip()
    extra_env=[client.V1EnvVar(
        name="IP_ALLOC",
        value=ip_ext
    ), client.V1EnvVar(
        name="IP_CREATOR",
        value=ip
    )]
    containers = game.make_deployment(params)
    for container in containers:
        if container.env:
            container.env.extend(extra_env)
        else:
            container.env = extra_env
        if not container.resources:
            container.resources=client.V1ResourceRequirements(
                limits={
                    "cpu": "4",
                    "memory": "32G"
                },
                requests={
                    "cpu": "2",
                    "memory": "16G"
                }
            )
    deployment=client.V1Deployment(
            spec=client.V1DeploymentSpec(
                replicas=1,
                selector=client.V1LabelSelector(
                    match_labels=labels,
                ),
                template=client.V1PodTemplateSpec(
                    spec=client.V1PodSpec(
                        containers=containers,
                        affinity=client.V1Affinity(
                            node_affinity=client.V1NodeAffinity(
                                required_during_scheduling_ignored_during_execution=client.V1NodeSelector(
                                    node_selector_terms=[
                                        client.V1NodeSelectorTerm(
                                            match_expressions=[
                                                client.V1NodeSelectorRequirement(
                                                    key="kubernetes.io/role",
                                                    operator="NotIn",
                                                    values=["shared"]
                                                )
                                            ]
                                        )
                                    ]
                                )
                            )
                        )
                    )
                )
            )
    )
    service=client.V1Service(
        spec=client.V1ServiceSpec(
            type="ClusterIP",
            selector=labels,
            ports=game.make_service(params),
            external_i_ps=[ip_ext],
        )
    )
    deployment.metadata=metadata
    deployment.spec.template.metadata=metadata
    service.metadata=metadata
    service.metadata.annotations={
			#"kube-router.io/service.dsr": "tunnel"
		}

    client.AppsV1Api().create_namespaced_deployment(
        namespace=NAMESPACE, 
        body=deployment,
    )

    service_resp = client.CoreV1Api().create_namespaced_service(
        namespace=NAMESPACE,
        body=service,
    )
    
    return {"uid": uid, "ip": ip}

def alloc_ip():
    space=ipaddress.ip_network(EXTERNAL_PREFIX)
    reserved=[]
    services = client.CoreV1Api().list_service_for_all_namespaces(watch=False)
    for service in services.items:
        if service.spec.external_i_ps:
            reserved.extend(service.spec.external_i_ps)
    for ip in space: 
        if str(ip) not in reserved:
            print("Alloc ip {}".format(ip))
            return str(ip)
    raise Exception("Cluster ran out of available IPs")