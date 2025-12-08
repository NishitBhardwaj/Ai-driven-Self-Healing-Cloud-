package scaling

import (
	"context"
	"fmt"
	"os"
	"time"

	"github.com/sirupsen/logrus"
	appsv1 "k8s.io/api/apps/v1"
	autoscalingv2 "k8s.io/api/autoscaling/v2"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/types"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/clientcmd"
)

// K8sScaling handles Kubernetes scaling operations
type K8sScaling struct {
	k8sClient *kubernetes.Clientset
	namespace string
	logger    *logrus.Logger
}

// NewK8sScaling creates a new K8sScaling instance
func NewK8sScaling() (*K8sScaling, error) {
	logger := logrus.New()

	// Initialize Kubernetes client
	k8sClient, err := initK8sClient()
	if err != nil {
		return nil, fmt.Errorf("failed to initialize Kubernetes client: %w", err)
	}

	namespace := os.Getenv("KUBERNETES_NAMESPACE")
	if namespace == "" {
		namespace = "self-healing-cloud"
	}

	return &K8sScaling{
		k8sClient: k8sClient,
		namespace: namespace,
		logger:    logger,
	}, nil
}

// initK8sClient initializes Kubernetes client
func initK8sClient() (*kubernetes.Clientset, error) {
	var config *rest.Config
	var err error

	// Try in-cluster config first
	config, err = rest.InClusterConfig()
	if err != nil {
		// Fall back to kubeconfig file
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
			return nil, fmt.Errorf("failed to load kubeconfig: %w", err)
		}
	}

	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		return nil, fmt.Errorf("failed to create Kubernetes client: %w", err)
	}

	return clientset, nil
}

// GetCurrentReplicas gets the current number of replicas for a service/deployment
func (ks *K8sScaling) GetCurrentReplicas(serviceName string) (int32, error) {
	ctx := context.Background()

	// Try to get deployment first
	deployment, err := ks.k8sClient.AppsV1().Deployments(ks.namespace).Get(ctx, serviceName, metav1.GetOptions{})
	if err == nil {
		replicas := int32(0)
		if deployment.Spec.Replicas != nil {
			replicas = *deployment.Spec.Replicas
		}
		ks.logger.WithFields(logrus.Fields{
			"service":  serviceName,
			"replicas": replicas,
		}).Debug("Retrieved current replicas from deployment")
		return replicas, nil
	}

	// Try StatefulSet
	statefulSet, err := ks.k8sClient.AppsV1().StatefulSets(ks.namespace).Get(ctx, serviceName, metav1.GetOptions{})
	if err == nil {
		replicas := int32(0)
		if statefulSet.Spec.Replicas != nil {
			replicas = *statefulSet.Spec.Replicas
		}
		ks.logger.WithFields(logrus.Fields{
			"service":  serviceName,
			"replicas": replicas,
		}).Debug("Retrieved current replicas from statefulset")
		return replicas, nil
	}

	return 0, fmt.Errorf("service %s not found (tried Deployment and StatefulSet)", serviceName)
}

// SetReplicas sets the number of replicas for a service/deployment
func (ks *K8sScaling) SetReplicas(serviceName string, replicas int32) error {
	ctx := context.Background()

	ks.logger.WithFields(logrus.Fields{
		"service":  serviceName,
		"replicas": replicas,
	}).Info("Setting replicas")

	// Try deployment first
	deployment, err := ks.k8sClient.AppsV1().Deployments(ks.namespace).Get(ctx, serviceName, metav1.GetOptions{})
	if err == nil {
		patch := []byte(fmt.Sprintf(`{"spec":{"replicas":%d}}`, replicas))
		_, err = ks.k8sClient.AppsV1().Deployments(ks.namespace).Patch(
			ctx,
			serviceName,
			types.MergePatchType,
			patch,
			metav1.PatchOptions{},
		)
		if err != nil {
			return fmt.Errorf("failed to patch deployment: %w", err)
		}

		ks.logger.WithFields(logrus.Fields{
			"service":  serviceName,
			"replicas": replicas,
		}).Info("Deployment replicas updated")
		return nil
	}

	// Try StatefulSet
	statefulSet, err := ks.k8sClient.AppsV1().StatefulSets(ks.namespace).Get(ctx, serviceName, metav1.GetOptions{})
	if err == nil {
		patch := []byte(fmt.Sprintf(`{"spec":{"replicas":%d}}`, replicas))
		_, err = ks.k8sClient.AppsV1().StatefulSets(ks.namespace).Patch(
			ctx,
			serviceName,
			types.MergePatchType,
			patch,
			metav1.PatchOptions{},
		)
		if err != nil {
			return fmt.Errorf("failed to patch statefulset: %w", err)
		}

		ks.logger.WithFields(logrus.Fields{
			"service":  serviceName,
			"replicas": replicas,
		}).Info("StatefulSet replicas updated")
		return nil
	}

	return fmt.Errorf("service %s not found (tried Deployment and StatefulSet)", serviceName)
}

