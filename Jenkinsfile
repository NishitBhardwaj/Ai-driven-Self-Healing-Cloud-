pipeline {
    agent any
    
    environment {
        REGISTRY = 'ghcr.io'
        IMAGE_PREFIX = "${env.GIT_URL.split('/')[1].replace('.git', '')}"
        KUBERNETES_NAMESPACE = "ai-cloud-${env.BRANCH_NAME == 'main' ? 'production' : 'staging'}"
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Unit Tests - Go') {
            steps {
                sh '''
                    go version
                    go mod download
                    go test -v -race -coverprofile=coverage.out ./tests/agents/...
                    go test -v -race -coverprofile=coverage-integration.out ./tests/integration/...
                '''
            }
            post {
                always {
                    publishCoverage adapters: [
                        coberturaAdapter('coverage.out'),
                        coberturaAdapter('coverage-integration.out')
                    ]
                }
            }
        }
        
        stage('Unit Tests - Python') {
            steps {
                sh '''
                    python3 --version
                    pip3 install --upgrade pip
                    pip3 install pytest pytest-cov
                    if [ -f agents/coding/requirements.txt ]; then pip3 install -r agents/coding/requirements.txt; fi
                    if [ -f agents/security/requirements.txt ]; then pip3 install -r agents/security/requirements.txt; fi
                    if [ -f agents/optimization/requirements.txt ]; then pip3 install -r agents/optimization/requirements.txt; fi
                    pytest tests/agents/*_test.py -v --cov=agents --cov-report=xml
                '''
            }
            post {
                always {
                    publishCoverage adapters: [coberturaAdapter('coverage.xml')]
                }
            }
        }
        
        stage('Linting - Go') {
            steps {
                sh '''
                    docker run --rm -v $(pwd):/app -w /app golangci/golangci-lint:latest golangci-lint run --timeout=5m
                '''
            }
        }
        
        stage('Linting - Python') {
            steps {
                sh '''
                    docker run --rm -v $(pwd):/app -w /app python:3.11 bash -c "
                        pip install flake8 black
                        flake8 agents/ --count --select=E9,F63,F7,F82 --show-source --statistics
                        black --check agents/
                    "
                '''
            }
        }
        
        stage('Build Docker Images') {
            parallel {
                stage('Build Self-Healing Agent') {
                    steps {
                        script {
                            def image = docker.build("${IMAGE_PREFIX}-self-healing:${env.BUILD_NUMBER}", "-f docker/agents/self-healing/Dockerfile .")
                            docker.withRegistry("https://${REGISTRY}", credentialsId: 'docker-registry-credentials') {
                                image.push("${env.BUILD_NUMBER}")
                                image.push("latest")
                            }
                        }
                    }
                }
                
                stage('Build Scaling Agent') {
                    steps {
                        script {
                            def image = docker.build("${IMAGE_PREFIX}-scaling:${env.BUILD_NUMBER}", "-f docker/agents/scaling/Dockerfile .")
                            docker.withRegistry("https://${REGISTRY}", credentialsId: 'docker-registry-credentials') {
                                image.push("${env.BUILD_NUMBER}")
                                image.push("latest")
                            }
                        }
                    }
                }
                
                stage('Build Task-Solving Agent') {
                    steps {
                        script {
                            def image = docker.build("${IMAGE_PREFIX}-task-solving:${env.BUILD_NUMBER}", "-f docker/agents/task-solving/Dockerfile .")
                            docker.withRegistry("https://${REGISTRY}", credentialsId: 'docker-registry-credentials') {
                                image.push("${env.BUILD_NUMBER}")
                                image.push("latest")
                            }
                        }
                    }
                }
                
                stage('Build Performance Monitoring Agent') {
                    steps {
                        script {
                            def image = docker.build("${IMAGE_PREFIX}-performance-monitoring:${env.BUILD_NUMBER}", "-f docker/agents/performance-monitoring/Dockerfile .")
                            docker.withRegistry("https://${REGISTRY}", credentialsId: 'docker-registry-credentials') {
                                image.push("${env.BUILD_NUMBER}")
                                image.push("latest")
                            }
                        }
                    }
                }
                
                stage('Build Python Agents') {
                    steps {
                        script {
                            ['coding', 'security', 'optimization'].each { agent ->
                                def image = docker.build("${IMAGE_PREFIX}-${agent}:${env.BUILD_NUMBER}", "-f docker/agents/${agent}/Dockerfile .")
                                docker.withRegistry("https://${REGISTRY}", credentialsId: 'docker-registry-credentials') {
                                    image.push("${env.BUILD_NUMBER}")
                                    image.push("latest")
                                }
                            }
                        }
                    }
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                sh '''
                    docker run --rm -v $(pwd):/app -v /var/run/docker.sock:/var/run/docker.sock \
                        aquasec/trivy:latest fs --severity HIGH,CRITICAL --exit-code 1 /app
                '''
            }
        }
        
        stage('Deploy to Kubernetes') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                script {
                    def kubeConfig = credentials('kubernetes-config')
                    sh '''
                        kubectl version --client
                        helm version
                        kubectl config use-context ${KUBE_CONTEXT}
                        kubectl create namespace ${KUBERNETES_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                        helm upgrade --install ai-cloud \
                            kubernetes/helm/ai-cloud \
                            --namespace ${KUBERNETES_NAMESPACE} \
                            --set image.registry=${REGISTRY} \
                            --set image.prefix=${IMAGE_PREFIX} \
                            --set image.tag=${BUILD_NUMBER} \
                            --set environment=${BRANCH_NAME == 'main' ? 'production' : 'staging'} \
                            --wait \
                            --timeout 10m
                        kubectl rollout status deployment/ai-cloud-self-healing -n ${KUBERNETES_NAMESPACE} --timeout=5m
                    '''
                }
            }
        }
        
        stage('Smoke Tests') {
            steps {
                sh '''
                    sleep 30
                    kubectl run -it --rm test-client --image=curlimages/curl --restart=Never -- \
                        curl -f http://ai-cloud-self-healing:8080/health || exit 1
                '''
            }
        }
    }
    
    post {
        success {
            emailext(
                subject: "Build Success: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Build succeeded. Check console output at ${env.BUILD_URL}",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
        failure {
            script {
                sh '''
                    kubectl config use-context ${KUBE_CONTEXT}
                    helm rollback ai-cloud ${KUBERNETES_NAMESPACE} || true
                '''
            }
            emailext(
                subject: "Build Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Build failed. Check console output at ${env.BUILD_URL}",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
        always {
            cleanWs()
        }
    }
}

