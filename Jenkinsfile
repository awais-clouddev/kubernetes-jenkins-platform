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

            stage('Security Scan - Trivy') {
                def frontendScanStatus = 0
                def apiScanStatus = 0

                withCredentials([usernamePassword(
                    credentialsId: 'ghcr-credentials',
                    usernameVariable: 'TRIVY_USERNAME',
                    passwordVariable: 'TRIVY_PASSWORD'
                )]) {
                    container('trivy') {

                        sh '''
                            set +x

                            mkdir -p \
                              "$WORKSPACE/evidence/phase10-pipeline" \
                              "$TRIVY_CACHE_DIR"
                        '''

                        frontendScanStatus = sh(
                            script: '''
                                set +x

                                FRONTEND_IMAGE="ghcr.io/awais-clouddev/kubernetes-jenkins-platform-frontend@${FRONTEND_DIGEST}"

                                echo "TRIVY_FRONTEND_SCAN_START=${FRONTEND_IMAGE}"

                                trivy image \
                                  --cache-dir "$TRIVY_CACHE_DIR" \
                                  --scanners vuln \
                                  --severity HIGH,CRITICAL \
                                  --ignore-unfixed \
                                  --exit-code 1 \
                                  --format json \
                                  --output "$WORKSPACE/evidence/phase10-pipeline/trivy-frontend.json" \
                                  "$FRONTEND_IMAGE"
                            ''',
                            returnStatus: true
                        )

                        if (frontendScanStatus == 0) {
                            echo "TRIVY_FRONTEND_SCAN_PASS=${env.FRONTEND_DIGEST}"
                        } else {
                            echo "TRIVY_FRONTEND_SCAN_FAIL=${env.FRONTEND_DIGEST}"
                        }

                        apiScanStatus = sh(
                            script: '''
                                set +x

                                API_IMAGE="ghcr.io/awais-clouddev/kubernetes-jenkins-platform-api@${API_DIGEST}"

                                echo "TRIVY_API_SCAN_START=${API_IMAGE}"

                                trivy image \
                                  --cache-dir "$TRIVY_CACHE_DIR" \
                                  --scanners vuln \
                                  --severity HIGH,CRITICAL \
                                  --ignore-unfixed \
                                  --exit-code 1 \
                                  --format json \
                                  --output "$WORKSPACE/evidence/phase10-pipeline/trivy-api.json" \
                                  "$API_IMAGE"
                            ''',
                            returnStatus: true
                        )

                        if (apiScanStatus == 0) {
                            echo "TRIVY_API_SCAN_PASS=${env.API_DIGEST}"
                        } else {
                            echo "TRIVY_API_SCAN_FAIL=${env.API_DIGEST}"
                        }
                    }
                }

                withEnv([
                    "FRONTEND_SCAN_STATUS=${frontendScanStatus}",
                    "API_SCAN_STATUS=${apiScanStatus}"
                ]) {
                    container('python') {
                        sh '''
                            python - <<'PY2'
import json
import os
from pathlib import Path

evidence = Path("evidence/phase10-pipeline")
evidence.mkdir(parents=True, exist_ok=True)

frontend_status = int(os.environ["FRONTEND_SCAN_STATUS"])
api_status = int(os.environ["API_SCAN_STATUS"])

deploy_eligible = (
    frontend_status == 0 and
    api_status == 0
)

gate = {
    "deployEligible": deploy_eligible,
    "gitSha": os.environ["GIT_COMMIT"],
    "frontend": {
        "image": "ghcr.io/awais-clouddev/kubernetes-jenkins-platform-frontend",
        "digest": os.environ["FRONTEND_DIGEST"],
        "trivyGate": "PASS" if frontend_status == 0 else "FAIL",
        "scanExitCode": frontend_status
    },
    "api": {
        "image": "ghcr.io/awais-clouddev/kubernetes-jenkins-platform-api",
        "digest": os.environ["API_DIGEST"],
        "trivyGate": "PASS" if api_status == 0 else "FAIL",
        "scanExitCode": api_status
    },
    "policy": {
        "scanner": "Trivy",
        "severity": ["HIGH", "CRITICAL"],
        "ignoreUnfixed": True
    }
}

(evidence / "trivy-gate.json").write_text(
    json.dumps(gate, indent=2) + "\\n"
)

deploy_file = evidence / "deploy-eligible.json"

if deploy_eligible:
    deploy_file.write_text(
        json.dumps(gate, indent=2) + "\\n"
    )
elif deploy_file.exists():
    deploy_file.unlink()
PY2
                        '''
                    }
                }

                echo "TRIVY_FRONTEND_EXIT_CODE=${frontendScanStatus}"
                echo "TRIVY_API_EXIT_CODE=${apiScanStatus}"

                archiveArtifacts(
                    artifacts: 'evidence/phase10-pipeline/**',
                    fingerprint: true
                )

                if (frontendScanStatus != 0 || apiScanStatus != 0) {
                    error(
                        "Trivy security gate failed: frontend=${frontendScanStatus}, api=${apiScanStatus}"
                    )
                }

                echo "PIPELINE_OUTPUT_DEPLOY_ELIGIBLE=true"
                echo "DEPLOY_ELIGIBLE_FRONTEND_DIGEST=${env.FRONTEND_DIGEST}"
                echo "DEPLOY_ELIGIBLE_API_DIGEST=${env.API_DIGEST}"
            }

        } finally {
            deleteDir()
        }
    }
}
