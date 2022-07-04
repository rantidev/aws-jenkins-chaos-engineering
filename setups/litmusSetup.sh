#! /bin/sh

aws eks --region us-east-1 update-kubeconfig --name c1new

kubectl apply -f https://k8s.io/examples/controllers/nginx-deployment.yaml

kubectl apply -f https://raw.githubusercontent.com/litmuschaos/litmus/2.10.0/mkdocs/docs/2.10.0/litmus-2.10.0.yaml

kubectl patch svc litmusportal-frontend-service -p '{"spec": {"type": "LoadBalancer"}}' -n litmus

kubectl get pods -n litmus -o wide

kubectl edit configmap agent-config -n litmus
