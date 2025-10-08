# Development Environment Input Variables

variable "backend_image_uri" {
  description = "URI for the backend container image"
  type        = string
}

variable "frontend_image_uri" {
  description = "URI for the frontend container image"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}
