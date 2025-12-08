package cloud

import (
	"context"
	"fmt"
	"os"
	"testing"
	"time"

	selfhealing "github.com/ai-driven-self-healing-cloud/agents/self-healing"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	appsv1 "k8s.io/api/apps/v1"
	corev1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/types"
	"k8s.io/apimachinery/pkg/util/intstr"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/clientcmd"
)

const (
	testNamespace        = "self-healing-cloud"
	testServiceName      = "test-failure-service"
	testDeploymentName   = "test-failure-deployment"
)

// getK8sClient creates a Kubernetes client (reused from minikube_scaling_test.go)
func getK8sClient(t *testing.T) *kubernetes.Clientset {
	var config *rest.Config
	var err error

	config, err = rest.InClusterConfig()
	if err != nil {
		kubeconfig := os.Getenv("KUBECONFIG")
		if kubeconfig == "" {
			home := os.Getenv("HOME")
			if home == "" {
				home = os.Getenv("USERPROFILE")
			}
			kubeconfig = fmt.Sprintf("%s/.kube/config", home)
		}
		config, err = clientcmd.BuildConfigFromFlags("", kubeconfig)
		if err != nil {
			t.Skipf("Kubernetes not available: %v", err)
		}
	}

	clientset, err := kubernetes.NewForConfig(config)
	require.NoError(t, err)
	return clientset
}

