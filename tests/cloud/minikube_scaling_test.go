package cloud

import (
	"context"
	"fmt"
	"os"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	appsv1 "k8s.io/api/apps/v1"
	autoscalingv2 "k8s.io/api/autoscaling/v2"
	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/api/resource"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/types"
	"k8s.io/apimachinery/pkg/util/intstr"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/clientcmd"
)

const (
	testNamespace     = "self-healing-cloud"
	testDeploymentName = "test-scaling-deployment"
	testServiceName   = "test-scaling-service"
	testHPAName       = "test-scaling-hpa"
)

// getK8sClient creates a Kubernetes client
func getK8sClient(t *testing.T) *kubernetes.Clientset {
	var config *rest.Config
	var err error

	// Try in-cluster config first
	config, err = rest.InClusterConfig()
	if err != nil {
		// Fall back to kubeconfig
		kubeconfig := os.Getenv("KUBECONFIG")
		if kubeconfig == "" {
			home := os.Getenv("HOME")
			if home == "" {
				home = os.Getenv("USERPROFILE") // Windows
			}
			kubeconfig = fmt.Sprintf("%s/.kube/config", home)
		}
		config, err = clientcmd.BuildConfigFromFlags("", kubeconfig)
		if err != nil {
			t.Skipf("Kubernetes not available: %v", err)
		}
	}

	clientset, err := kubernetes.NewForConfig(config)
	require.NoError(t, err, "Failed to create Kubernetes client")

	return clientset
}

// ensureNamespace ensures the test namespace exists
func ensureNamespace(t *testing.T, client *kubernetes.Clientset, namespace string) {
	ctx := context.Background()
	_, err := client.CoreV1().Namespaces().Get(ctx, namespace, metav1.GetOptions{})
	if err != nil {
		// Create namespace if it doesn't exist
		_, err = client.CoreV1().Namespaces().Create(ctx, &corev1.Namespace{
			ObjectMeta: metav1.ObjectMeta{
				Name: namespace,
			},
		}, metav1.CreateOptions{})
		if err != nil {
			t.Logf("Namespace may already exist: %v", err)
		}
	}
}

// TestKubernetesConnection verifies Kubernetes cluster is accessible
func TestKubernetesConnection(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	client := getK8sClient(t)
	ctx := context.Background()

	// Test: List nodes
	nodes, err := client.CoreV1().Nodes().List(ctx, metav1.ListOptions{})
	require.NoError(t, err, "Should list nodes successfully")
	assert.Greater(t, len(nodes.Items), 0, "Should have at least one node")
}

