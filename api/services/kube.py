from kubernetes import config


def init():
    try:
        config.load_incluster_config()
    except Exception as e:
        print("Failed to init k8s (in-cluster)")
        print(str(e))
        config.load_kube_config()
    