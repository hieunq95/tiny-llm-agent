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
            steps {
                echo 'Testing rag-pipeline backend'
                sh '''
                    docker exec python bash -c "\
                    cd rag-pipeline && \
                    pip install --no-cache-dir -r requirements.txt && \
                    export PYTHONPATH=${PYTHON_PATH} DISABLE_TRACING=true && \
                    pytest --cov=src \
                           --cov-report=xml:coverage.xml \
                           --junitxml=test-reports/results.xml \
                           test/
                           "
                '''
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

        stage('Check Coverage') {
            steps {
                script {
                    echo 'Checking code coverage'
                    // env.WORKSPACE = pwd()   
                    // def fileContent = readFile "${env.WORKSPACE}/rag-pipeline/coverage.xml"
                    // def xml = new XmlSlurper().parseText(fileContent)
                    // def lineRate = xml.@'line-rate'.text()
                    def lineRate = sh(
                        script: 'grep "line-rate" rag-pipeline/coverage.xml | sed -n \'s/.*line-rate="\\([^"]*\\).*/\\1/p\'',
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