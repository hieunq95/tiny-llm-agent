pipeline {
    agent any

    environment {
        REPO_URL = 'https://github.com/hieunq95/tiny-llm-agent.git'
        BRANCH = 'features'
        SERVICE_NAME = 'tiny-llm-agent'
        VENV_PATH = './venv'
        PYTHON_PATH = '/rag-pipeline/src'
        CODECOV_TOKEN = credentials('codecov-token')
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo 'Cloning repository from ' + REPO_URL
                git branch: "${BRANCH}", url: "${REPO_URL}", credentialsId: "github-pat"
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    echo 'Setting up Python virtual environment'
                    sh 'python3 -m venv ${VENV_PATH}'
                    sh 'source ${VENV_PATH}/bin/activate'
                    sh 'pip install -r rag-pipeline/requirements.txt'
                    sh 'cd rag-pipeline'
                    sh 'DISABLE_TRACING=true pytest --cov=src test/'
                    sh 'pytest --cov=${PYTHON_PATH} --cov-report=xml:coverage.xml --junitxml=test-reports/results.xml test/'
                    echo 'Saving test reports'
                    archiveArtifacts artifacts: 'coverage.xml', fingerprint: true
                    archiveArtifacts artifacts: 'test-reports/results.xml', fingerprint: true
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

        stage('Build') {
            steps {
                script {
                    echo 'Building Docker image for rag-pipeline backend'
                    sh 'docker-compose -f jenkins/docker-compose.yml up --build'
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