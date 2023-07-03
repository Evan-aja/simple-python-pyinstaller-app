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
                GITHUB_USERNAME = credentials('github-user-name')
                GITHUB_REPO = credentials('github-repo-name')
                GITHUB_REPO_FULL = "${GITHUB_USERNAME}/${GITHUB_REPO}"
                GITHUB_TOKEN = credentials('github-token-id')
                GIT_USERNAME = credentials('git-user-name')
                GIT_EMAIL = credentials('git-user-email')
                RELEASE_NAME = 'v1.0.0'
            }
            steps {
                script {
                    def existingRelease = sh(script: "curl -sSL -H 'Accept: application/vnd.github+json' -H 'Authorization: Bearer ${env.GITHUB_TOKEN}' -H 'X-GitHub-Api-Version: 2022-11-28' https://api.github.com/repos/${env.GITHUB_REPO_FULL}/releases", returnStdout: true).trim()


                    if (existingRelease) {
                        def latestTag = findLatestTag(existingRelease)
                        RELEASE_NAME = getNextReleaseName(latestTag)
                    }
                    dir(path: env.BUILD_ID) {
                        sh "git clone https://github.com/${env.GITHUB_USERNAME}/${env.GITHUB_REPO}.git"
                        sh "cp -r sources/dist/add2vals ${env.GITHUB_REPO}/"
                        sh "cd ${env.GITHUB_REPO}"
                        sh "git config user.email \"${env.GIT_EMAIL}\""
                        sh "git config user.name \"${env.GIT_USERNAME}\""
                        sh "git tag \"${RELEASE_NAME}\""
                        sh "GIT_ASKPASS=true GIT_USERNAME=${env.GIT_USERNAME} GIT_PASSWORD=${env.GITHUB_TOKEN} git push --tags"
                        sh "curl -sSL -X POST -H \"Accept: application/vnd.github+json\" -H \"Authorization: Bearer ${env.GITHUB_TOKEN}\" -H \"X-GitHub-Api-Version: 2022-11-28\" https://api.github.com/repos/${env.GITHUB_REPO_FULL}/releases -d \"{\"tag_name\":\"${RELEASE_NAME}\",\"target_commitish\":\"master\",\"name\":\"${RELEASE_NAME}\",\"body\":\"Description of the release\",\"draft\":false,\"prerelease\":false,\"generate_release_notes\":false}\""
                    }
                }
            }
        }
    }
}

def findLatestTag(existingRelease) {
    def releases = new groovy.json.JsonSlurper().parseText(existingRelease)
    def latestTag = releases.find { release -> release.tag_name }?.tag_name
    return latestTag ?: ''
}

def getNextReleaseName(latestTag) {
    if (latestTag) {
        def versionParts = latestTag.tokenize('.')
        int lastPart = versionParts.last().toInteger()
        versionParts[versionParts.size() - 1] = (lastPart + 1).toString()
        return versionParts.join('.')
    } else {
        return RELEASE_NAME
    }
}