// PredictAndScale predicts future load and scales accordingly
func (ks *K8sScaling) PredictAndScale() error {
	ks.logger.Info("Predicting load and scaling services")

	ctx := context.Background()

	// Get all deployments in namespace
	deployments, err := ks.k8sClient.AppsV1().Deployments(ks.namespace).List(ctx, metav1.ListOptions{})
	if err != nil {
		return fmt.Errorf("failed to list deployments: %w", err)
	}

	// Get HPA configurations
	hpas, err := ks.k8sClient.AutoscalingV2().HorizontalPodAutoscalers(ks.namespace).List(ctx, metav1.ListOptions{})
	if err != nil {
		ks.logger.WithError(err).Warn("Failed to list HPAs, continuing without HPA info")
	}

	// Analyze each deployment
	for _, deployment := range deployments.Items {
		serviceName := deployment.Name
		
		// Get current metrics (simplified - in production, query metrics server)
		currentReplicas, err := ks.GetCurrentReplicas(serviceName)
		if err != nil {
			ks.logger.WithError(err).Warnf("Failed to get replicas for %s", serviceName)
			continue
		}

		// Find HPA for this deployment
		var hpa *autoscalingv2.HorizontalPodAutoscaler
		for i := range hpas.Items {
			if hpas.Items[i].Spec.ScaleTargetRef.Name == serviceName {
				hpa = &hpas.Items[i]
				break
			}
		}

		// Predict scaling need (simplified prediction logic)
		// In production, this would use ML models to predict load
		predictedReplicas, reason := ks.predictReplicas(serviceName, currentReplicas, hpa)

		if predictedReplicas != currentReplicas {
			ks.logger.WithFields(logrus.Fields{
				"service":          serviceName,
				"current":          currentReplicas,
				"predicted":        predictedReplicas,
				"reason":           reason,
			}).Info("Scaling prediction made")

			// Apply scaling
			if err := ks.SetReplicas(serviceName, predictedReplicas); err != nil {
				ks.logger.WithError(err).Errorf("Failed to scale %s", serviceName)
				continue
			}

			ks.logger.WithFields(logrus.Fields{
				"service": serviceName,
				"replicas": predictedReplicas,
			}).Info("Service scaled successfully")
		}
	}

	return nil
}

// predictReplicas predicts the optimal number of replicas
// This is a simplified version - in production, this would use ML models
func (ks *K8sScaling) predictReplicas(serviceName string, current int32, hpa *autoscalingv2.HorizontalPodAutoscaler) (int32, string) {
	// Get pod metrics (simplified - would query metrics server in production)
	// For now, use a simple heuristic based on time and service name
	
	// Simulate prediction based on time of day (example)
	hour := time.Now().Hour()
	var predicted int32
	var reason string

	if hour >= 9 && hour <= 17 {
		// Business hours - scale up
		predicted = current + 1
		if hpa != nil && hpa.Spec.MaxReplicas != nil && predicted > *hpa.Spec.MaxReplicas {
			predicted = *hpa.Spec.MaxReplicas
		}
		reason = "Predicted higher load during business hours"
	} else {
		// Off hours - scale down
		predicted = current - 1
		if hpa != nil && hpa.Spec.MinReplicas != nil && predicted < *hpa.Spec.MinReplicas {
			predicted = *hpa.Spec.MinReplicas
		}
		reason = "Predicted lower load during off hours"
	}

	// Ensure minimum of 1 replica
	if predicted < 1 {
		predicted = 1
	}

	return predicted, reason
}

// GetHPAStatus gets the current status of HorizontalPodAutoscaler
func (ks *K8sScaling) GetHPAStatus(serviceName string) (*autoscalingv2.HorizontalPodAutoscaler, error) {
	ctx := context.Background()
	
	hpa, err := ks.k8sClient.AutoscalingV2().HorizontalPodAutoscalers(ks.namespace).Get(ctx, serviceName+"-hpa", metav1.GetOptions{})
	if err != nil {
		return nil, fmt.Errorf("failed to get HPA: %w", err)
	}

	return hpa, nil
}

// ScaleToMin scales a service to its minimum replicas
func (ks *K8sScaling) ScaleToMin(serviceName string) error {
	hpa, err := ks.GetHPAStatus(serviceName)
	if err != nil {
		// If no HPA, scale to 1
		return ks.SetReplicas(serviceName, 1)
	}

	minReplicas := int32(1)
	if hpa.Spec.MinReplicas != nil {
		minReplicas = *hpa.Spec.MinReplicas
	}

	return ks.SetReplicas(serviceName, minReplicas)
}

// ScaleToMax scales a service to its maximum replicas
func (ks *K8sScaling) ScaleToMax(serviceName string) error {
	hpa, err := ks.GetHPAStatus(serviceName)
	if err != nil {
		return fmt.Errorf("failed to get HPA for %s: %w", serviceName, err)
	}

	if hpa.Spec.MaxReplicas == nil {
		return fmt.Errorf("HPA for %s has no max replicas set", serviceName)
	}

	return ks.SetReplicas(serviceName, *hpa.Spec.MaxReplicas)
}

