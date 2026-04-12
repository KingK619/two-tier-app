pipeline {
    agent any
    stages {
        stage('Pull Code') {
            steps { checkout scm }
        }
        stage('Deploy Application') {
            steps {
                sh 'docker compose down || true'
                sh 'docker compose up -d --build'
                }
        }
    }
}