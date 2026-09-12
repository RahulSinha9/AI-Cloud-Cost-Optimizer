# AI Cloud Cost Optimizer

AI-assisted **AWS cloud cost anomaly detection and optimization** for DevOps and FinOps workflows.

## What it does

The service ingests daily cloud-cost points, detects statistically significant upward spikes, produces conservative optimization recommendations, exposes Prometheus metrics, and can optionally use an OpenAI-compatible LLM for an operator-facing summary.

```text
AWS Cost Explorer / JSON
          |
          v
   Daily cost series
          |
          v
 Statistical anomaly detector
          |
          v
 Optimization recommender ----> Prometheus metrics
          |
          v
 Optional AI advisor
          |
          v
 Human-readable analysis
```

## Features

- FastAPI endpoints: `/healthz`, `/readyz`, `/metrics`, `/v1/analyze`, `/v1/aws/daily`.
- Configurable z-score anomaly threshold.
- Budget overrun recommendations.
- Service spend concentration recommendations.
- Optional AWS Cost Explorer integration.
- Optional OpenAI-compatible AI advisor, disabled by default.
- Deterministic fallback summary, so the core workflow does not depend on an LLM.
- Prometheus request, anomaly, and latency metrics.
- Non-root Docker container with a health check.
- Kubernetes Deployment, Service, HPA, and ServiceMonitor manifests.
- Terraform baseline for ECR, CloudWatch Logs, task execution IAM, and least-privilege Cost Explorer access.
- GitHub Actions CI for tests, coverage, linting, and container build validation.

## Quick start

Python 3.11+ is required.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs` for the OpenAPI UI.

### Sample analysis

```bash
curl -X POST http://localhost:8000/v1/analyze \
  -H 'content-type: application/json' \
  --data @sample_costs.json
```

## Docker

```bash
docker compose up --build
```

Then:

```bash
./scripts/smoke_test.sh
```

## Tests and lint

```bash
make install
make test
make lint
```

Coverage is configured to fail below 85%.

## AWS Cost Explorer

Enable with:

```bash
COST_EXPLORER_ENABLED=true
AWS_REGION=ap-south-1
```

The application expects credentials with `ce:GetCostAndUsage`. Prefer workload IAM roles over static credentials.

```text
GET /v1/aws/daily
```

## Optional AI advisor

Any provider implementing an OpenAI-compatible `/chat/completions` API can be used.

```bash
AI_ENABLED=true
AI_BASE_URL=https://your-provider.example/v1
AI_MODEL=your-model
AI_API_KEY=...
```

The deterministic recommender remains the source of quantitative recommendations. The LLM only refines the operator-facing summary and must not be treated as an authorization engine.

## Kubernetes

Build/publish an image and replace the image value in `k8s/deployment.yaml`.

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
```

Apply `k8s/servicemonitor.yaml` only when the Prometheus Operator CRD is installed.

## Terraform

```bash
cd terraform
terraform init
terraform plan
```

The Terraform module is intentionally account-neutral: it provisions reusable application resources but leaves VPC, load balancer, and ECS cluster topology to your platform layer.

## Security

- `.env` and Terraform state files are ignored.
- Container runs as UID 10001.
- Kubernetes disables privilege escalation and drops Linux capabilities.
- Cost Explorer role grants only `ce:GetCostAndUsage`.
- Savings figures are heuristics and should be validated against utilization and billing data.
- Recommendations are advisory; no mutation of AWS resources is performed.

## Layout

```text
.
├── app/
├── k8s/
├── terraform/
├── tests/
├── .github/workflows/ci.yml
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
└── sample_costs.json
```

## Next production extensions

- PostgreSQL or S3/Athena persistence.
- AWS Organizations multi-account aggregation.
- Slack/Teams notifications.
- Cost allocation tags and owner attribution.
- AWS Compute Optimizer integration.
- OpenTelemetry traces.
- Policy-as-code gates before any future automated changes.