// TestDeploymentCreation verifies deployment creation
func TestDeploymentCreation(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	client := getK8sClient(t)
	ctx := context.Background()
	ensureNamespace(t, client, testNamespace)

	// Cleanup: Delete deployment if exists
	_ = client.AppsV1().Deployments(testNamespace).Delete(ctx, testDeploymentName, metav1.DeleteOptions{})

	// Test: Create deployment
	t.Run("CreateDeployment", func(t *testing.T) {
		replicas := int32(2)
		deployment := &appsv1.Deployment{
			ObjectMeta: metav1.ObjectMeta{
				Name:      testDeploymentName,
				Namespace: testNamespace,
			},
			Spec: appsv1.DeploymentSpec{
				Replicas: &replicas,
				Selector: &metav1.LabelSelector{
					MatchLabels: map[string]string{
						"app": testDeploymentName,
					},
				},
				Template: corev1.PodTemplateSpec{
					ObjectMeta: metav1.ObjectMeta{
						Labels: map[string]string{
							"app": testDeploymentName,
						},
					},
					Spec: corev1.PodSpec{
						Containers: []corev1.Container{
							{
								Name:  "nginx",
								Image: "nginx:alpine",
								Ports: []corev1.ContainerPort{
									{
										ContainerPort: 80,
									},
								},
								Resources: corev1.ResourceRequirements{
									Requests: corev1.ResourceList{
										corev1.ResourceCPU:    resource.MustParse("100m"),
										corev1.ResourceMemory: resource.MustParse("128Mi"),
									},
									Limits: corev1.ResourceList{
										corev1.ResourceCPU:    resource.MustParse("500m"),
										corev1.ResourceMemory: resource.MustParse("512Mi"),
									},
								},
							},
						},
					},
				},
			},
		}

		created, err := client.AppsV1().Deployments(testNamespace).Create(ctx, deployment, metav1.CreateOptions{})
		require.NoError(t, err, "Should create deployment successfully")
		assert.Equal(t, testDeploymentName, created.Name)
		assert.Equal(t, replicas, *created.Spec.Replicas)
	})

	// Test: Wait for deployment to be ready
	t.Run("WaitForDeploymentReady", func(t *testing.T) {
		timeout := 2 * time.Minute
		interval := 5 * time.Second
		deadline := time.Now().Add(timeout)

		for time.Now().Before(deadline) {
			deployment, err := client.AppsV1().Deployments(testNamespace).Get(ctx, testDeploymentName, metav1.GetOptions{})
			if err == nil {
				if deployment.Status.ReadyReplicas == *deployment.Spec.Replicas {
					t.Logf("Deployment ready with %d replicas", deployment.Status.ReadyReplicas)
					break
				}
			}
			time.Sleep(interval)
		}

		deployment, err := client.AppsV1().Deployments(testNamespace).Get(ctx, testDeploymentName, metav1.GetOptions{})
		require.NoError(t, err)
		assert.Equal(t, *deployment.Spec.Replicas, deployment.Status.ReadyReplicas, "Deployment should have all replicas ready")
	})

	// Cleanup
	t.Cleanup(func() {
		_ = client.AppsV1().Deployments(testNamespace).Delete(ctx, testDeploymentName, metav1.DeleteOptions{})
	})
}

// TestHPACreation verifies HPA creation and configuration
func TestHPACreation(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	client := getK8sClient(t)
	ctx := context.Background()
	ensureNamespace(t, client, testNamespace)

	// Ensure deployment exists
	TestDeploymentCreation(t)

	// Cleanup: Delete HPA if exists
	_ = client.AutoscalingV2().HorizontalPodAutoscalers(testNamespace).Delete(ctx, testHPAName, metav1.DeleteOptions{})

	// Test: Create HPA
	t.Run("CreateHPA", func(t *testing.T) {
		minReplicas := int32(2)
		maxReplicas := int32(10)
		targetCPU := int32(70)

		hpa := &autoscalingv2.HorizontalPodAutoscaler{
			ObjectMeta: metav1.ObjectMeta{
				Name:      testHPAName,
				Namespace: testNamespace,
			},
			Spec: autoscalingv2.HorizontalPodAutoscalerSpec{
				ScaleTargetRef: autoscalingv2.CrossVersionObjectReference{
					APIVersion: "apps/v1",
					Kind:       "Deployment",
					Name:       testDeploymentName,
				},
				MinReplicas: &minReplicas,
				MaxReplicas: maxReplicas,
				Metrics: []autoscalingv2.MetricSpec{
					{
						Type: autoscalingv2.ResourceMetricSourceType,
						Resource: &autoscalingv2.ResourceMetricSource{
							Name: corev1.ResourceCPU,
							Target: autoscalingv2.MetricTarget{
								Type:               autoscalingv2.UtilizationMetricType,
								AverageUtilization: &targetCPU,
							},
						},
					},
				},
			},
		}

		created, err := client.AutoscalingV2().HorizontalPodAutoscalers(testNamespace).Create(ctx, hpa, metav1.CreateOptions{})
		require.NoError(t, err, "Should create HPA successfully")
		assert.Equal(t, testHPAName, created.Name)
		assert.Equal(t, minReplicas, *created.Spec.MinReplicas)
		assert.Equal(t, maxReplicas, created.Spec.MaxReplicas)
	})

	// Cleanup
	t.Cleanup(func() {
		_ = client.AutoscalingV2().HorizontalPodAutoscalers(testNamespace).Delete(ctx, testHPAName, metav1.DeleteOptions{})
	})
}

