pipeline {
    agent any

    environment {
        REPO_URL = 'https://github.com/hieunq95/tiny-llm-agent.git'
        BRANCH = 'dev-cicd'
        SERVICE_NAME = 'tiny-llm-agent'
        PYTHON_PATH = '/rag-pipeline/src'
        CODECOV_TOKEN = credentials('CODECOV_TOKEN')
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo 'Cloning repository from ' + REPO_URL
                git branch: "${BRANCH}", url: "${REPO_URL}", credentialsId: "github-pat"
            }
        }

        stage('Test') {
            agent {
                docker {
                    image 'python:3.10-slim'
                }
            }
            steps {
                echo 'Testing rag-pipeline backend'
                sh '''
                    pip install -r rag-pipeline/requirements.txt \
                    bash -c "export PYTHONPATH=${PYTHON_PATH} DISABLE_TRACING=true && pytest --cov=src --cov-report=xml:coverage.xml --junitxml=test-reports/results.xml test/ 
                '''
            }
        }

        stage('Upload Coverage') {
            steps {
                script {
                    // Upload coverage to Codecov
                    sh '''
                        curl -s https://codecov.io/bash | bash -s -- -t $CODECOV_TOKEN -f coverage.xml
                    '''
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    echo 'Building image for rag-pipeline backend'
                    // Build and start containers in detached mode.
                    sh 'docker-compose -f jenkins/docker-compose.yml build --no-cache'
                }
            }
        }

        stage('Check Coverage') {
            steps {
                script {
                    echo 'Checking coverage'
                }
            }
        }
    }

    post {
        always {
            echo "Pipeline execution complete."
        }
        failure {
            echo "Pipeline failed. Please check the logs."
        }
        success {
            echo "Pipeline succeeded. Your deployment is live!"
        }
    }
}