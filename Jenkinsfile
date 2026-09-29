node('k8s-build-agent') {

    timeout(time: 30, unit: 'MINUTES') {

        try {

            stage('Checkout') {
                def scmVars = checkout scm
                env.GIT_COMMIT = scmVars.GIT_COMMIT
                echo "Checked out commit: ${env.GIT_COMMIT}"
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
                        pip install --quiet -r api/requirements.txt httpx
                        pip install --quiet --upgrade "pytest>=8.3,<9"
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

            stage('Build and Push Images') {
                withCredentials([usernamePassword(
                    credentialsId: 'ghcr-credentials',
                    usernameVariable: 'GHCR_USERNAME',
                    passwordVariable: 'GHCR_TOKEN'
                )]) {
                    container('buildctl') {
                        sh '''
                            set +x

                            mkdir -p "$WORKSPACE/.docker" "$WORKSPACE/evidence/phase10-pipeline"

                            cleanup_registry_auth() {
                                rm -f "$WORKSPACE/.docker/config.json"
                                rmdir "$WORKSPACE/.docker" 2>/dev/null || true
                            }

                            trap cleanup_registry_auth EXIT

                            cat > "$WORKSPACE/.docker/config.json" <<EOF
{"auths":{"ghcr.io":{"username":"${GHCR_USERNAME}","password":"${GHCR_TOKEN}"}}}
EOF

                            chmod 600 "$WORKSPACE/.docker/config.json"
                            export DOCKER_CONFIG="$WORKSPACE/.docker"

                            buildctl \
                              --addr "$BUILDKIT_HOST" \
                              --tlscacert "$BUILDKIT_TLS_CACERT" \
                              --tlscert "$BUILDKIT_TLS_CERT" \
                              --tlskey "$BUILDKIT_TLS_KEY" \
                              build \
                              --frontend dockerfile.v0 \
                              --local context=frontend \
                              --local dockerfile=frontend \
                              --output type=image,name=ghcr.io/awais-clouddev/kubernetes-jenkins-platform-frontend:${GIT_COMMIT},push=true \
                              --metadata-file "$WORKSPACE/evidence/phase10-pipeline/frontend-metadata.json"

                            buildctl \
                              --addr "$BUILDKIT_HOST" \
                              --tlscacert "$BUILDKIT_TLS_CACERT" \
                              --tlscert "$BUILDKIT_TLS_CERT" \
                              --tlskey "$BUILDKIT_TLS_KEY" \
                              build \
                              --frontend dockerfile.v0 \
                              --local context=api \
                              --local dockerfile=api \
                              --output type=image,name=ghcr.io/awais-clouddev/kubernetes-jenkins-platform-api:${GIT_COMMIT},push=true \
                              --metadata-file "$WORKSPACE/evidence/phase10-pipeline/api-metadata.json"

                            echo "BUILDKIT_GHCR_PUSH_COMPLETE"
                        '''
                    }
                }

                container('python') {
                    env.FRONTEND_DIGEST = sh(
                        script: '''
                            python -c 'import json; print(json.load(open("evidence/phase10-pipeline/frontend-metadata.json"))["containerimage.digest"])'
                        ''',
                        returnStdout: true
                    ).trim()

                    env.API_DIGEST = sh(
                        script: '''
                            python -c 'import json; print(json.load(open("evidence/phase10-pipeline/api-metadata.json"))["containerimage.digest"])'
                        ''',
                        returnStdout: true
                    ).trim()
                }

                if (!(env.FRONTEND_DIGEST ==~ /^sha256:[0-9a-f]{64}$/)) {
                    error("Invalid frontend image digest: ${env.FRONTEND_DIGEST}")
                }

                if (!(env.API_DIGEST ==~ /^sha256:[0-9a-f]{64}$/)) {
                    error("Invalid API image digest: ${env.API_DIGEST}")
                }

                writeFile(
                    file: 'evidence/phase10-pipeline/frontend-digest.txt',
                    text: "${env.FRONTEND_DIGEST}\n"
                )

                writeFile(
                    file: 'evidence/phase10-pipeline/api-digest.txt',
                    text: "${env.API_DIGEST}\n"
                )

                writeFile(
                    file: 'evidence/phase10-pipeline/source-git-sha.txt',
                    text: "${env.GIT_COMMIT}\n"
                )

                echo "PIPELINE_OUTPUT_GIT_SHA=${env.GIT_COMMIT}"
                echo "PIPELINE_OUTPUT_FRONTEND_DIGEST=${env.FRONTEND_DIGEST}"
                echo "PIPELINE_OUTPUT_API_DIGEST=${env.API_DIGEST}"

                archiveArtifacts(
                    artifacts: 'evidence/phase10-pipeline/**',
                    fingerprint: true
                )
            }

        } finally {
            deleteDir()
        }
    }
}
