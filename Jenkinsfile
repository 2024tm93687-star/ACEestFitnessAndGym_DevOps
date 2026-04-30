pipeline {
    agent any

    parameters {
        choice(name: 'DEPLOYMENT_STRATEGY', choices: ['rolling-update', 'blue-green', 'canary', 'shadow', 'ab-test'], description: 'Deployment methodology to use for the release.')
        choice(name: 'BLUE_GREEN_TARGET', choices: ['green', 'blue'], description: 'Target slot for blue-green deployments.')
        choice(name: 'ROLLBACK_TO', choices: ['none', 'blue', 'green'], description: 'For blue-green only: switch service traffic back to this slot without deploying a new image.')
        string(name: 'STABLE_REPLICAS', defaultValue: '3', description: 'Stable pod count for canary and A/B traffic distribution.')
        string(name: 'CANARY_REPLICAS', defaultValue: '1', description: 'Canary or B-variant pod count.')
    }
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
            when {
                expression { params.ROLLBACK_TO == 'none' }
            }
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
            when {
                expression { params.ROLLBACK_TO == 'none' }
            }
            steps {
                script {
                    if (isUnix()) {
                        // Use the python inside the venv to run pytest
                        sh './venv/bin/python3 -m pytest test_app.py -v --cov=app --cov-report=xml'
                    } else {
                        bat 'venv\\Scripts\\python -m pytest test_app.py -v --cov=app --cov-report=xml'
                    }
                }
            }
        }

        stage('SonarQube Analysis') {
            when {
                expression { params.ROLLBACK_TO == 'none' }
            }
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'

                    withSonarQubeEnv('SonarQube') {
                        if (isUnix()) {
                            sh "${scannerHome}/bin/sonar-scanner"
                        } else {
                            bat "\"${scannerHome}\\bin\\sonar-scanner.bat\""
                        }
                    }
                }
            }
        }

        stage('Quality Gate') {
            when {
                expression { params.ROLLBACK_TO == 'none' }
            }
            steps {
                timeout(time: 15, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build, Test, and Push Docker Image to github Container Registry') {
            when {
                expression { params.ROLLBACK_TO == 'none' }
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'github-creds-container', usernameVariable: 'GITHUB_USERNAME', passwordVariable: 'GITHUB_TOKEN')]) {
                        def imageVersion = "${env.REGISTRY}/${env.REGISTRY_OWNER}/${env.IMAGE_NAME}:${env.BUILD_NUMBER}"
                        def imageLatest = "${env.REGISTRY}/${env.REGISTRY_OWNER}/${env.IMAGE_NAME}:latest"

                        if (isUnix()) {
                            sh """
                                docker build --target test -t ${env.IMAGE_NAME}:test-${env.BUILD_NUMBER} .
                                docker run --rm ${env.IMAGE_NAME}:test-${env.BUILD_NUMBER}
                                docker build --target runtime -t ${imageVersion} -t ${imageLatest} .
                                echo "${GITHUB_TOKEN}" | docker login ${env.REGISTRY} -u "${GITHUB_USERNAME}" --password-stdin
                                docker push ${imageVersion}
                                docker push ${imageLatest}
                                docker logout ${env.REGISTRY}
                            """
                        } else {
                            bat """
                                docker build --target test -t ${env.IMAGE_NAME}:test-%BUILD_NUMBER% .
                                docker run --rm ${env.IMAGE_NAME}:test-%BUILD_NUMBER%
                                docker build --target runtime -t ${imageVersion} -t ${imageLatest} .
                                echo %GITHUB_TOKEN% | docker login ${env.REGISTRY} -u %GITHUB_USERNAME% --password-stdin
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
                        def strategy = params.DEPLOYMENT_STRATEGY
                        def rollbackTo = params.ROLLBACK_TO
                        def blueGreenTarget = params.BLUE_GREEN_TARGET
                        def stableReplicas = params.STABLE_REPLICAS
                        def canaryReplicas = params.CANARY_REPLICAS

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
                            """

                            if (rollbackTo != 'none') {
                                sh """
                                    export KUBECONFIG="\$KUBECONFIG_FILE"
                                    kubectl apply -f k8s/service-${rollbackTo}.yaml
                                    kubectl rollout status deployment/${env.K8S_DEPLOYMENT}-${rollbackTo} --timeout=180s
                                """
                            } else if (strategy == 'rolling-update') {
                                sh """
                                    export KUBECONFIG="\$KUBECONFIG_FILE"
                                    kubectl delete deployment ${env.K8S_DEPLOYMENT}-blue ${env.K8S_DEPLOYMENT}-green ${env.K8S_DEPLOYMENT}-canary ${env.K8S_DEPLOYMENT}-shadow ${env.K8S_DEPLOYMENT}-ab --ignore-not-found
                                    kubectl apply -f k8s/deployment.yaml
                                    kubectl apply -f k8s/service.yaml
                                    kubectl set image deployment/${env.K8S_DEPLOYMENT} ${env.K8S_CONTAINER}=${imageVersion}
                                    kubectl rollout status deployment/${env.K8S_DEPLOYMENT} --timeout=180s
                                """
                            } else if (strategy == 'blue-green') {
                                sh """
                                    export KUBECONFIG="\$KUBECONFIG_FILE"
                                    kubectl apply -f k8s/service.yaml
                                    kubectl apply -f k8s/deployment-${blueGreenTarget}.yaml
                                    kubectl set image deployment/${env.K8S_DEPLOYMENT}-${blueGreenTarget} ${env.K8S_CONTAINER}=${imageVersion}
                                    kubectl rollout status deployment/${env.K8S_DEPLOYMENT}-${blueGreenTarget} --timeout=180s
                                    kubectl apply -f k8s/service-${blueGreenTarget}.yaml
                                """
                            } else if (strategy == 'canary') {
                                sh """
                                    export KUBECONFIG="\$KUBECONFIG_FILE"
                                    kubectl delete deployment ${env.K8S_DEPLOYMENT}-blue ${env.K8S_DEPLOYMENT}-green ${env.K8S_DEPLOYMENT}-ab --ignore-not-found
                                    kubectl apply -f k8s/service.yaml
                                    kubectl scale deployment/${env.K8S_DEPLOYMENT} --replicas=${stableReplicas}
                                    kubectl apply -f k8s/deployment-canary.yaml
                                    kubectl set image deployment/${env.K8S_DEPLOYMENT}-canary ${env.K8S_CONTAINER}=${imageVersion}
                                    kubectl scale deployment/${env.K8S_DEPLOYMENT}-canary --replicas=${canaryReplicas}
                                    kubectl rollout status deployment/${env.K8S_DEPLOYMENT}-canary --timeout=180s
                                """
                            } else if (strategy == 'shadow') {
                                sh """
                                    export KUBECONFIG="\$KUBECONFIG_FILE"
                                    kubectl apply -f k8s/deployment-shadow.yaml
                                    kubectl set image deployment/${env.K8S_DEPLOYMENT}-shadow ${env.K8S_CONTAINER}=${imageVersion}
                                    kubectl rollout status deployment/${env.K8S_DEPLOYMENT}-shadow --timeout=180s
                                """
                            } else if (strategy == 'ab-test') {
                                sh """
                                    export KUBECONFIG="\$KUBECONFIG_FILE"
                                    kubectl delete deployment ${env.K8S_DEPLOYMENT}-blue ${env.K8S_DEPLOYMENT}-green ${env.K8S_DEPLOYMENT}-canary --ignore-not-found
                                    kubectl apply -f k8s/service.yaml
                                    kubectl scale deployment/${env.K8S_DEPLOYMENT} --replicas=${stableReplicas}
                                    kubectl apply -f k8s/deployment-ab.yaml
                                    kubectl set image deployment/${env.K8S_DEPLOYMENT}-ab ${env.K8S_CONTAINER}=${imageVersion}
                                    kubectl scale deployment/${env.K8S_DEPLOYMENT}-ab --replicas=${canaryReplicas}
                                    kubectl rollout status deployment/${env.K8S_DEPLOYMENT}-ab --timeout=180s
                                """
                            }
                        } else {
                            bat """
                                set "KUBECONFIG=%KUBECONFIG_FILE%"
                                kubectl config current-context
                                kubectl cluster-info
                                kubectl create secret docker-registry ghcr-pull-secret --docker-server=${env.REGISTRY} --docker-username=%GITHUB_USERNAME% --docker-password=%GITHUB_TOKEN% --dry-run=client -o yaml | kubectl apply -f -
                            """

                            if (rollbackTo != 'none') {
                                bat """
                                    set "KUBECONFIG=%KUBECONFIG_FILE%"
                                    kubectl apply -f k8s/service-${rollbackTo}.yaml
                                    kubectl rollout status deployment/%K8S_DEPLOYMENT%-${rollbackTo} --timeout=180s
                                """
                            } else if (strategy == 'rolling-update') {
                                bat """
                                    set "KUBECONFIG=%KUBECONFIG_FILE%"
                                    kubectl delete deployment %K8S_DEPLOYMENT%-blue %K8S_DEPLOYMENT%-green %K8S_DEPLOYMENT%-canary %K8S_DEPLOYMENT%-shadow %K8S_DEPLOYMENT%-ab --ignore-not-found
                                    kubectl apply -f k8s/deployment.yaml
                                    kubectl apply -f k8s/service.yaml
                                    kubectl set image deployment/%K8S_DEPLOYMENT% %K8S_CONTAINER%=${imageVersion}
                                    kubectl rollout status deployment/%K8S_DEPLOYMENT% --timeout=180s
                                """
                            } else if (strategy == 'blue-green') {
                                bat """
                                    set "KUBECONFIG=%KUBECONFIG_FILE%"
                                    kubectl apply -f k8s/service.yaml
                                    kubectl apply -f k8s/deployment-${blueGreenTarget}.yaml
                                    kubectl set image deployment/%K8S_DEPLOYMENT%-${blueGreenTarget} %K8S_CONTAINER%=${imageVersion}
                                    kubectl rollout status deployment/%K8S_DEPLOYMENT%-${blueGreenTarget} --timeout=180s
                                    kubectl apply -f k8s/service-${blueGreenTarget}.yaml
                                """
                            } else if (strategy == 'canary') {
                                bat """
                                    set "KUBECONFIG=%KUBECONFIG_FILE%"
                                    kubectl delete deployment %K8S_DEPLOYMENT%-blue %K8S_DEPLOYMENT%-green %K8S_DEPLOYMENT%-ab --ignore-not-found
                                    kubectl apply -f k8s/service.yaml
                                    kubectl scale deployment/%K8S_DEPLOYMENT% --replicas=${stableReplicas}
                                    kubectl apply -f k8s/deployment-canary.yaml
                                    kubectl set image deployment/%K8S_DEPLOYMENT%-canary %K8S_CONTAINER%=${imageVersion}
                                    kubectl scale deployment/%K8S_DEPLOYMENT%-canary --replicas=${canaryReplicas}
                                    kubectl rollout status deployment/%K8S_DEPLOYMENT%-canary --timeout=180s
                                """
                            } else if (strategy == 'shadow') {
                                bat """
                                    set "KUBECONFIG=%KUBECONFIG_FILE%"
                                    kubectl apply -f k8s/deployment-shadow.yaml
                                    kubectl set image deployment/%K8S_DEPLOYMENT%-shadow %K8S_CONTAINER%=${imageVersion}
                                    kubectl rollout status deployment/%K8S_DEPLOYMENT%-shadow --timeout=180s
                                """
                            } else if (strategy == 'ab-test') {
                                bat """
                                    set "KUBECONFIG=%KUBECONFIG_FILE%"
                                    kubectl delete deployment %K8S_DEPLOYMENT%-blue %K8S_DEPLOYMENT%-green %K8S_DEPLOYMENT%-canary --ignore-not-found
                                    kubectl apply -f k8s/service.yaml
                                    kubectl scale deployment/%K8S_DEPLOYMENT% --replicas=${stableReplicas}
                                    kubectl apply -f k8s/deployment-ab.yaml
                                    kubectl set image deployment/%K8S_DEPLOYMENT%-ab %K8S_CONTAINER%=${imageVersion}
                                    kubectl scale deployment/%K8S_DEPLOYMENT%-ab --replicas=${canaryReplicas}
                                    kubectl rollout status deployment/%K8S_DEPLOYMENT%-ab --timeout=180s
                                """
                            }
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
