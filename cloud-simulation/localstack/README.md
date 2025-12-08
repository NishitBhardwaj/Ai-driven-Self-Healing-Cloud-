# LocalStack Setup for Cloud Simulation

This directory contains the LocalStack configuration and setup scripts for simulating AWS services locally. LocalStack provides a fully functional local AWS cloud stack that allows you to develop and test the Self-Healing Cloud system without requiring actual cloud infrastructure.

## What is LocalStack?

LocalStack is a cloud service emulator that runs in a single container on your laptop or in your CI environment. It provides an easy-to-use test/mocking framework for developing Cloud applications. It spins up the following core Cloud APIs on your local machine:

- **S3**: Object storage service
- **Lambda**: Serverless compute service
- **CloudWatch**: Monitoring and observability service
- **EC2**: Virtual machines (limited simulation)
- **DynamoDB**: NoSQL database service
- **SQS**: Message queuing service
- **SNS**: Notification service

## Architecture

```
┌─────────────────────────────────────────┐
│         LocalStack Container             │
│  ┌───────────────────────────────────┐  │
│  │  AWS Services (S3, Lambda, etc.)  │  │
│  └───────────────────────────────────┘  │
│  Port: 4566 (Gateway)                    │
└─────────────────────────────────────────┘
           │
           │ AWS API Calls
           │
┌──────────▼──────────────────────────────┐
│     Self-Healing Agents                 │
│  - Self-Healing Agent                   │
│  - Performance Monitoring Agent          │
│  - Security Agent                        │
│  - Scaling Agent                         │
└─────────────────────────────────────────┘
```

## Prerequisites

- **Docker** and **Docker Compose** installed
- **AWS CLI** installed (for running bootstrap script)
- **curl** (for health checks)
- **zip** (for Lambda deployment packages)

### Install AWS CLI (if not already installed)

**Windows:**
```powershell
# Using Chocolatey
choco install awscli

# Or download from: https://aws.amazon.com/cli/
```

**Linux/Mac:**
```bash
# Using pip
pip install awscli

# Or using package manager
# Ubuntu/Debian: sudo apt-get install awscli
# macOS: brew install awscli
```

## Quick Start

### 1. Start LocalStack

```bash
cd cloud-simulation/localstack
docker-compose up -d
```

This will start:
- **LocalStack** on port `4566`
- **LocalStack UI** on port `8080` (optional web interface)

### 2. Wait for LocalStack to be Ready

```bash
# Check health status
curl http://localhost:4566/_localstack/health

# Or wait automatically (included in bootstrap script)
```

### 3. Run Bootstrap Script

The bootstrap script creates all necessary AWS resources:

```bash
# Make script executable (Linux/Mac)
chmod +x bootstrap.sh

# Run bootstrap
./bootstrap.sh

# On Windows (PowerShell)
bash bootstrap.sh
```

The bootstrap script will:
- ✅ Create S3 buckets for logs, artifacts, and metrics
- ✅ Create DynamoDB tables for events, health checks, and healing actions
- ✅ Deploy a sample Lambda function for testing
- ✅ Create SNS topics for alerts and notifications
- ✅ Create SQS queues for task processing
- ✅ Set up CloudWatch log groups
- ✅ Print environment status

### 4. Verify Setup

```bash
# List S3 buckets
aws --endpoint-url=http://localhost:4566 s3 ls

# List Lambda functions
aws --endpoint-url=http://localhost:4566 lambda list-functions

# List DynamoDB tables
aws --endpoint-url=http://localhost:4566 dynamodb list-tables
```

## Configuration

### Environment Variables

LocalStack uses the following environment variables (set in `docker-compose.yml`):

- `SERVICES`: Comma-separated list of AWS services to enable
- `AWS_DEFAULT_REGION`: Default AWS region (default: `us-east-1`)
- `AWS_ACCESS_KEY_ID`: AWS access key (default: `test`)
- `AWS_SECRET_ACCESS_KEY`: AWS secret key (default: `test`)
- `DEBUG`: Enable debug logging (default: `1`)

