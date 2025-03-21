pipeline {
    agent any

    environment {
        REPO_URL = 'https://github.com/hieunq95/tiny-llm-agent.git'
        BRANCH = 'features'
        SERVICE_NAME = 'tiny-llm-agent'
        VENV_PATH = '/opt/venv'
        PYTHON_PATH = '/rag-pipeline/src'
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo 'Cloning repository from ' + REPO_URL
                git branch: "${BRANCH}", url: "${REPO_URL}", credentialsId: "github-pat"
            }
        }

        stage('Build') {
            steps {
                script {
                    echo 'Building Docker image for rag-pipeline backend'
                    // Build and start containers in detached mode.
                    sh 'docker-compose -f jenkins/docker-compose.yml up --build -d --no-recreate'
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    echo 'Running unit tests on backend'
                    sh 'docker exec rag-pipeline bash -c "export PYTHONPATH=/rag-pipeline/src DISABLE_TRACING=true && pytest --cov=src --cov-report=xml:coverage.xml --junitxml=test-reports/results.xml test/ "'
                    sh 'docker cp rag-pipeline:/rag-pipeline/coverage.xml ./coverage.xml'
                }
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

        stage('Cleanup') {
            steps {
                script {
                    sh 'docker-compose -f jenkins/docker-compose.yml down -v'
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