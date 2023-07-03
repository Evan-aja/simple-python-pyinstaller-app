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
                        sh "cp -r sources/dist/add2vals ."
                        
                        def release = sh(script: "curl -XPOST -H 'Authorization:token ${env.GITHUB_TOKEN}' --data '{\"tag_name\": \"${RELEASE_NAME}\", \"target_commitish\": \"master\", \"name\": \"${env.GITHUB_REPO_FULL}\", \"body\": \"Description of the release\", \"draft\": false, \"prerelease\": true}' https://api.github.com/repos/${env.GITHUB_REPO_FULL}/releases", returnStdout: true).trim()

                        def id = sh(script: "echo \"${release}\" | sed -n -e 's/\"id\":\\ \\([0-9]\\+\\),/\\1/p' | head -n 1 | sed 's/[[:blank:]]//g'", returnStdout: true).trim()

                        sh "echo \"${id}\""

                        sh "curl -X POST -H \"Authorization: Bearer ${GITHUB_TOKEN}\" -H \"Content-Type: application/octet-stream\" --data-binary @add2vals https://uploads.github.com/repos/${env.GITHUB_REPO_FULL}/releases/${id}/assets?name=add2vals"
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