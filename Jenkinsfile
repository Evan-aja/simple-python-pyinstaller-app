pipeline {
    agent none
    stages {
        stage('Build') {
            agent {
                docker {
                    image 'python:2-alpine'
                }
            }
            steps {
                sh 'pwd'
                sh 'ls -l'
                sh 'python -m py_compile sources/add2vals.py sources/calc.py'
                stash(name: 'compiled-sources', includes: 'sources/*.py*')
            }
        }
        stage('Test') {
            agent {
                docker {
                    image 'qnib/pytest'
                }
            }
            steps {
                sh 'py.test --verbose --junit-xml test-reports/results.xml sources/test_calc.py'
            }
            post {
                always {
                    junit 'test-reports/results.xml'
                }
            }
        }
        stage('Deliver') {
            agent any
            environment {
                VOLUME = '$(pwd)/sources:/src'
                IMAGE = 'cdrx/pyinstaller-linux:python2'
            }
            steps {
                dir(path: env.BUILD_ID){
                    unstash 'compiled-sources'
                    sh "docker run --rm -v ${VOLUME} ${IMAGE} 'pyinstaller -F add2vals.py'"
                }
            }
            post {
                success {
                    archiveArtifacts "${env.BUILD_ID}/sources/dist/add2vals"
                    sh "docker run --rm -v ${VOLUME} ${IMAGE} 'rm -rf build dist'"
                }
            }
        }
        stage('Publish') {
            agent any
            environment {
                RELEASE_NAME = 'v1.0.0'
                RELEASE_DESCRIPTION = 'Release description'
                GITHUB_TOKEN = credentials('github-token-id')
                GITHUB_URL = credentials('github-url-id')
            }
            steps {
                dir(path: env.BUILD_ID) {
                    sh "git clone $GITHUB_URL"
                    sh "cp -r sources/dist/add2vals simple-python-pyinstaller-app/"
                    sh "cd simple-python-pyinstaller-app"
                    sh "git tag $RELEASE_NAME"
                    sh "git push --tags"
                    sh "hub release create -a add2vals -m $RELEASE_DESCRIPTION $RELEASE_NAME"
                }
            }
        }
    }
}