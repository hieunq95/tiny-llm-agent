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
                    cd rag-pipeline
                    pip install -r requirements.txt
                    export PYTHONPATH=${PYTHON_PATH}
                    export DISABLE_TRACING=true
                    pytest --cov=src \
                           --cov-report=xml:coverage.xml \
                           --junitxml=test-reports/results.xml \
                           test/
                '''
            }
        }

        stage('Upload Coverage') {
            steps {
                script {
                    echo 'Uploading coverage report to Codecov'
                    sh '''
                        cd rag-pipeline
                        curl -s https://codecov.io/bash | bash -s -- -t $CODECOV_TOKEN -f coverage.xml
                    '''
                }
            }
        }

        stage('Check Coverage') {
            steps {
                script {
                    def coverageFile = 'rag-pipeline/coverage.xml'
                    // Wait for file to be available
                    waitUntil {
                        fileExists(coverageFile)
                    }
                    // Verify file content
                    def coverage = readFile(coverageFile)
                    def matcher = (coverage =~ /line-rate="([^"]+)"/)
                    if (!matcher) {
                        error("Failed to parse ${coverageFile}!")
                    }
                    def coveragePercent = (matcher[0][1].toFloat() * 100).round(2)
                    
                    if (coveragePercent < 80) {
                        error("Coverage ${coveragePercent}% is below the 80% threshold!")
                    } else {
                        echo "Coverage ${coveragePercent}% meets requirements ✅"
                    }
                }
            }
        }

        stage('Build') {
            agent any
            steps {
                script {
                    echo 'Building images'
                    sh 'docker-compose -f docker-compose.yml build --no-cache'
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    echo 'Deploying services'
                    sh 'docker-compose -f docker-compose.yml up -d'
                }
            }
        }
    }

    post {
        always {
            echo "Pipeline execution complete."
            sh 'docker-compose -f docker-compose.yml down -v'
        }
        failure {
            echo "Pipeline failed. Please check the logs."
        }
        success {
            echo "Pipeline succeeded. Your deployment is live!"
        }
    }
}