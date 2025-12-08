package cloud

import (
	"context"
	"net/http"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/lambda"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const (
	testBucketName    = "test-bucket-cloud-simulation"
	testLambdaName    = "self-healing-test-lambda"
	testRegion        = "us-east-1"
	localstackEndpoint = "http://localhost:4566"
)

// getLocalStackEndpoint returns the LocalStack endpoint URL
func getLocalStackEndpoint() string {
	endpoint := os.Getenv("AWS_ENDPOINT_URL")
	if endpoint == "" {
		endpoint = localstackEndpoint
	}
	return endpoint
}

// createS3Client creates an S3 client configured for LocalStack
func createS3Client(t *testing.T) *s3.S3 {
	endpoint := getLocalStackEndpoint()
	
	config := &aws.Config{
		Region:           aws.String(testRegion),
		Endpoint:         aws.String(endpoint),
		Credentials:      credentials.NewStaticCredentials("test", "test", ""),
		S3ForcePathStyle: aws.Bool(true),
	}

	sess, err := session.NewSession(config)
	require.NoError(t, err, "Failed to create AWS session")

	return s3.New(sess)
}

// createLambdaClient creates a Lambda client configured for LocalStack
func createLambdaClient(t *testing.T) *lambda.Lambda {
	endpoint := getLocalStackEndpoint()
	
	config := &aws.Config{
		Region:      aws.String(testRegion),
		Endpoint:    aws.String(endpoint),
		Credentials: credentials.NewStaticCredentials("test", "test", ""),
	}

	sess, err := session.NewSession(config)
	require.NoError(t, err, "Failed to create AWS session")

	return lambda.New(sess)
}

// TestLocalStackConnection verifies LocalStack is accessible
func TestLocalStackConnection(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	// Check if LocalStack is running
	endpoint := getLocalStackEndpoint()
	client := &http.Client{Timeout: 5 * time.Second}
	
	resp, err := client.Get(endpoint + "/_localstack/health")
	if err != nil {
		t.Skipf("LocalStack not available at %s: %v", endpoint, err)
	}
	defer resp.Body.Close()

	assert.Equal(t, 200, resp.StatusCode, "LocalStack should be healthy")
}

// TestS3BucketCreation verifies S3 bucket creation in LocalStack
func TestS3BucketCreation(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	s3Client := createS3Client(t)
	ctx := context.Background()

	// Clean up: Delete bucket if it exists
	_, _ = s3Client.DeleteBucket(&s3.DeleteBucketInput{
		Bucket: aws.String(testBucketName),
	})
	time.Sleep(1 * time.Second) // Wait for deletion

	// Test: Create bucket
	t.Run("CreateBucket", func(t *testing.T) {
		_, err := s3Client.CreateBucketWithContext(ctx, &s3.CreateBucketInput{
			Bucket: aws.String(testBucketName),
		})
		require.NoError(t, err, "Should create bucket successfully")

		// Verify bucket exists
		_, err = s3Client.HeadBucketWithContext(ctx, &s3.HeadBucketInput{
			Bucket: aws.String(testBucketName),
		})
		assert.NoError(t, err, "Bucket should exist after creation")
	})

	// Test: List buckets
	t.Run("ListBuckets", func(t *testing.T) {
		result, err := s3Client.ListBucketsWithContext(ctx, &s3.ListBucketsInput{})
		require.NoError(t, err, "Should list buckets successfully")

		found := false
		for _, bucket := range result.Buckets {
			if *bucket.Name == testBucketName {
				found = true
				break
			}
		}
		assert.True(t, found, "Created bucket should appear in list")
	})

	// Test: Upload object
	t.Run("UploadObject", func(t *testing.T) {
		testKey := "test-object.txt"
		testContent := "Hello, LocalStack!"

		_, err := s3Client.PutObjectWithContext(ctx, &s3.PutObjectInput{
			Bucket: aws.String(testBucketName),
			Key:    aws.String(testKey),
			Body:   strings.NewReader(testContent),
		})
		require.NoError(t, err, "Should upload object successfully")

		// Verify object exists
		result, err := s3Client.GetObjectWithContext(ctx, &s3.GetObjectInput{
			Bucket: aws.String(testBucketName),
			Key:    aws.String(testKey),
		})
		require.NoError(t, err, "Should retrieve object successfully")
		defer result.Body.Close()

		bodyBytes := make([]byte, len(testContent))
		_, err = result.Body.Read(bodyBytes)
		assert.NoError(t, err, "Should read object content")
		assert.Equal(t, testContent, string(bodyBytes), "Object content should match")
	})

	// Cleanup
	t.Cleanup(func() {
		// Delete all objects in bucket
		listResult, _ := s3Client.ListObjectsV2WithContext(ctx, &s3.ListObjectsV2Input{
			Bucket: aws.String(testBucketName),
		})
		for _, obj := range listResult.Contents {
			s3Client.DeleteObjectWithContext(ctx, &s3.DeleteObjectInput{
				Bucket: aws.String(testBucketName),
				Key:    obj.Key,
			})
		}
		// Delete bucket
		s3Client.DeleteBucketWithContext(ctx, &s3.DeleteBucketInput{
			Bucket: aws.String(testBucketName),
		})
	})
}

