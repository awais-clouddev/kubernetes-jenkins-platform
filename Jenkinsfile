node('k8s-build-agent') {

    timeout(time: 30, unit: 'MINUTES') {

        try {

            stage('Checkout') {
                checkout scm
            }

            stage('Validation') {
                container('python') {
                    sh '''
                        test -f api/Dockerfile
                        test -f api/requirements.txt
                        test -f frontend/Dockerfile
                        test -f frontend/index.html
                        test -f frontend/app.js
                        python -m py_compile api/app/main.py
                    '''
                }
            }

            stage('Backend Tests') {
                container('python') {
                    sh '''
                        python -m venv .venv
                        . .venv/bin/activate
                        pip install --quiet -r api/requirements.txt pytest httpx
                        PYTHONPATH=api pytest -q api/tests
                    '''
                }
            }

            stage('Frontend Tests') {
                sh '''
                    test -s frontend/index.html
                    test -s frontend/app.js
                    test -s frontend/style.css
                    grep -qi '<html' frontend/index.html
                    echo FRONTEND_TEST_OK
                '''
            }

        } finally {
            deleteDir()
        }
    }
}
