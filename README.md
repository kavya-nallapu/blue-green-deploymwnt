# Blue-Green Deployment (Python + Docker + Kubernetes + AWS + Jenkins + NGINX)

A complete CI/CD demo for zero-downtime deployments using the blue-green strategy.

## Architecture

```
Developer -> Jenkins -> AWS ECR -> EKS (blue/green) -> NGINX Ingress -> Users
```

## How Blue-Green Works

1. **Blue** and **Green** are two identical environments running the same app.
2. Only one color receives live traffic at a time via `myapp-active` Service.
3. Jenkins deploys the new version to the **inactive** color.
4. After smoke tests pass, traffic is switched by updating the Service selector.
5. Rollback = switch selector back to the previous color.

## Project Structure

```
blue-green/
├── app/main.py              # FastAPI app with /health endpoint
├── tests/test_app.py        # Unit tests
├── k8s/                     # Kubernetes manifests
│   ├── namespace.yaml
│   ├── deployment-blue.yaml
│   ├── deployment-green.yaml
│   ├── service-blue.yaml
│   ├── service-green.yaml
│   ├── service-active.yaml  # Traffic switch point
│   └── ingress.yaml         # NGINX Ingress
├── Dockerfile
├── Jenkinsfile              # CI/CD pipeline
└── requirements.txt
```

## Prerequisites

- AWS EKS cluster
- AWS ECR repository
- NGINX Ingress Controller on EKS
- Jenkins with Docker, kubectl, awscli
- Update `AWS_ACCOUNT_ID`, `AWS_REGION`, and ECR image URLs in manifests

## Deploy to Kubernetes

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment-blue.yaml
kubectl apply -f k8s/deployment-green.yaml
kubectl apply -f k8s/service-blue.yaml
kubectl apply -f k8s/service-green.yaml
kubectl apply -f k8s/service-active.yaml
kubectl apply -f k8s/ingress.yaml
```

## Run Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
curl http://localhost:8000/health
```

## Run Tests

```bash
pytest -q
```

## Jenkins Pipeline Stages

1. Checkout code
2. Run tests
3. Build & push Docker image to ECR
4. Detect active/inactive color
5. Deploy to inactive color
6. Smoke test inactive color
7. Switch traffic (patch `myapp-active` selector)
8. Post-switch health check
9. Auto-rollback on failure