// TestAutoscalingEvent simulates autoscaling by updating deployment replicas
func TestAutoscalingEvent(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	client := getK8sClient(t)
	ctx := context.Background()
	ensureNamespace(t, client, testNamespace)

	// Ensure deployment and HPA exist
	TestDeploymentCreation(t)
	TestHPACreation(t)

	// Test: Scale up deployment
	t.Run("ScaleUp", func(t *testing.T) {
		deployment, err := client.AppsV1().Deployments(testNamespace).Get(ctx, testDeploymentName, metav1.GetOptions{})
		require.NoError(t, err)

		initialReplicas := *deployment.Spec.Replicas
		newReplicas := int32(5)

		// Update replicas
		patch := []byte(fmt.Sprintf(`{"spec":{"replicas":%d}}`, newReplicas))
		_, err = client.AppsV1().Deployments(testNamespace).Patch(
			ctx,
			testDeploymentName,
			types.MergePatchType,
			patch,
			metav1.PatchOptions{},
		)
		require.NoError(t, err, "Should scale up deployment")

		// Wait for scaling
		timeout := 2 * time.Minute
		interval := 5 * time.Second
		deadline := time.Now().Add(timeout)

		for time.Now().Before(deadline) {
			deployment, err := client.AppsV1().Deployments(testNamespace).Get(ctx, testDeploymentName, metav1.GetOptions{})
			if err == nil && deployment.Status.ReadyReplicas == newReplicas {
				t.Logf("Deployment scaled to %d replicas", newReplicas)
				break
			}
			time.Sleep(interval)
		}

		// Verify scaling
		deployment, err = client.AppsV1().Deployments(testNamespace).Get(ctx, testDeploymentName, metav1.GetOptions{})
		require.NoError(t, err)
		assert.Equal(t, newReplicas, *deployment.Spec.Replicas, "Deployment should have new replica count")
		assert.Greater(t, *deployment.Spec.Replicas, initialReplicas, "Replicas should have increased")
	})

	// Test: Scale down
	t.Run("ScaleDown", func(t *testing.T) {
		newReplicas := int32(3)

		patch := []byte(fmt.Sprintf(`{"spec":{"replicas":%d}}`, newReplicas))
		_, err := client.AppsV1().Deployments(testNamespace).Patch(
			ctx,
			testDeploymentName,
			types.MergePatchType,
			patch,
			metav1.PatchOptions{},
		)
		require.NoError(t, err, "Should scale down deployment")

		// Wait for scaling
		time.Sleep(30 * time.Second)

		deployment, err := client.AppsV1().Deployments(testNamespace).Get(ctx, testDeploymentName, metav1.GetOptions{})
		require.NoError(t, err)
		assert.Equal(t, newReplicas, *deployment.Spec.Replicas, "Deployment should have scaled down")
	})
}

// TestHPAStatus verifies HPA status and metrics
func TestHPAStatus(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	client := getK8sClient(t)
	ctx := context.Background()
	ensureNamespace(t, client, testNamespace)

	// Ensure HPA exists
	TestHPACreation(t)

	// Test: Get HPA status
	t.Run("GetHPAStatus", func(t *testing.T) {
		hpa, err := client.AutoscalingV2().HorizontalPodAutoscalers(testNamespace).Get(ctx, testHPAName, metav1.GetOptions{})
		require.NoError(t, err, "Should get HPA successfully")

		assert.NotNil(t, hpa.Status, "HPA should have status")
		assert.NotNil(t, hpa.Status.CurrentReplicas, "HPA should have current replicas")
		assert.GreaterOrEqual(t, int(*hpa.Status.CurrentReplicas), int(*hpa.Spec.MinReplicas), "Current replicas should be >= min")
		assert.LessOrEqual(t, int(*hpa.Status.CurrentReplicas), int(hpa.Spec.MaxReplicas), "Current replicas should be <= max")

		t.Logf("HPA Status - Current Replicas: %d, Desired: %d, Min: %d, Max: %d",
			*hpa.Status.CurrentReplicas,
			*hpa.Status.DesiredReplicas,
			*hpa.Spec.MinReplicas,
			hpa.Spec.MaxReplicas)
	})
}

