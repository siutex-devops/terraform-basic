terraform {
  required_version = ">=0.13"
  backend "s3" {
    bucket = "myapp-test1"
    key = "terraform/state.tfstate"
    region = "us-east-1"
    
  }
}

provider "aws" {
    region = "us-east-1"
}

resource "aws_vpc" "myapp-vpc" {
    cidr_block = var.vpc_cidr_block
    tags = {
        Name = "${var.env_prefix}-vpc"
    }
}

module "myapp-subnet" {
    source = "./modules/subnet"
    subnet_cidr_block = var.subnet_cidr_block
    avail_zone = var.avail_zone
    env_prefix = var.env_prefix
    vpc_id = aws_vpc.myapp-vpc.id
    default_route_table_id = aws_vpc.myapp-vpc.default_route_table_id
}

module "myapp-server" {
    source = "./modules/webserver"
    vpc_id = aws_vpc.myapp-vpc.id
    my_ip = var.my_ip
    env_prefix = var.env_prefix
    image_name = var.image_name
    public_key_location = var.public_key_location
    instance_type = var.instance_type
    subnet_id = module.myapp-subnet.subnet.id
    avail_zone = var.avail_zone
}

module "myapp-role" {
  source = "./modules/iam"
  role_name = var.role_name
}

resource "aws_ecs_cluster" "cluster" {
  name = "python-http-server-cluster"
}

resource "aws_ecs_task_definition" "task" {
  family                   = "python-http-server-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = module.myapp-role.iam-role.arn

  container_definitions = jsonencode([{
    name  = "python-http-server"
    image = "siutex/python-server"
    portMappings = [{
      containerPort = 8080
      hostPort      = 8080
      protocol      = "tcp"
    }]
  }])
}

resource "aws_ecs_service" "service" {
  name            = "python-http-server-service"
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    assign_public_ip = true
    subnets          = [module.myapp-subnet.subnet.id]
    security_groups  = module.myapp-server.instance.vpc_security_group_ids
  }
}