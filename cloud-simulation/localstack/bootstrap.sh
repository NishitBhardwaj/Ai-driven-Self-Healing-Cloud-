#!/bin/bash

# LocalStack Bootstrap Script
# This script sets up AWS resources in LocalStack for testing the Self-Healing Cloud system

set -e

echo "=========================================="
echo "LocalStack Bootstrap Script"
echo "=========================================="

# Configuration
ENDPOINT_URL="http://localhost:4566"
REGION="us-east-1"
AWS_ACCESS_KEY_ID="test"
AWS_SECRET_ACCESS_KEY="test"

# Export AWS credentials for AWS CLI
export AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=$REGION

# Wait for LocalStack to be ready
echo "Waiting for LocalStack to be ready..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:4566/_localstack/health | grep -q "\"lambda\": \"available\""; then
        echo "LocalStack is ready!"
        break
    fi
    attempt=$((attempt + 1))
    echo "Attempt $attempt/$max_attempts: Waiting for LocalStack..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "ERROR: LocalStack did not become ready in time"
    exit 1
fi

echo ""
echo "=========================================="
echo "Creating S3 Buckets"
echo "=========================================="

# Create S3 buckets
aws --endpoint-url=$ENDPOINT_URL s3 mb s3://self-healing-agent-logs --region $REGION || true
aws --endpoint-url=$ENDPOINT_URL s3 mb s3://agent-artifacts --region $REGION || true
aws --endpoint-url=$ENDPOINT_URL s3 mb s3://cloud-metrics --region $REGION || true
aws --endpoint-url=$ENDPOINT_URL s3 mb s3://lambda-deployments --region $REGION || true

echo "S3 Buckets created:"
aws --endpoint-url=$ENDPOINT_URL s3 ls --region $REGION

echo ""
echo "=========================================="
echo "Creating DynamoDB Tables"
echo "=========================================="

# Create DynamoDB tables
aws --endpoint-url=$ENDPOINT_URL dynamodb create-table \
    --table-name agent-events \
    --attribute-definitions \
        AttributeName=event_id,AttributeType=S \
        AttributeName=timestamp,AttributeType=N \
    --key-schema \
        AttributeName=event_id,KeyType=HASH \
        AttributeName=timestamp,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region $REGION || true

aws --endpoint-url=$ENDPOINT_URL dynamodb create-table \
    --table-name system-health \
    --attribute-definitions \
        AttributeName=resource_id,AttributeType=S \
        AttributeName=check_time,AttributeType=N \
    --key-schema \
        AttributeName=resource_id,KeyType=HASH \
        AttributeName=check_time,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region $REGION || true

aws --endpoint-url=$ENDPOINT_URL dynamodb create-table \
    --table-name healing-actions \
    --attribute-definitions \
        AttributeName=action_id,AttributeType=S \
    --key-schema \
        AttributeName=action_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region $REGION || true

echo "DynamoDB Tables created:"
aws --endpoint-url=$ENDPOINT_URL dynamodb list-tables --region $REGION

echo ""
echo "=========================================="
echo "Deploying Lambda Function"
echo "=========================================="

# Create deployment package
cd lambda
if [ -f "lambda_handler.zip" ]; then
    rm lambda_handler.zip
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -t . --quiet || true
fi

# Create zip file (excluding unnecessary files)
zip -r lambda_handler.zip lambda_handler.py -x "*.pyc" "__pycache__/*" "*.zip" || \
    zip -r lambda_handler.zip . -x "*.pyc" "__pycache__/*" "*.zip" "bootstrap.sh" "docker-compose.yml" "README.md"

cd ..

# Create IAM role for Lambda (simplified for LocalStack)
ROLE_ARN="arn:aws:iam::000000000000:role/lambda-execution-role"

# Create the Lambda function
aws --endpoint-url=$ENDPOINT_URL lambda create-function \
    --function-name self-healing-test-lambda \
    --runtime python3.9 \
    --role $ROLE_ARN \
    --handler lambda_handler.lambda_handler \
    --zip-file fileb://lambda/lambda_handler.zip \
    --timeout 30 \
    --memory-size 256 \
    --region $REGION || \
    aws --endpoint-url=$ENDPOINT_URL lambda update-function-code \
        --function-name self-healing-test-lambda \
        --zip-file fileb://lambda/lambda_handler.zip \
        --region $REGION

echo "Lambda function deployed:"
aws --endpoint-url=$ENDPOINT_URL lambda list-functions --region $REGION

