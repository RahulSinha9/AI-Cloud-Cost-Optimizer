variable "aws_region" {
  type        = string
  description = "AWS deployment region"
  default     = "ap-south-1"
}

variable "project_name" {
  type        = string
  description = "Project name used for tags and resource names"
  default     = "ai-cloud-cost-optimizer"
}
