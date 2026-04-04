pipeline {
    agent any

    environment {
        APP_IMAGE = 'aceest-fitness-app'
        DEV_CONTAINER = 'aceest-fitness-api-dev'
        PROD_CONTAINER = 'aceest-fitness-api-prod'
        DEV_PORT = '5001'
        PROD_PORT = '5000'
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

        stage('Build Docker Image') {
            steps {
                script {
                    def imageVersion = "${env.APP_IMAGE}:${env.BUILD_NUMBER}"
                    def imageLatest = "${env.APP_IMAGE}:latest"

                    // Docker commands are usually the same across platforms if Docker Desktop is installed
                    if (isUnix()) {
                        sh "docker build -t ${imageVersion} -t ${imageLatest} ."
                    } else {
                        bat "docker build -t ${imageVersion} -t ${imageLatest} ."
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

        stage('Deploy to DEV') {
            when {
                expression {
                    def rawBranch = env.BRANCH_NAME ?: env.GIT_BRANCH ?: ''
                    def normalizedBranch = rawBranch.replaceFirst('^origin/', '').replaceFirst('^refs/heads/', '')
                    return normalizedBranch == 'develop'
                }
            }
            steps {
                script {
                    def imageVersion = "${env.APP_IMAGE}:${env.BUILD_NUMBER}"

                    if (isUnix()) {
                        sh """
                            docker rm -f ${env.DEV_CONTAINER} 2>/dev/null || true
                            docker run -d --name ${env.DEV_CONTAINER} \\
                                -p ${env.DEV_PORT}:5000 \\
                                --restart unless-stopped \\
                                ${imageVersion}
                        """
                    } else {
                        bat """
                            docker rm -f %DEV_CONTAINER% 2>nul || echo DEV container not present
                            docker run -d --name %DEV_CONTAINER% ^
                                -p %DEV_PORT%:5000 ^
                                --restart unless-stopped ^
                                ${imageVersion}
                        """
                    }
                }
            }
        }

        stage('Deploy to PROD') {
            when {
                expression {
                    def rawBranch = env.BRANCH_NAME ?: env.GIT_BRANCH ?: ''
                    def normalizedBranch = rawBranch.replaceFirst('^origin/', '').replaceFirst('^refs/heads/', '')
                    return normalizedBranch == 'main'
                }
            }
            steps {
                script {
                    def imageVersion = "${env.APP_IMAGE}:${env.BUILD_NUMBER}"

                    if (isUnix()) {
                        sh """
                            docker rm -f ${env.PROD_CONTAINER} 2>/dev/null || true
                            docker run -d --name ${env.PROD_CONTAINER} \\
                                -p ${env.PROD_PORT}:5000 \\
                                --restart unless-stopped \\
                                ${imageVersion}
                        """
                    } else {
                        bat """
                            docker rm -f %PROD_CONTAINER% 2>nul || echo PROD container not present
                            docker run -d --name %PROD_CONTAINER% ^
                                -p %PROD_PORT%:5000 ^
                                --restart unless-stopped ^
                                ${imageVersion}
                        """
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