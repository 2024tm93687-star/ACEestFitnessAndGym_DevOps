pipeline {
    agent any

    environment {
        REGISTRY = 'ghcr.io'
        REGISTRY_OWNER = '2024tm93687-star'
        IMAGE_NAME = 'aceest-fitness-app'
        K8S_DEPLOYMENT = 'aceest-fitness-api'
        K8S_CONTAINER = 'aceest-fitness-api'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    if (isUnix()) {
                        // CI installs requirements-dev.txt because tests run here.
                        // requirements-dev.txt includes requirements.txt plus test tooling.
                        sh '''
                            python3 -m venv venv
                            ./venv/bin/python3 -m pip install --upgrade pip
                            ./venv/bin/python3 -m pip install -r requirements-dev.txt
                        '''
                    } else {
                        bat '''
                            python -m venv venv
                            venv\\Scripts\\python -m pip install --upgrade pip
                            venv\\Scripts\\python -m pip install -r requirements-dev.txt
                        '''
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    if (isUnix()) {
                        // Use the python inside the venv to run pytest
                        sh './venv/bin/python3 -m pytest test_app.py -v'
                    } else {
                        bat 'venv\\Scripts\\python -m pytest test_app.py -v'
                    }
                }
            }
        }

        stage('Build and Push Docker Image to github Container Registry') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'github-creds-container', usernameVariable: 'GITHUB_USERNAME', passwordVariable: 'GITHUB_TOKEN')]) {
                        def imageVersion = "${env.REGISTRY}/${env.REGISTRY_OWNER}/${env.IMAGE_NAME}:${env.BUILD_NUMBER}"
                        def imageLatest = "${env.REGISTRY}/${env.REGISTRY_OWNER}/${env.IMAGE_NAME}:latest"

                        if (isUnix()) {
                            sh """
                                echo "${GITHUB_TOKEN}" | docker login ${env.REGISTRY} -u "${GITHUB_USERNAME}" --password-stdin
                                docker build -t ${imageVersion} -t ${imageLatest} .
                                docker push ${imageVersion}
                                docker push ${imageLatest}
                                docker logout ${env.REGISTRY}
                            """
                        } else {
                            bat """
                                echo %GITHUB_TOKEN% | docker login ${env.REGISTRY} -u %GITHUB_USERNAME% --password-stdin
                                docker build -t ${imageVersion} -t ${imageLatest} .
                                docker push ${imageVersion}
                                docker push ${imageLatest}
                                docker logout ${env.REGISTRY}
                            """
                        }
                    }
                }
            }
        }

        stage('Detect Branch Context') {
            steps {
                script {
                    def rawBranch = env.BRANCH_NAME ?: env.GIT_BRANCH ?: ''
                    def normalizedBranch = rawBranch.replaceFirst('^origin/', '').replaceFirst('^refs/heads/', '')
                    echo "BRANCH_NAME=${env.BRANCH_NAME}"
                    echo "GIT_BRANCH=${env.GIT_BRANCH}"
                    echo "Normalized branch=${normalizedBranch}"
                }
            }
        }

        stage('Deploy to Minikube') {
            when {
                expression {
                    def rawBranch = env.BRANCH_NAME ?: env.GIT_BRANCH ?: ''
                    def normalizedBranch = rawBranch.replaceFirst('^origin/', '').replaceFirst('^refs/heads/', '')
                    return normalizedBranch == 'main' || normalizedBranch == 'develop'
                }
            }
            steps {
                script {
                    withCredentials([
                        file(credentialsId: 'minikube-kubeconfig', variable: 'KUBECONFIG_FILE'),
                        usernamePassword(credentialsId: 'github-creds-container', usernameVariable: 'GITHUB_USERNAME', passwordVariable: 'GITHUB_TOKEN')
                    ]) {
                        def imageVersion = "${env.REGISTRY}/${env.REGISTRY_OWNER}/${env.IMAGE_NAME}:${env.BUILD_NUMBER}"

                        if (isUnix()) {
                            sh """
                                export KUBECONFIG="\$KUBECONFIG_FILE"
                                kubectl config current-context
                                kubectl cluster-info
                                kubectl create secret docker-registry ghcr-pull-secret \
                                    --docker-server=${env.REGISTRY} \
                                    --docker-username="\$GITHUB_USERNAME" \
                                    --docker-password="\$GITHUB_TOKEN" \
                                    --dry-run=client -o yaml | kubectl apply -f -
                                kubectl apply -f k8s/deployment.yaml
                                kubectl apply -f k8s/service.yaml
                                kubectl set image deployment/${env.K8S_DEPLOYMENT} ${env.K8S_CONTAINER}=${imageVersion}
                                kubectl rollout status deployment/${env.K8S_DEPLOYMENT} --timeout=180s
                            """
                        } else {
                            bat """
                                set "KUBECONFIG=%KUBECONFIG_FILE%"
                                kubectl config current-context
                                kubectl cluster-info
                                kubectl create secret docker-registry ghcr-pull-secret --docker-server=${env.REGISTRY} --docker-username=%GITHUB_USERNAME% --docker-password=%GITHUB_TOKEN% --dry-run=client -o yaml | kubectl apply -f -
                                kubectl apply -f k8s/deployment.yaml
                                kubectl apply -f k8s/service.yaml
                                kubectl set image deployment/%K8S_DEPLOYMENT% %K8S_CONTAINER%=${imageVersion}
                                kubectl rollout status deployment/%K8S_DEPLOYMENT% --timeout=180s
                            """
                        }
                    }
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed. Please check the logs.'
        }
    }
}
