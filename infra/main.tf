terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------

variable "aws_region" {
  default = "us-east-1"
}

variable "db_password" {
  description = "Contraseña para RDS — pasar con TF_VAR_db_password"
  sensitive   = true
}

variable "ec2_sg_id" {
  description = "Security Group ID de la instancia EC2 de PacFeed"
  default     = "sg-0086045a00ae500bd"
}

# ---------------------------------------------------------------------------
# S3 Bucket — privado, cifrado, acceso público bloqueado
# ---------------------------------------------------------------------------

resource "aws_s3_bucket" "pacfeed" {
  bucket        = "pacfeed-media-${data.aws_caller_identity.current.account_id}"
  force_destroy = true
}

data "aws_caller_identity" "current" {}

resource "aws_s3_bucket_public_access_block" "pacfeed" {
  bucket                  = aws_s3_bucket.pacfeed.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "pacfeed" {
  bucket = aws_s3_bucket.pacfeed.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# ---------------------------------------------------------------------------
# Security Group para RDS — solo desde EC2
# ---------------------------------------------------------------------------

data "aws_vpc" "default" {
  default = true
}

resource "aws_security_group" "rds" {
  name        = "pacfeed-rds-sg"
  description = "Permite PostgreSQL solo desde la EC2 de PacFeed"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description     = "PostgreSQL desde EC2 PacFeed"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.ec2_sg_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ---------------------------------------------------------------------------
# Subnet group para RDS
# ---------------------------------------------------------------------------

data "aws_subnets" "default" {
  filter {
    name   = "default-for-az"
    values = ["true"]
  }
}

resource "aws_db_subnet_group" "pacfeed" {
  name       = "pacfeed-db-subnet-group"
  subnet_ids = data.aws_subnets.default.ids
}

# ---------------------------------------------------------------------------
# RDS PostgreSQL — cifrado, sin acceso público
# ---------------------------------------------------------------------------

resource "aws_db_instance" "pacfeed" {
  identifier             = "pacfeed-db"
  engine                 = "postgres"
  engine_version         = "15"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  storage_type           = "gp2"
  storage_encrypted      = true
  db_name                = "pacfeed"
  username               = "pacfeed_user"
  password               = var.db_password
  publicly_accessible    = false
  skip_final_snapshot    = true
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.pacfeed.name

  # Monitoreo mejorado desactivado (no soportado en Learner Lab)
  monitoring_interval = 0
}

# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------

output "s3_bucket_name" {
  value = aws_s3_bucket.pacfeed.bucket
}

output "rds_endpoint" {
  value = aws_db_instance.pacfeed.endpoint
}
