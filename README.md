### before

    add terraform.tfvars file with content:
    vpc_cidr_block = "your content"
    subnet_cidr_block = "your content"
    avail_zone = "your content"
    env_prefix = "your content"
    my_ip = "your content"
    instance_type = "your content"
    public_key_location = "your content"
    image_name = "your content"
    role_name = "your content"

### initialize

    terraform init

### preview terraform actions

    terraform plan

### apply configuration with variables

    terraform apply -var-file terraform-dev.tfvars

### destroy a single resource

    terraform destroy -target aws_vpc.myapp-vpc

### destroy everything fromtf files

    terraform destroy