// TestLambdaInvocation verifies Lambda function invocation in LocalStack
func TestLambdaInvocation(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	lambdaClient := createLambdaClient(t)
	ctx := context.Background()

	// Check if Lambda function exists
	t.Run("ListLambdaFunctions", func(t *testing.T) {
		result, err := lambdaClient.ListFunctionsWithContext(ctx, &lambda.ListFunctionsInput{})
		require.NoError(t, err, "Should list Lambda functions successfully")

		found := false
		for _, fn := range result.Functions {
			if *fn.FunctionName == testLambdaName {
				found = true
				break
			}
		}
		
		if !found {
			t.Skipf("Lambda function %s not found. Run bootstrap script first.", testLambdaName)
		}
	})

	// Test: Invoke Lambda function
	t.Run("InvokeLambda", func(t *testing.T) {
		payload := `{"test": "data", "action": "test"}`
		
		result, err := lambdaClient.InvokeWithContext(ctx, &lambda.InvokeInput{
			FunctionName: aws.String(testLambdaName),
			Payload:      []byte(payload),
		})
		
		require.NoError(t, err, "Should invoke Lambda function successfully")
		assert.NotNil(t, result.StatusCode, "Should have status code")
		assert.Equal(t, int64(200), *result.StatusCode, "Lambda should return 200")

		// Check for function errors
		if result.FunctionError != nil {
			t.Logf("Lambda function error: %s", *result.FunctionError)
			t.Logf("Payload: %s", string(result.Payload))
		} else {
			t.Logf("Lambda invocation successful. Payload: %s", string(result.Payload))
		}
	})

	// Test: Invoke with error simulation
	t.Run("InvokeLambdaWithError", func(t *testing.T) {
		// Lambda function may simulate errors randomly
		// This test verifies error handling
		payload := `{"test": "error_simulation"}`
		
		result, err := lambdaClient.InvokeWithContext(ctx, &lambda.InvokeInput{
			FunctionName: aws.String(testLambdaName),
			Payload:      []byte(payload),
		})
		
		require.NoError(t, err, "Invoke call should succeed even if function errors")
		
		// Function may return error, which is expected behavior
		if result.FunctionError != nil {
			t.Logf("Expected function error received: %s", *result.FunctionError)
		}
	})
}

// TestS3OperationsComprehensive tests various S3 operations
func TestS3OperationsComprehensive(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	s3Client := createS3Client(t)
	ctx := context.Background()

	// Setup
	_, err := s3Client.CreateBucketWithContext(ctx, &s3.CreateBucketInput{
		Bucket: aws.String(testBucketName),
	})
	require.NoError(t, err)

	// Cleanup
	defer func() {
		// Delete all objects
		listResult, _ := s3Client.ListObjectsV2WithContext(ctx, &s3.ListObjectsV2Input{
			Bucket: aws.String(testBucketName),
		})
		for _, obj := range listResult.Contents {
			s3Client.DeleteObjectWithContext(ctx, &s3.DeleteObjectInput{
				Bucket: aws.String(testBucketName),
				Key:    obj.Key,
			})
		}
		// Delete bucket
		s3Client.DeleteBucketWithContext(ctx, &s3.DeleteBucketInput{
			Bucket: aws.String(testBucketName),
		})
	}()

	t.Run("MultipleObjects", func(t *testing.T) {
		// Upload multiple objects
		objects := []string{"file1.txt", "file2.txt", "file3.txt"}
		for _, key := range objects {
			_, err := s3Client.PutObjectWithContext(ctx, &s3.PutObjectInput{
				Bucket: aws.String(testBucketName),
				Key:    aws.String(key),
				Body:   strings.NewReader("content for " + key),
			})
			require.NoError(t, err, "Should upload %s", key)
		}

		// List objects
		result, err := s3Client.ListObjectsV2WithContext(ctx, &s3.ListObjectsV2Input{
			Bucket: aws.String(testBucketName),
		})
		require.NoError(t, err)
		assert.Equal(t, int64(len(objects)), *result.KeyCount, "Should have correct number of objects")
	})

	t.Run("DeleteObject", func(t *testing.T) {
		key := "to-delete.txt"
		// Upload
		_, err := s3Client.PutObjectWithContext(ctx, &s3.PutObjectInput{
			Bucket: aws.String(testBucketName),
			Key:    aws.String(key),
			Body:   strings.NewReader("content"),
		})
		require.NoError(t, err)

		// Delete
		_, err = s3Client.DeleteObjectWithContext(ctx, &s3.DeleteObjectInput{
			Bucket: aws.String(testBucketName),
			Key:    aws.String(key),
		})
		require.NoError(t, err, "Should delete object successfully")

		// Verify deletion
		_, err = s3Client.HeadObjectWithContext(ctx, &s3.HeadObjectInput{
			Bucket: aws.String(testBucketName),
			Key:    aws.String(key),
		})
		assert.Error(t, err, "Object should not exist after deletion")
	})
}

