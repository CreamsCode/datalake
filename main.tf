provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "main_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "MainVPC"
  }
}

resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.main_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "us-east-1a"
  tags = {
    Name = "PublicSubnet"
  }
}

resource "aws_subnet" "private_subnet" {
  vpc_id                  = aws_vpc.main_vpc.id
  cidr_block              = "10.0.2.0/24"
  map_public_ip_on_launch = false
  availability_zone       = "us-east-1a"
  tags = {
    Name = "PrivateSubnet"
  }
}

resource "aws_internet_gateway" "internet_gateway" {
  vpc_id = aws_vpc.main_vpc.id
  tags = {
    Name = "InternetGateway"
  }
}

resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.main_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.internet_gateway.id
  }
  tags = {
    Name = "PublicRouteTable"
  }
}

resource "aws_route_table_association" "public_subnet_association" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_route_table.id
}

resource "aws_security_group" "mongodb_cluster" {
  vpc_id = aws_vpc.main_vpc.id
  tags = {
    Name = "MongoDBSecurityGroup"
  }

  ingress {
    description = "MongoDB access"
    from_port   = 27017
    to_port     = 27019
    protocol    = "tcp"
    cidr_blocks = [aws_subnet.public_subnet.cidr_block]
  }

  ingress {
    description = "SSH Access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "listener_security" {
  vpc_id = aws_vpc.main_vpc.id
  tags = {
    Name = "ListenerSecurityGroup"
  }

  ingress {
    description = "SSH Access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Instances: Config Server, Mongos, Shards
resource "aws_instance" "config_server" {
  ami           = "ami-05576a079321f21f8"
  instance_type = "t2.micro"
  key_name      = "vockey"
  subnet_id     = aws_subnet.public_subnet.id
  vpc_security_group_ids = [aws_security_group.mongodb_cluster.id]
  iam_instance_profile   = "EMR_EC2_DefaultRole"
  tags = {
    Name = "MongoDB-Config-Server"
  }
  user_data = <<-EOF
    #!/bin/bash
    echo '[mongodb-org-8.0]' | sudo tee /etc/yum.repos.d/mongodb-org-8.0.repo
    echo 'name=MongoDB Repository' | sudo tee -a /etc/yum.repos.d/mongodb-org-8.0.repo
    echo 'baseurl=https://repo.mongodb.org/yum/amazon/2023/mongodb-org/8.0/x86_64/' | sudo tee -a /etc/yum.repos.d/mongodb-org-8.0.repo
    echo 'gpgcheck=1' | sudo tee -a /etc/yum.repos.d/mongodb-org-8.0.repo
    echo 'enabled=1' | sudo tee -a /etc/yum.repos.d/mongodb-org-8.0.repo
    echo 'gpgkey=https://pgp.mongodb.com/server-8.0.asc' | sudo tee -a /etc/yum.repos.d/mongodb-org-8.0.repo
    dnf install -y mongodb-org mongodb-mongosh-shared-openssl3 openssl mongodb-org-database-tools-extra mongodb-database-tools mongodb-org-tools mongodb-org-server mongodb-org-mongos mongodb-org-database jq
    sudo rm -f /tmp/mongodb-27017.sock
    sudo chown -R mongod:mongod /var/lib/mongo
    sudo chown -R mongod:mongod /var/log/mongodb
    sudo chmod 700 /var/lib/mongo
    sudo chmod 700 /var/log/mongodb
    echo "sharding.clusterRole: configsvr" | sudo tee -a /etc/mongod.conf
    sudo systemctl enable mongod
    sudo systemctl start mongod
  EOF
}

resource "aws_instance" "mongos_router" {
  ami           = "ami-05576a079321f21f8"
  instance_type = "t2.micro"
  key_name      = "vockey"
  subnet_id     = aws_subnet.public_subnet.id
  vpc_security_group_ids = [aws_security_group.mongodb_cluster.id]
  iam_instance_profile   = "EMR_EC2_DefaultRole"
  tags = {
    Name = "MongoDB-Mongos"
  }
  user_data = <<-EOF
    #!/bin/bash
    echo '[mongodb-org-8.0]' | sudo tee /etc/yum.repos.d/mongodb-org-8.0.repo
    echo 'name=MongoDB Repository' | sudo tee -a /etc/yum.repos.d/mongodb-org-8.0.repo
    echo 'baseurl=https://repo.mongodb.org/yum/amazon/2023/mongodb-org/8.0/x86_64/' | sudo tee -a /etc/yum.repos.d/mongodb-org-8.0.repo
    echo 'gpgcheck=1' | sudo tee -a /etc/yum.repos.d/mongodb-org-8.0.repo
    echo 'enabled=1' | sudo tee -a /etc/yum.repos.d/mongodb-org-8.0.repo
    echo 'gpgkey=https://pgp.mongodb.com/server-8.0.asc' | sudo tee -a /etc/yum.repos.d/mongodb-org-8.0.repo
    dnf install -y mongodb-org mongodb-mongosh-shared-openssl3 openssl mongodb-org-database-tools-extra mongodb-database-tools mongodb-org-tools mongodb-org-server mongodb-org-mongos mongodb-org-database jq
    sudo rm -f /tmp/mongodb-27017.sock
    sudo chown -R mongod:mongod /var/lib/mongo
    sudo chown -R mongod:mongod /var/log/mongodb
    sudo chmod 700 /var/lib/mongo
    sudo chmod 700 /var/log/mongodb
    echo "sharding.clusterRole: mongos" | sudo tee -a /etc/mongod.conf
    sudo systemctl enable mongod
    sudo systemctl start mongod
  EOF
}

resource "aws_instance" "shard" {
  count         = 3
  ami           = "ami-05576a079321f21f8"
  instance_type = "t2.micro"
  key_name      = "vockey"
  subnet_id     = aws_subnet.public_subnet.id
  vpc_security_group_ids = [aws_security_group.mongodb_cluster.id]
  iam_instance_profile   = "EMR_EC2_DefaultRole"
  tags = {
    Name = "MongoDB-Shard-${count.index + 1}"
  }
  user_data = <<-EOF
    #!/bin/bash
    echo '[mongodb-org-8.0]' | sudo tee /etc/yum.repos.d/mongodb-org-8.0.repo
    echo 'name=MongoDB Repository' | sudo tee -a /etc/yum.repos.d/mongodb-org-8.0.repo
    echo 'baseurl=https://repo.mongodb.org/yum/amazon/2023/mongodb-org/8.0/x86_64/' | sudo tee -a /etc/yum.repos.d/mongodb-org-8.0.repo
    echo 'gpgcheck=1' | sudo tee -a /etc/yum.repos.d/mongodb-org-8.0.repo
    echo 'enabled=1' | sudo tee -a /etc/yum.repos.d/mongodb-org-8.0.repo
    echo 'gpgkey=https://pgp.mongodb.com/server-8.0.asc' | sudo tee -a /etc/yum.repos.d/mongodb-org-8.0.repo
    dnf install -y mongodb-org mongodb-mongosh-shared-openssl3 openssl mongodb-org-database-tools-extra mongodb-database-tools mongodb-org-tools mongodb-org-server mongodb-org-mongos mongodb-org-database jq
    sudo rm -f /tmp/mongodb-27017.sock
    sudo chown -R mongod:mongod /var/lib/mongo
    sudo chown -R mongod:mongod /var/log/mongodb
    sudo chmod 700 /var/lib/mongo
    sudo chmod 700 /var/log/mongodb
    echo "sharding.clusterRole: shardsvr" | sudo tee -a /etc/mongod.conf
    sudo systemctl enable mongod
    sudo systemctl start mongod
  EOF
}

resource "aws_instance" "listener" {
  ami           = "ami-05576a079321f21f8"
  instance_type = "t2.micro"
  key_name      = "vockey"
  subnet_id     = aws_subnet.public_subnet.id
  vpc_security_group_ids = [aws_security_group.listener_security.id]
  iam_instance_profile   = "EMR_EC2_DefaultRole"
  tags = {
    Name = "Listener"
  }
  user_data = <<-EOF
    #!/bin/bash
    sudo yum update -y
    sudo yum install -y git python3-pip
    git clone https://github.com/LOS-CREMA/datalake /home/ec2-user/datalake
    cd /home/ec2-user/datalake
    pip3 install -r requirements.txt
    python3 main.py
  EOF
}
