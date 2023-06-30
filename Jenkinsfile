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
        sh 'sh \'python -m py_compile sources/add2vals.py sources/calc.py\''
      }
    }

    stage('Test') {
      agent {
        docker {
          image 'qnib/pytest'
        }

      }
      steps {
        sh 'sh \'py.test --verbose --junit-xml test-reports/results.xml sources/test_calc.py\''
        junit 'test-reports/results.xml'
      }
    }

    stage('Deliver') {
      agent {
        docker {
          image 'cdrx/pyinstaller-linux:python2'
        }

      }
      steps {
        sh 'sh \'pyinstaller --onefile sources/add2vals.py\''
        archiveArtifacts 'dist/add2vals'
      }
    }

  }
}