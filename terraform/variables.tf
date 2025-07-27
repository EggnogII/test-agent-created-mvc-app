variable "aws_region" {
  description = "AWS region to deploy resources into"
  type        = string
  default     = "us-west-2"
}

variable "prefix" {
  description = "Prefix used for naming AWS resources"
  type        = string
  default     = "vehicle-decoder"
}

variable "task_port" {
  description = "Port on which the container listens"
  type        = number
  default     = 5000
}

variable "desired_count" {
  description = "Number of ECS tasks to run"
  type        = number
  default     = 1
}

variable "ecs_task_cpu" {
  description = "CPU units for the ECS task"
  type        = number
  default     = 256
}

variable "ecs_task_memory" {
  description = "Memory (MB) for the ECS task"
  type        = number
  default     = 512
}

variable "image_url" {
  description = "Full URI of the Docker image to deploy (e.g. account-id.dkr.ecr.us-west-2.amazonaws.com/repo:tag)"
  type        = string
}
