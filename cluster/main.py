from kubernetes import client, config, utils


def shutdown_cluster(request):
    """
    Deletes all non-system pods in the cluster.
    """
    try:
        # Load Kubernetes configuration for external access
        config.load_kube_config()  # Replaced load_incluster_config with load_kube_config
        v1 = client.CoreV1Api()

        # List all namespaces
        namespaces = v1.list_namespace()
        for ns in namespaces.items:
            namespace = ns.metadata.name

            # Skip system namespaces
            if namespace in ["kube-system", "default", "kube-public"]:
                continue

            # List and delete all pods in the namespace
            pods = v1.list_namespaced_pod(namespace=namespace)
            for pod in pods.items:
                v1.delete_namespaced_pod(
                    name=pod.metadata.name,
                    namespace=namespace,
                    body=client.V1DeleteOptions()
                )

        return "Workloads successfully stopped."

    except Exception as e:
        return f"Error during shutdown: {str(e)}"


def start_cluster(request):
    """
    Applies predefined Kubernetes manifests to start workloads.
    """
    try:
        # Load Kubernetes configuration for external access
        config.load_kube_config()  # Replaced load_incluster_config with load_kube_config
        k8s_client = client.ApiClient()

        # Path to stored YAML manifests
        manifest_files = [
            "/home/ariel/project/flask-deployment.yaml",
            "/home/ariel/project/nodejs-deployment.yaml",
            "/home/ariel/project/flask-service.yaml",
            "/home/ariel/project/nodejs-service.yaml",
        ]

        # Apply each manifest
        for manifest in manifest_files:
            with open(manifest) as f:
                utils.create_from_yaml(k8s_client, yaml_file=f)

        return "Workloads successfully restarted."

    except Exception as e:
        return f"Error during startup: {str(e)}"