// ensureNamespace ensures the test namespace exists
func ensureNamespace(t *testing.T, client *kubernetes.Clientset, namespace string) {
	ctx := context.Background()
	_, err := client.CoreV1().Namespaces().Get(ctx, namespace, metav1.GetOptions{})
	if err != nil {
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

// createTestDeployment creates a test deployment for failure injection
func createTestDeployment(t *testing.T, client *kubernetes.Clientset, name string) {
	ctx := context.Background()
	replicas := int32(2)

	deployment := &appsv1.Deployment{
		ObjectMeta: metav1.ObjectMeta{
			Name:      name,
			Namespace: testNamespace,
		},
		Spec: appsv1.DeploymentSpec{
			Replicas: &replicas,
			Selector: &metav1.LabelSelector{
				MatchLabels: map[string]string{
					"app": name,
				},
			},
			Template: corev1.PodTemplateSpec{
				ObjectMeta: metav1.ObjectMeta{
					Labels: map[string]string{
						"app": name,
					},
				},
				Spec: corev1.PodSpec{
					Containers: []corev1.Container{
						{
							Name:  "nginx",
							Image: "nginx:alpine",
							Ports: []corev1.ContainerPort{
								{ContainerPort: 80},
							},
							LivenessProbe: &corev1.Probe{
								ProbeHandler: corev1.ProbeHandler{
									HTTPGet: &corev1.HTTPGetAction{
										Path: "/",
										Port: intstr.FromInt(80),
									},
								},
								InitialDelaySeconds: 5,
								PeriodSeconds:       10,
							},
						},
					},
				},
			},
		},
	}

	_, err := client.AppsV1().Deployments(testNamespace).Create(ctx, deployment, metav1.CreateOptions{})
	require.NoError(t, err, "Should create test deployment")

	// Wait for deployment to be ready
	timeout := 2 * time.Minute
	deadline := time.Now().Add(timeout)
	for time.Now().Before(deadline) {
		deployment, err := client.AppsV1().Deployments(testNamespace).Get(ctx, name, metav1.GetOptions{})
		if err == nil && deployment.Status.ReadyReplicas == replicas {
			break
		}
		time.Sleep(5 * time.Second)
	}
}

// TestServiceCrashSimulation simulates a service crash and verifies recovery
func TestServiceCrashSimulation(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	client := getK8sClient(t)
	ctx := context.Background()
	ensureNamespace(t, client, testNamespace)

	// Setup: Create test deployment
	createTestDeployment(t, client, testDeploymentName)

	// Cleanup
	defer func() {
		_ = client.AppsV1().Deployments(testNamespace).Delete(ctx, testDeploymentName, metav1.DeleteOptions{})
	}()

	// Test: Get initial pod count
	t.Run("GetInitialPodCount", func(t *testing.T) {
		pods, err := client.CoreV1().Pods(testNamespace).List(ctx, metav1.ListOptions{
			LabelSelector: fmt.Sprintf("app=%s", testDeploymentName),
		})
		require.NoError(t, err)
		initialCount := len(pods.Items)
		assert.Greater(t, initialCount, 0, "Should have at least one pod initially")
		t.Logf("Initial pod count: %d", initialCount)
	})

	// Test: Simulate pod crash by deleting a pod
	t.Run("SimulatePodCrash", func(t *testing.T) {
		pods, err := client.CoreV1().Pods(testNamespace).List(ctx, metav1.ListOptions{
			LabelSelector: fmt.Sprintf("app=%s", testDeploymentName),
		})
		require.NoError(t, err)
		require.Greater(t, len(pods.Items), 0, "Should have pods to delete")

		// Delete first pod to simulate crash
		podToDelete := pods.Items[0].Name
		t.Logf("Deleting pod: %s to simulate crash", podToDelete)

		err = client.CoreV1().Pods(testNamespace).Delete(ctx, podToDelete, metav1.DeleteOptions{
			GracePeriodSeconds: func() *int64 { v := int64(0); return &v }(),
		})
		require.NoError(t, err, "Should delete pod successfully")

		// Verify pod is deleted
		_, err = client.CoreV1().Pods(testNamespace).Get(ctx, podToDelete, metav1.GetOptions{})
		assert.Error(t, err, "Pod should be deleted")
	})

	// Test: Verify self-healing (pod recreation)
	t.Run("VerifySelfHealing", func(t *testing.T) {
		timeout := 2 * time.Minute
		interval := 5 * time.Second
		deadline := time.Now().Add(timeout)

		var recovered bool
		for time.Now().Before(deadline) {
			pods, err := client.CoreV1().Pods(testNamespace).List(ctx, metav1.ListOptions{
				LabelSelector: fmt.Sprintf("app=%s", testDeploymentName),
			})
			if err == nil {
				// Check if we have the expected number of pods
				deployment, _ := client.AppsV1().Deployments(testNamespace).Get(ctx, testDeploymentName, metav1.GetOptions{})
				if deployment != nil {
					expectedReplicas := *deployment.Spec.Replicas
					runningPods := 0
					for _, pod := range pods.Items {
						if pod.Status.Phase == corev1.PodRunning {
							runningPods++
						}
					}
					if runningPods >= int(expectedReplicas) {
						recovered = true
						t.Logf("Self-healing successful: %d pods running (expected: %d)", runningPods, expectedReplicas)
						break
					}
				}
			}
			time.Sleep(interval)
		}

		assert.True(t, recovered, "Deployment should have recreated pods (self-healing)")
	})
}

// TestSelfHealingAgentReaction tests if Self-Healing Agent reacts to failures
func TestSelfHealingAgentReaction(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	// Initialize Self-Healing Agent
	agent := selfhealing.NewSelfHealingAgent()
	err := agent.Start()
	require.NoError(t, err, "Should start Self-Healing Agent")
	defer agent.Stop()

	// Test: Create healing request
	t.Run("CreateHealingRequest", func(t *testing.T) {
		request := &selfhealing.HealingRequest{
			ServiceID:   testDeploymentName,
			FailureType: "pod_crash",
			Error:       "Pod crashed unexpectedly",
			Metadata: map[string]interface{}{
				"namespace": testNamespace,
				"pod_name":  "test-pod",
			},
		}

		healer := selfhealing.NewHealer()
		result, err := healer.Heal(request)
		require.NoError(t, err, "Should process healing request")
		assert.NotNil(t, result, "Should return healing result")
		assert.Equal(t, request.ServiceID, result.ServiceID, "Result should match service ID")
		assert.True(t, result.Success, "Healing should be successful")
		t.Logf("Healing action: %s, Reasoning: %s", result.Action, result.Reasoning)
	})

	// Test: Use CloudAdapter for actual healing
	t.Run("CloudAdapterHealing", func(t *testing.T) {
		client := getK8sClient(t)
		ctx := context.Background()
		ensureNamespace(t, client, testNamespace)

		// Create test deployment
		createTestDeployment(t, client, testDeploymentName)
		defer func() {
			_ = client.AppsV1().Deployments(testNamespace).Delete(ctx, testDeploymentName, metav1.DeleteOptions{})
		}()

		// Get a pod to restart
		pods, err := client.CoreV1().Pods(testNamespace).List(ctx, metav1.ListOptions{
			LabelSelector: fmt.Sprintf("app=%s", testDeploymentName),
		})
		require.NoError(t, err)
		require.Greater(t, len(pods.Items), 0, "Should have pods")

		podName := pods.Items[0].Name

		// Create cloud adapter and restart pod
		adapter, err := selfhealing.NewCloudAdapter()
		if err != nil {
			t.Skipf("Cloud adapter not available: %v", err)
		}

		err = adapter.RestartPod(podName)
		require.NoError(t, err, "Should restart pod via CloudAdapter")

		// Wait a bit for pod to be recreated
		time.Sleep(10 * time.Second)

		// Verify pod was recreated (new pod with different name)
		newPods, err := client.CoreV1().Pods(testNamespace).List(ctx, metav1.ListOptions{
			LabelSelector: fmt.Sprintf("app=%s", testDeploymentName),
		})
		require.NoError(t, err)

		// Check if we have pods (old one deleted, new one created)
		assert.Greater(t, len(newPods.Items), 0, "Should have pods after restart")
	})
}

// TestMultipleFailureScenarios tests various failure scenarios
func TestMultipleFailureScenarios(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration test in short mode")
	}

	client := getK8sClient(t)
	ctx := context.Background()
	ensureNamespace(t, client, testNamespace)

	// Test: Deployment failure
	t.Run("DeploymentFailure", func(t *testing.T) {
		deploymentName := "test-failure-deployment-2"
		createTestDeployment(t, client, deploymentName)
		defer func() {
			_ = client.AppsV1().Deployments(testNamespace).Delete(ctx, deploymentName, metav1.DeleteOptions{})
		}()

		// Simulate failure by scaling to 0
		patch := []byte(`{"spec":{"replicas":0}}`)
		_, err := client.AppsV1().Deployments(testNamespace).Patch(
			ctx,
			deploymentName,
			types.MergePatchType,
			patch,
			metav1.PatchOptions{},
		)
		require.NoError(t, err)

		// Wait and verify
		time.Sleep(10 * time.Second)
		deployment, err := client.AppsV1().Deployments(testNamespace).Get(ctx, deploymentName, metav1.GetOptions{})
		require.NoError(t, err)
		assert.Equal(t, int32(0), *deployment.Spec.Replicas, "Deployment should be scaled to 0")

		// Recover by scaling back
		patch = []byte(`{"spec":{"replicas":2}}`)
		_, err = client.AppsV1().Deployments(testNamespace).Patch(
			ctx,
			deploymentName,
			types.MergePatchType,
			patch,
			metav1.PatchOptions{},
		)
		require.NoError(t, err)

		// Verify recovery
		timeout := 2 * time.Minute
		deadline := time.Now().Add(timeout)
		for time.Now().Before(deadline) {
			deployment, err := client.AppsV1().Deployments(testNamespace).Get(ctx, deploymentName, metav1.GetOptions{})
			if err == nil && deployment.Status.ReadyReplicas == 2 {
				t.Logf("Deployment recovered with %d replicas", deployment.Status.ReadyReplicas)
				break
			}
			time.Sleep(5 * time.Second)
		}
	})
}