echo ""
echo "=========================================="
echo "Creating SNS Topics"
echo "=========================================="

# Create SNS topics
aws --endpoint-url=$ENDPOINT_URL sns create-topic \
    --name agent-alerts \
    --region $REGION || true

aws --endpoint-url=$ENDPOINT_URL sns create-topic \
    --name system-failures \
    --region $REGION || true

aws --endpoint-url=$ENDPOINT_URL sns create-topic \
    --name healing-actions \
    --region $REGION || true

echo "SNS Topics created:"
aws --endpoint-url=$ENDPOINT_URL sns list-topics --region $REGION

echo ""
echo "=========================================="
echo "Creating SQS Queues"
echo "=========================================="

# Create SQS queues
aws --endpoint-url=$ENDPOINT_URL sqs create-queue \
    --queue-name agent-task-queue \
    --region $REGION \
    --attributes VisibilityTimeout=30,MessageRetentionPeriod=345600 || true

aws --endpoint-url=$ENDPOINT_URL sqs create-queue \
    --queue-name healing-action-queue \
    --region $REGION \
    --attributes VisibilityTimeout=60,MessageRetentionPeriod=345600 || true

aws --endpoint-url=$ENDPOINT_URL sqs create-queue \
    --queue-name event-queue \
    --region $REGION \
    --attributes VisibilityTimeout=30,MessageRetentionPeriod=345600 || true

echo "SQS Queues created:"
aws --endpoint-url=$ENDPOINT_URL sqs list-queues --region $REGION

echo ""
echo "=========================================="
echo "Setting up EC2 Mock Metadata"
echo "=========================================="

# Note: EC2 metadata service is automatically available in LocalStack
# at http://169.254.169.254/latest/meta-data/
echo "EC2 metadata service available at: http://169.254.169.254/latest/meta-data/"
echo "You can query instance metadata using:"
echo "  curl http://169.254.169.254/latest/meta-data/instance-id"

echo ""
echo "=========================================="
echo "Creating CloudWatch Log Groups"
echo "=========================================="

# Create CloudWatch log groups
aws --endpoint-url=$ENDPOINT_URL logs create-log-group \
    --log-group-name /aws/lambda/self-healing-test-lambda \
    --region $REGION || true

aws --endpoint-url=$ENDPOINT_URL logs create-log-group \
    --log-group-name /aws/agents/self-healing \
    --region $REGION || true

aws --endpoint-url=$ENDPOINT_URL logs create-log-group \
    --log-group-name /aws/agents/all-agents \
    --region $REGION || true

echo "CloudWatch Log Groups created:"
aws --endpoint-url=$ENDPOINT_URL logs describe-log-groups --region $REGION | grep logGroupName

echo ""
echo "=========================================="
echo "LocalStack Environment Status"
echo "=========================================="

echo ""
echo "✅ S3 Buckets:"
aws --endpoint-url=$ENDPOINT_URL s3 ls --region $REGION

echo ""
echo "✅ DynamoDB Tables:"
aws --endpoint-url=$ENDPOINT_URL dynamodb list-tables --region $REGION

echo ""
echo "✅ Lambda Functions:"
aws --endpoint-url=$ENDPOINT_URL lambda list-functions --region $REGION | grep FunctionName

echo ""
echo "✅ SNS Topics:"
aws --endpoint-url=$ENDPOINT_URL sns list-topics --region $REGION | grep TopicArn

echo ""
echo "✅ SQS Queues:"
aws --endpoint-url=$ENDPOINT_URL sqs list-queues --region $REGION

echo ""
echo "✅ CloudWatch Log Groups:"
aws --endpoint-url=$ENDPOINT_URL logs describe-log-groups --region $REGION | grep logGroupName

echo ""
echo "=========================================="
echo "Bootstrap Complete!"
echo "=========================================="
echo ""
echo "LocalStack Endpoint: $ENDPOINT_URL"
echo "Region: $REGION"
echo "Access Key: $AWS_ACCESS_KEY_ID"
echo "Secret Key: $AWS_SECRET_ACCESS_KEY"
echo ""
echo "LocalStack UI: http://localhost:8080"
echo ""
echo "You can now test the environment using AWS CLI commands."
echo "Example:"
echo "  aws --endpoint-url=$ENDPOINT_URL s3 ls"
echo "  aws --endpoint-url=$ENDPOINT_URL lambda invoke --function-name self-healing-test-lambda /dev/stdout"
echo ""

