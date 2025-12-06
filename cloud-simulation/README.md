# Cloud Simulation Directory

This folder contains configuration files and setup instructions for simulating cloud services locally. This allows you to develop and test the multi-agent system without requiring actual cloud infrastructure, reducing costs and enabling faster iteration.

## Overview

The cloud simulation setup uses:

- **LocalStack**: Simulates AWS services (S3, DynamoDB, Lambda, EC2, etc.) locally
- **MinIO**: Provides S3-compatible object storage for local development

## LocalStack

LocalStack provides a fully functional local AWS cloud stack. It supports most AWS services and allows you to test your agents' cloud interactions locally.

### Setup

1. **Install LocalStack**:

   ```bash
   pip install localstack
   ```

   Or using Docker:

   ```bash
   docker pull localstack/localstack
   ```

2. **Configuration**:

   Configuration files are located in `/cloud-simulation/localstack/`. The main configuration file defines which AWS services to simulate.

3. **Start LocalStack**:

   ```bash
   localstack start
   ```

   Or using Docker:

   ```bash
   docker run -d -p 4566:4566 -p 4571:4571 localstack/localstack
   ```

4. **Configure AWS CLI**:

   ```bash
   aws configure set aws_access_key_id test
   aws configure set aws_secret_access_key test
   aws configure set default.region us-east-1
   aws configure set endpoint-url http://localhost:4566
   ```

### Supported Services

LocalStack supports many AWS services including:

- **S3**: Object storage
- **DynamoDB**: NoSQL database
- **Lambda**: Serverless functions
- **EC2**: Virtual machines (limited simulation)
- **SQS**: Message queuing
- **SNS**: Notifications
- **IAM**: Identity and access management
- **CloudWatch**: Monitoring and logging

### Usage Example

```python
import boto3

# Connect to LocalStack
s3_client = boto3.client(
    's3',
    endpoint_url='http://localhost:4566',
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

# Create a bucket
s3_client.create_bucket(Bucket='test-bucket')

# Upload a file
s3_client.upload_file('test.txt', 'test-bucket', 'test.txt')
```

## MinIO

MinIO is an S3-compatible object storage service that can run locally or in the cloud.

### Setup

1. **Install MinIO**:

   Using Docker:

   ```bash
   docker run -d -p 9000:9000 -p 9001:9001 \
     -e "MINIO_ROOT_USER=minioadmin" \
     -e "MINIO_ROOT_PASSWORD=minioadmin" \
     minio/minio server /data --console-address ":9001"
   ```

2. **Configuration**:

   Configuration files are located in `/cloud-simulation/minio/`.

3. **Access MinIO Console**:

   Open http://localhost:9001 in your browser and log in with:
   - Username: `minioadmin`
   - Password: `minioadmin`

### Usage Example

```python
from minio import Minio
from minio.error import S3Error

# Create MinIO client
client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# Create a bucket
client.make_bucket("test-bucket")

# Upload a file
client.fput_object("test-bucket", "test.txt", "test.txt")
```

## Integration with Agents

Agents can interact with simulated cloud services just as they would with real AWS services. The main difference is the endpoint URL:

- **LocalStack**: `http://localhost:4566`
- **MinIO**: `http://localhost:9000`

### Environment Variables

Set these environment variables to use local cloud simulation:

```bash
export AWS_ENDPOINT_URL=http://localhost:4566
export MINIO_ENDPOINT=http://localhost:9000
export USE_LOCAL_CLOUD=true
```

## Docker Compose Setup

A complete local cloud simulation environment can be started using Docker Compose:

```bash
cd docker/docker-compose
docker-compose up -d
```

This will start:
- LocalStack
- MinIO
- PostgreSQL
- MongoDB
- Redis
- RabbitMQ (for message queuing)

## Testing with Simulated Cloud

1. **Start LocalStack and MinIO**:

   ```bash
   docker-compose up -d
   ```

2. **Run Agents**:

   ```bash
   cd ../agents
   python task_solving_agent.py
   ```

3. **Verify Cloud Interactions**:

   Check LocalStack logs or MinIO console to verify that agents are interacting with simulated cloud services correctly.

## Troubleshooting

### LocalStack Issues

- **Port conflicts**: Ensure ports 4566 and 4571 are available
- **Service not available**: Check LocalStack logs for service initialization errors
- **Connection refused**: Verify LocalStack is running and accessible

### MinIO Issues

- **Port conflicts**: Ensure ports 9000 and 9001 are available
- **Access denied**: Verify credentials match configuration
- **Bucket creation fails**: Check MinIO logs for errors

## Migration to Real Cloud

When ready to deploy to real cloud infrastructure:

1. Update endpoint URLs in agent configurations
2. Configure real AWS credentials
3. Update IAM roles and permissions
4. Test with real cloud services in a staging environment

## Related Documentation

- Docker setup: `/docker/README.md`
- Agent configuration: `/config/cloud-config/`
- Architecture documentation: `/docs/architecture/`

