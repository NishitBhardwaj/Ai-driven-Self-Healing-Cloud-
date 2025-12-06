# CI/CD Directory

This folder contains configuration files and scripts for the Continuous Integration and Continuous Deployment (CI/CD) pipeline. The CI/CD pipeline automates the process of building, testing, and deploying the multi-agent system.

## Overview

The CI/CD pipeline ensures:

- **Continuous Integration**: Automatically integrates code changes, runs tests, and builds artifacts
- **Continuous Deployment**: Automatically deploys code changes to staging and production environments
- **Quality Assurance**: Enforces code quality standards and automated testing
- **Fast Feedback**: Provides quick feedback on code changes

## Supported CI/CD Platforms

### Jenkins

Jenkins is an open-source automation server that provides extensive plugin support for building, testing, and deploying applications.

**Configuration Location**: `/ci-cd/jenkins/`

#### Setup

1. **Install Jenkins**:

   ```bash
   # Using Docker
   docker run -d \
     --name jenkins \
     -p 8080:8080 \
     -p 50000:50000 \
     -v jenkins_home:/var/jenkins_home \
     jenkins/jenkins:lts
   ```

2. **Access Jenkins**:

   Open http://localhost:8080 and follow the setup wizard.

3. **Pipeline Configuration**:

   Pipeline files (Jenkinsfile) are located in `/ci-cd/jenkins/`:
   - `Jenkinsfile`: Main pipeline definition
   - `pipeline-config.groovy`: Pipeline configuration
   - `deploy-stages.groovy`: Deployment stage definitions

#### Pipeline Stages

1. **Checkout**: Clone the repository
2. **Build**: Build Docker images for agents
3. **Test**: Run unit tests and integration tests
4. **Lint**: Run code quality checks
5. **Security Scan**: Scan for vulnerabilities
6. **Deploy to Staging**: Deploy to staging environment
7. **Integration Tests**: Run end-to-end tests
8. **Deploy to Production**: Deploy to production (with approval)

### GitLab CI

GitLab CI is integrated into GitLab and provides a simple YAML-based configuration for CI/CD pipelines.

**Configuration Location**: `/ci-cd/gitlab-ci/`

#### Setup

1. **GitLab CI Configuration**:

   The main configuration file is `.gitlab-ci.yml` in the repository root, with additional files in `/ci-cd/gitlab-ci/`:
   - `.gitlab-ci.yml`: Main pipeline configuration
   - `stages.yml`: Stage definitions
   - `deploy.yml`: Deployment configurations

#### Pipeline Stages

```yaml
stages:
  - build
  - test
  - lint
  - security
  - deploy-staging
  - integration-tests
  - deploy-production
```

## Pipeline Workflow

### 1. Code Commit

When code is committed to the repository:

```bash
git add .
git commit -m "Add new feature"
git push origin main
```

### 2. Build Stage

- Builds Docker images for each agent
- Tags images with commit SHA
- Pushes images to container registry

### 3. Test Stage

- Runs unit tests for each agent
- Runs integration tests
- Generates test coverage reports

### 4. Quality Checks

- Runs linting (ESLint, Pylint)
- Runs code formatting checks
- Performs security scanning

### 5. Deploy to Staging

- Deploys agents to staging Kubernetes cluster
- Runs smoke tests
- Verifies deployment health

### 6. Integration Tests

- Runs end-to-end tests
- Tests agent interactions
- Validates system behavior

### 7. Deploy to Production

- Requires manual approval
- Deploys to production Kubernetes cluster
- Monitors deployment health
- Automatic rollback on failure

## Configuration Files

### Jenkins

- **Jenkinsfile**: Main pipeline definition using Groovy DSL
- **pipeline-config.groovy**: Shared pipeline configuration
- **deploy-stages.groovy**: Deployment stage definitions

### GitLab CI

- **.gitlab-ci.yml**: Main pipeline configuration
- **stages.yml**: Stage definitions and templates
- **deploy.yml**: Deployment job definitions

## Environment Variables

Set these environment variables in your CI/CD platform:

```bash
# Container Registry
DOCKER_REGISTRY=your-registry.com
DOCKER_USERNAME=your-username
DOCKER_PASSWORD=your-password

# Kubernetes
KUBECONFIG_PATH=/path/to/kubeconfig
KUBERNETES_NAMESPACE=production

# Cloud Credentials (for cloud deployment)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-1

# Database
POSTGRES_HOST=postgres-host
POSTGRES_PASSWORD=postgres-password
MONGODB_URI=mongodb://host:27017
```

## Testing in CI/CD

### Unit Tests

```bash
# Python agents
pytest tests/unit/ --cov=agents --cov-report=xml

# Node.js agents
npm run test:unit -- --coverage
```

### Integration Tests

```bash
pytest tests/integration/ --docker-compose
```

### End-to-End Tests

```bash
pytest tests/e2e/ --kubernetes
```

## Deployment Strategies

### Blue-Green Deployment

- Deploy new version alongside old version
- Switch traffic to new version
- Keep old version as backup

### Canary Deployment

- Deploy new version to subset of instances
- Monitor performance
- Gradually roll out to all instances

### Rolling Deployment

- Gradually replace old instances with new ones
- Maintain service availability
- Automatic rollback on failure

## Monitoring Deployment

Monitor deployments using:

- **Kubernetes**: `kubectl get deployments`
- **Prometheus**: Deployment metrics
- **Grafana**: Deployment dashboards
- **Logs**: Centralized logging (ELK Stack)

## Rollback Procedures

### Automatic Rollback

Configure automatic rollback on:

- Health check failures
- High error rates
- Performance degradation

### Manual Rollback

```bash
# Kubernetes
kubectl rollout undo deployment/agent-name

# Docker Compose
docker-compose down
docker-compose up -d --scale agent-name=previous-version
```

## Best Practices

1. **Fast Feedback**: Keep pipeline execution time under 15 minutes
2. **Parallel Execution**: Run independent tests in parallel
3. **Caching**: Cache dependencies and build artifacts
4. **Security**: Never commit secrets; use secret management
5. **Testing**: Maintain high test coverage (>80%)
6. **Documentation**: Document pipeline changes and configurations

## Troubleshooting

### Build Failures

- Check build logs for errors
- Verify dependencies are available
- Check Docker image build context

### Test Failures

- Review test output and logs
- Check test environment setup
- Verify test data availability

### Deployment Failures

- Check Kubernetes cluster status
- Verify resource quotas
- Check network connectivity
- Review deployment logs

## Related Documentation

- Docker setup: `/docker/README.md`
- Kubernetes setup: `/kubernetes/README.md`
- Testing: `/tests/README.md`
- Monitoring: `/monitoring/README.md`