### Endpoint URL

All AWS CLI commands must use the LocalStack endpoint:

```bash
aws --endpoint-url=http://localhost:4566 <command>
```

Or configure AWS CLI to use LocalStack by default:

```bash
aws configure set endpoint-url http://localhost:4566
```

## How Agents Connect

Agents connect to LocalStack using the AWS SDK with the LocalStack endpoint URL. Here's how to configure agents:

### Python (boto3)

```python
import boto3

# Create S3 client
s3_client = boto3.client(
    's3',
    endpoint_url='http://localhost:4566',
    aws_access_key_id='test',
    aws_secret_access_key='test',
    region_name='us-east-1'
)

# Create Lambda client
lambda_client = boto3.client(
    'lambda',
    endpoint_url='http://localhost:4566',
    aws_access_key_id='test',
    aws_secret_access_key='test',
    region_name='us-east-1'
)
```

### Go (AWS SDK)

```go
import (
    "github.com/aws/aws-sdk-go/aws"
    "github.com/aws/aws-sdk-go/aws/credentials"
    "github.com/aws/aws-sdk-go/aws/session"
    "github.com/aws/aws-sdk-go/service/s3"
)

sess := session.Must(session.NewSession(&aws.Config{
    Region:      aws.String("us-east-1"),
    Endpoint:    aws.String("http://localhost:4566"),
    Credentials: credentials.NewStaticCredentials("test", "test", ""),
}))

s3Client := s3.New(sess)
```

### Environment Variables for Agents

Set these environment variables in your agent configuration:

```bash
export AWS_ENDPOINT_URL=http://localhost:4566
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1
export USE_LOCAL_CLOUD=true
```

## Testing Functionality

### S3 Operations

```bash
# Create a bucket
aws --endpoint-url=http://localhost:4566 s3 mb s3://test-bucket

# Upload a file
aws --endpoint-url=http://localhost:4566 s3 cp test.txt s3://test-bucket/

# List objects
aws --endpoint-url=http://localhost:4566 s3 ls s3://test-bucket/

# Download a file
aws --endpoint-url=http://localhost:4566 s3 cp s3://test-bucket/test.txt ./
```

### Lambda Operations

```bash
# Invoke the test Lambda function
aws --endpoint-url=http://localhost:4566 lambda invoke \
    --function-name self-healing-test-lambda \
    --payload '{"test": "data"}' \
    response.json

# View response
cat response.json

# View Lambda logs
aws --endpoint-url=http://localhost:4566 logs tail /aws/lambda/self-healing-test-lambda --follow
```

### DynamoDB Operations

```bash
# Put an item
aws --endpoint-url=http://localhost:4566 dynamodb put-item \
    --table-name agent-events \
    --item '{"event_id": {"S": "test-123"}, "timestamp": {"N": "1234567890"}, "message": {"S": "Test event"}}'

# Get an item
aws --endpoint-url=http://localhost:4566 dynamodb get-item \
    --table-name agent-events \
    --key '{"event_id": {"S": "test-123"}, "timestamp": {"N": "1234567890"}}'

# Scan table
aws --endpoint-url=http://localhost:4566 dynamodb scan --table-name agent-events
```

### SQS Operations

```bash
# Send a message
aws --endpoint-url=http://localhost:4566 sqs send-message \
    --queue-url http://localhost:4566/000000000000/agent-task-queue \
    --message-body '{"task": "test", "priority": "high"}'

# Receive messages
aws --endpoint-url=http://localhost:4566 sqs receive-message \
    --queue-url http://localhost:4566/000000000000/agent-task-queue

# List queues
aws --endpoint-url=http://localhost:4566 sqs list-queues
```

### SNS Operations

```bash
# Publish a message
aws --endpoint-url=http://localhost:4566 sns publish \
    --topic-arn arn:aws:sns:us-east-1:000000000000:agent-alerts \
    --message "Test alert message"

# List topics
aws --endpoint-url=http://localhost:4566 sns list-topics
```

