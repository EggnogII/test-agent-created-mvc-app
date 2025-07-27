output "load_balancer_dns" {
  description = "DNS name of the application load balancer"
  value       = aws_lb.alb.dns_name
}