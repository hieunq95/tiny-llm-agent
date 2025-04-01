pipeline {
    agent any

    environment {
        REPO_URL = 'https://github.com/hieunq95/tiny-llm-agent.git'
        BRANCH = 'chore/update-codecov'
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
            steps {
                // Run pytest and generate code coverage report
                echo 'Testing rag-pipeline backend'
                sh '''
                    docker exec -e PYTHON_PATH="${PYTHON_PATH}" python bash -c "\
                    cd rag-pipeline && \
                    pip install --no-cache-dir -r requirements.txt && \
                    export PYTHONPATH=${PYTHON_PATH} OTEL_SDK_DISABLED=true && \
                    pytest --cov=src \
                           --cov-report=xml:coverage.xml \
                           --junitxml=test-reports/results.xml \
                           tests/
                           "
                '''
                sh 'docker cp python:/rag-pipeline/coverage.xml ./rag-pipeline/coverage.xml'
                // Check if coverage passes the threshold
                script {
                    echo 'Checking code coverage'
                    def lineRate = sh(
                        script: 'grep -m1 "line-rate" rag-pipeline/coverage.xml | sed -n \'s/.*line-rate="\\([^"]*\\).*/\\1/p\'',
                        returnStdout: true
                    ).trim()
                    echo "Line Rate: ${lineRate}"

                    float coverage = lineRate.toFloat()
                    if (coverage < 0.8) {
                    error("Code coverage too low: ${coverage * 100}%")
                    } else {
                    echo "Coverage is sufficient: ${coverage * 100}%"
                    }
                }
            }
        }

        stage('Upload Coverage') {
            steps {
                script {
                    sh '''
                        docker exec python bash -c "\
                        cd rag-pipeline && \
                        export CODECOV_TOKEN=${CODECOV_TOKEN} && \
                        curl -s https://codecov.io/bash | bash -s -- -t $CODECOV_TOKEN -f coverage.xml
                        "
                    '''
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
                    // sh 'docker-compose -f docker-compose.yml up -d'
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