### CloudWatch Operations

```bash
# Put a metric
aws --endpoint-url=http://localhost:4566 cloudwatch put-metric-data \
    --namespace SelfHealingAgent \
    --metric-name CPUUsage \
    --value 75.5

# List log groups
aws --endpoint-url=http://localhost:4566 logs describe-log-groups
```

## Lambda Function Details

The included test Lambda function (`lambda/lambda_handler.py`) is designed to:

1. **Simulate Failures**: Randomly throws exceptions to test self-healing capabilities
2. **Generate Events**: Creates events that can trigger the Self-Healing Agent
3. **Test Monitoring**: Provides metrics and logs for CloudWatch

### Failure Types Simulated

- **Timeout**: Simulates function timeout
- **Memory Error**: Simulates out-of-memory conditions
- **Connection Error**: Simulates network failures
- **Validation Error**: Simulates input validation failures
- **Resource Not Found**: Simulates missing resources
- **Permission Denied**: Simulates access control failures

### Configuring Failure Rate

Set the `FAILURE_PROBABILITY` environment variable when creating/updating the Lambda:

```bash
aws --endpoint-url=http://localhost:4566 lambda update-function-configuration \
    --function-name self-healing-test-lambda \
    --environment Variables="{FAILURE_PROBABILITY=0.5}"
```

## LocalStack UI

Access the LocalStack web UI at: **http://localhost:8080**

The UI provides:
- Service overview and status
- Resource browser
- API request/response viewer
- Log viewer

## Troubleshooting

### LocalStack Not Starting

```bash
# Check Docker is running
docker ps

# Check LocalStack logs
docker-compose logs localstack

# Check if port 4566 is in use
netstat -an | grep 4566  # Linux/Mac
netstat -an | findstr 4566  # Windows
```

### Bootstrap Script Fails

```bash
# Ensure LocalStack is ready
curl http://localhost:4566/_localstack/health

# Check AWS CLI is configured
aws --version

# Run bootstrap with verbose output
bash -x bootstrap.sh
```

### Lambda Function Not Deploying

```bash
# Check Lambda code is in correct location
ls -la lambda/lambda_handler.py

# Manually create zip file
cd lambda
zip -r lambda_handler.zip lambda_handler.py
cd ..

# Deploy manually
aws --endpoint-url=http://localhost:4566 lambda create-function \
    --function-name self-healing-test-lambda \
    --runtime python3.9 \
    --role arn:aws:iam::000000000000:role/lambda-execution-role \
    --handler lambda_handler.lambda_handler \
    --zip-file fileb://lambda/lambda_handler.zip
```

### Connection Refused Errors

- Ensure LocalStack container is running: `docker-compose ps`
- Verify endpoint URL: `http://localhost:4566`
- Check firewall settings
- Try accessing health endpoint: `curl http://localhost:4566/_localstack/health`

## Data Persistence

LocalStack data is persisted in the `.localstack/` directory. To reset:

```bash
# Stop containers
docker-compose down

# Remove persisted data
rm -rf .localstack/

# Start fresh
docker-compose up -d
```

## Stopping LocalStack

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (clears all data)
docker-compose down -v
```

## Next Steps

1. **Configure Agents**: Update agent configuration files to use LocalStack endpoint
2. **Run Tests**: Execute agent tests against LocalStack
3. **Monitor**: Use LocalStack UI to monitor agent interactions
4. **Extend**: Add more Lambda functions or resources as needed

## Additional Resources

- [LocalStack Documentation](https://docs.localstack.cloud/)
- [LocalStack GitHub](https://github.com/localstack/localstack)
- [AWS CLI Documentation](https://docs.aws.amazon.com/cli/latest/userguide/)
- [Project Architecture Docs](../../docs/architecture/)

## Support

For issues or questions:
1. Check LocalStack logs: `docker-compose logs localstack`
2. Review bootstrap script output
3. Consult LocalStack documentation
4. Check project issue tracker

