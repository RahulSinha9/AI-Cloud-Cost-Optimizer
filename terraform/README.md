# Terraform deployment scaffold

This directory provisions the baseline AWS resources used by the application:

- Immutable ECR repository with scan-on-push.
- CloudWatch log group with 30-day retention.
- ECS task execution role.
- Least-privilege Cost Explorer role permitting only `ce:GetCostAndUsage`.

The ECS service and network topology are intentionally left to the target platform module because VPC, ALB, subnet, and cluster layouts vary by account.
