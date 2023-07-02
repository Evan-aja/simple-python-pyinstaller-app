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
                GITHUB_REPO = credentials('github-url-id')
                GITHUB_TOKEN = credentials('your-github-token-id')
                
            }
            steps {
                script {
                    def existingTags = sh(script: "git ls-remote --tags https://github.com/${env.GITHUB_REPO} | awk -F/ '{ print $3 }' | sort -Vr", returnStdout: true).trim()
                    def latestTag = existingTags.tokenize('\n').first()
                    def releaseName = getNextReleaseName(latestTag)

                    dir(path: env.BUILD_ID) {
                        sh "git clone ${env.GITHUB_REPO}"
                        sh "cp -r sources/dist/add2vals ${env.GITHUB_REPO}/"
                        sh "cd ${env.GITHUB_REPO}"
                        sh "git tag ${releaseName}"
                        sh "git push --tags"
                        sh "hub release create -a add2vals -m ${releaseName} ${releaseName}"
                    }
                }
            }
        }
    }
}

def getNextReleaseName(latestTag) {
    if (latestTag) {
        def versionParts = latestTag.tokenize('.')
        int lastPart = versionParts.last().toInteger()
        versionParts[versionParts.size() - 1] = (lastPart + 1).toString()
        return versionParts.join('.')
    } else {
        return 'v1.0.0'
    }
}