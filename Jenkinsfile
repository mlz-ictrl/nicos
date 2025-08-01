#!groovy

//*** job setup */
properties([
    buildDiscarder(logRotator(artifactDaysToKeepStr: '',
                              artifactNumToKeepStr: '',
                              daysToKeepStr: '',
                              numToKeepStr: '50')),
    parameters([
        string(defaultValue: 'frm2/nicos/nicos',
               description: '', name: 'GERRIT_PROJECT'),
        string(defaultValue: 'refs/heads/master',
               description: '', name: 'GERRIT_BRANCH'),
        string(defaultValue: 'refs/heads/master',
               description: '', name: 'GERRIT_REFSPEC'),
        choice(choices: '''\
patchset-created
ref-updated
change-merged''',
        description: '', name: 'GERRIT_EVENT_TYPE')]),
        [$class: 'ScannerJobProperty', doNotScan: false],
        [$class: 'RebuildSettings', autoRebuild: false, rebuildDisabled: false],
        [$class: 'ThrottleJobProperty', categories: [],
            limitOneJobWithMatchingParams: true,
            maxConcurrentPerNode: 30,
            maxConcurrentTotal: 70,
            paramsToUseForLimit: 'GERRIT_REFSPEC',
            throttleEnabled: true,
            throttleOption: 'project'],
        pipelineTriggers([gerrit(silent:true,
                                 commentTextParameterMode: 'PLAIN',
                                 commitMessageParameterMode: 'PLAIN',
                                 customUrl: '',
                                 gerritProjects: [
                                     [pattern: 'frm2/nicos/nicos',
                                      compareType: 'PLAIN',
                                      disableStrictForbiddenFileVerification: false,
                                      branches: [[compareType: 'PLAIN', pattern: 'master'],
                                                 [compareType: 'REG_EXP', pattern: 'release-.*'],
                                                 [compareType: 'REG_EXP', pattern: 'feature-.*'],
                                                 [compareType: 'PLAIN', pattern: 'hidden']
                                                 ],
                                 ]],
                                 serverName: 'defaultServer',
                                 triggerOnEvents: [
                                        patchsetCreated(excludeDrafts: false,
                                                        excludeNoCodeChange: false,
                                                        excludeTrivialRebase: false),
                                        changeMerged(),
                                        commentAddedContains('@recheck')
                                        ]
                                    )])
    ])

// ************* Global arrays  ***/

this.verifyresult = [:]
this.pipissues = []

// ************* Function defs ***/


def checkoutSource() {
    echo(GERRIT_PROJECT)
    deleteDir()
    gerrit_checkout()
    sh "git describe"
}

def publishGerrit(name, value) {
    def map = [(-1): "FAILED", 0: "RUNNING", 1: "SUCCESSFUL"]
    gerritPostCheck(["jenkins:${name}": map[value]])
}


def refreshVenv(info="" , venv='$NICOS3VENV', checkupdates=false) {
    try {
        sh "./ciscripts/run_venvupdate.sh $venv $info"
    } catch (all) {
        echo "Could not run venv update, let's hope the image has all dependencies"
    }

    if (info?.trim()) {
        archiveArtifacts([allowEmptyArchive: true, artifacts: "pip-*.log"])
    }
    if (checkupdates) {
        // currently only core requirements are checked
        this.pipissues.add(scanForIssues(tool: groovyScript(id: 'pip-updates',
                                         name: 'pip updates',
                                         parserId: 'pip-output-updated-ng',
                                         pattern: 'pip-core-*.log')))
        this.pipissues.add(scanForIssues(tool: groovyScript(id: 'pip-errors',
                                         name: 'pip errors',
                                         parserId: 'pip-output-error-ng',
                                         pattern: 'pip-core-*.log')))
        this.pipissues.add(scanForIssues(tool: groovyScript(id: 'pip-errors-compile',
                                         name: 'pip errors',
                                         parserId: 'pip-output-error-compile-ng',
                                         pattern: 'pip-core-*.log')))
    }
}

def runPylint(info='', venv='$NICOS3VENV') {
    def idtag = "pylint-$info".toString()
    verifyresult.put(idtag, 0)
    publishGerrit(idtag,verifyresult[idtag])
    try {
        withCredentials([string(credentialsId: 'GERRITHTTP', variable: 'GERRITHTTP')]) {
            try {
                refreshVenv("$idtag", venv)
            } catch (all) {
                echo "refreshVenv failed"
            }

            sh "./ciscripts/run_pylint.sh $venv"

            verifyresult.put(idtag, 1)
        }
    }
    catch (all) {
        verifyresult.put(idtag,-1)
    }

    try {
        sh """
if [ -f pylint_all.txt ] ; then
    mv pylint_all.txt ${idtag}.txt
else
    touch ${idtag}.txt
fi"""
    } catch (all) {
        echo "Move failed?"
    }
    echo "********************"
    echo "${idtag}: result=" + verifyresult[idtag]
    echo "********************"

    publishGerrit(idtag,verifyresult[idtag])
    archiveArtifacts([allowEmptyArchive: true,
                          artifacts: 'pylint-*.txt'])
    recordIssues([enabledForFailure: true,
                  ignoreQualityGate: true,
                  tools: [pyLint(id: idtag, name: "Pylint $info", pattern: 'pylint-*.txt')],
                  unhealthy: 2,
                  healthy: 1,
                  failedTotalAll: 1])


    if (verifyresult[idtag] < 0) {
        error("Failure in $idtag")
    }
}

def runIsort() {
    verifyresult.put('isort',0)
    publishGerrit('isort', verifyresult['isort'])
    try {
        withCredentials([string(credentialsId: 'GERRITHTTP', variable: 'GERRITHTTP')]) {
            refreshVenv()
            sh '''if [ -x ./ciscripts/run_isort.sh ] ; then
                      ./ciscripts/run_isort.sh
                  fi
               '''
            verifyresult.put('isort', 1)
        }
    }
    catch (all) {
        verifyresult.put('isort',-1)
    }
    archiveArtifacts([allowEmptyArchive: true, artifacts: "isort_all.txt"])
    // echo "isort: result=" + verifyresult['isort']
    publishGerrit('isort', verifyresult['isort'])
    recordIssues([enabledForFailure: true,
                  ignoreQualityGate: true,
                  tools: [groovyScript(parserId: 'isort_diff',
                                       pattern: 'isort_*.txt',
                                       reportEncoding: 'UTF-8')],
                  unhealthy: 20,
                  healthy: 1,
                  ])

    if (verifyresult['isort'] < 0) {
        // currently only warn, but do not fail the job
        echo("Imports are incorrectly sorted")
        echo("To fix the isort errors run:")
        echo("git diff HEAD^ --name-only --diff-filter d '*.py' | xargs isort")
        // error('Failure in isort')
    }
}

def runSetupcheck() {
    verifyresult.put('sc', 0)
    publishGerrit('setupcheck', verifyresult['sc'])
    try {
        withCredentials([string(credentialsId: 'GERRITHTTP',
                                variable: 'GERRITHTTP')]) {
            refreshVenv()
            ansiColor('xterm') {
                sh './ciscripts/run_setupcheck.sh'
            }
            verifyresult.put('sc', 1)
        }
    }
    catch (all) {
        verifyresult.put('sc', -1)
    }
    echo "setupcheck: result=" + verifyresult['sc']
    publishGerrit('setupcheck',verifyresult['sc'])
    archiveArtifacts([allowEmptyArchive: true,
                      artifacts: 'setupcheck.log'])

    recordIssues([enabledForFailure: true,
                  ignoreQualityGate: true,
                  tools: [groovyScript(parserId: 'nicos-setup-check-syntax-error-ng',
                                       pattern: 'setupcheck.log',
                                       reportEncoding: 'UTF-8'),
                          groovyScript(parserId: 'nicos-setup-check-errors-file-ng',
                                       pattern: 'setupcheck.log',
                                       reportEncoding: 'UTF-8'),
                          groovyScript(parserId: 'nicos-setup-check-warnings-ng',
                                       pattern: 'setupcheck.log',
                                       reportEncoding: 'UTF-8'),
                                                                              ],
                  unhealthy: 2,
                  healthy: 1,
                  ])

    if (verifyresult['sc'] < 0) {
        error('Failure in setupcheck')
    }
}

def runTests(venv, pyver, withcov, checkpypiupdates=false, skipvenvupdate=false) {
    if (!skipvenvupdate) {
        refreshVenv('pytest', venv, checkpypiupdates)
    }
    writeFile file: 'pytest_ini.add', text: """
addopts = --tb=short
  --junit-xml=pytest-${pyver}.xml
  --junit-prefix=$pyver""" + (withcov ? """
  --cov
  --cov-config=.coveragerc
  --cov-report=html:cov-$pyver
  --cov-report=xml:cobertura-${pyver}.xml
  --cov-report=term

""" : "")
    sh """
     [ -f pytest.ini ] || echo "[pytest]" > pytest.ini
    cat pytest_ini.add >> pytest.ini"""


    verifyresult.put(pyver, 0)
    publishGerrit('pytest-'+pyver, verifyresult[pyver])
    try {
        timeout(14) {
            sh "./ciscripts/run_pytest.sh $venv"
            verifyresult.put(pyver, 1)
        } // timeout
    } catch(all) {
        verifyresult.put(pyver, -1)
    }

    echo "Test $pyver: result=" + verifyresult[pyver]
    publishGerrit('pytest-'+pyver, verifyresult[pyver])

    junit([allowEmptyResults: true,
           keepLongStdio: true,
           testResults: "pytest-${pyver}.xml"])
    archiveArtifacts([allowEmptyArchive: true,
                      artifacts: "pytest-${pyver}.xml"])
    if (withcov) {
        archiveArtifacts([allowEmptyArchive: true,
                          artifacts: "cobertura-${pyver}.xml"])
        publishHTML([allowMissing: true,
                     alwaysLinkToLastBuild: false,
                     keepAll: true,
                     reportDir: "cov-$pyver/",
                     reportFiles: 'index.html',
                     reportName: "Coverage ($pyver)"])
    }

    if (verifyresult[pyver] < 0) {
        error('Failure in test with ' + pyver)
    }
}

def runDocTest() {
    verifyresult.put('doc', 0)
    publishGerrit('doc', verifyresult['doc'])
    try {
        refreshVenv('','$NICOS3VENV')
        sh './ciscripts/run_doctest.sh'
        archiveArtifacts([allowEmptyArchive: true,
                          artifacts: 'doc/build/latex/NICOS.*'])
        publishHTML([allowMissing: true,
                     alwaysLinkToLastBuild: true,
                     keepAll: true,
                     reportDir: 'doc/build/html',
                     reportFiles: 'index.html',
                     reportName: 'Nicos Doc (test build)'])

        verifyresult.put('doc', 1)
    } catch (all) {
        verifyresult.put('doc',-1 )
    }
    echo "Docs: result=" + verifyresult['doc']
    publishGerrit('doc', verifyresult['doc'])

    if (verifyresult['doc'] < 0) {
        error('Failure in doc test')
    }
}

// ************* End Function defs ***/

// ************* Start main script ***/
timestamps {

node('dockerhost') {
    stage(name: 'checkout code: ' + GERRIT_PROJECT) {
        checkoutSource()
    }

    def buildimage_deb = null;
    def buildimage_debonly = null;
    def buildimage_rocky = null;

    stage('docker setup') {
        buildimage_deb = docker.image('docker.ictrl.frm2.tum.de:5443/jenkins/nicos-jenkins:bullseye')
        buildimage_deb.pull()

        buildimage_debonly = docker.image('docker.ictrl.frm2.tum.de:5443/jenkins/nicos-jenkins:bullseye-debonly')
        buildimage_debonly.pull()

        buildimage_rocky = docker.image('docker.ictrl.frm2.tum.de:5443/jenkins/nicos-jenkins:rockylinux9')
        buildimage_rocky.pull()
    }

    stage(name: 'prepare') {
        withCredentials([string(credentialsId: 'RMAPIKEY', variable: 'RMAPIKEY'),
                         string(credentialsId: 'RMSYSKEY', variable: 'RMSYSKEY')]) {
           buildimage_deb.inside(){
                sh  '''\
#!/bin/bash
export PYTHONIOENCODING=utf-8
~/tools2/bin/mlzrmupdater
'''
            } // image.inside
        } // credentials
    } // stage


try {
    parallel pylint: {
        stage(name: 'pylint') {
            ws {
                checkoutSource()
                buildimage_deb.inside('-v /home/git:/home/git') {
                    runPylint('py3')
                }
            } // ws
        } // stage
    }, isort: {
        stage(name: 'isort') {
            buildimage_deb.inside('-v /home/git:/home/git') {
                runIsort()
            }
        } // stage
    }, setup_check: {
        stage(name: 'Nicos Setup check') {
            buildimage_deb.inside('-v /home/git:/home/git') {
                timeout(5) {
                    runSetupcheck()
                }
            }
        } // stage
    }, test_rocky: {
        stage(name: 'Test on RockyLinux') {
            ws {
                checkoutSource()
                buildimage_rocky.inside('-v /home/git:/home/git') {
                    runTests('$NICOS3VENV', 'python3-rocky', false, true, true)
                } // image.inside
            } // ws
        } // stage
    }, test_debian: {
        stage(name: 'Tests on Debian') {
            ws {
                checkoutSource()
                buildimage_debonly.inside('-v /home/git:/home/git') {
                    runTests('$NICOS3VENV', 'python3-debonly', false, true, true)
                } // image.inside
            } // ws
        } // stage
    }, test_all: {
	stage(name: 'Tests on Debian, with all dependencies') {
            ws {
                checkoutSource()
                def kafkaversion="4.0.0"
                docker.image("docker.ictrl.frm2.tum.de:5443/jenkins/kafka:${kafkaversion}").withRun() { kafka ->
                    def influxdbversion = "0.0.2"
                    docker.image("docker.ictrl.frm2.tum.de:5443/jenkins/influxdb:${influxdbversion}").withRun() { influxdb ->
                        token = sh (
                           script: """
                               docker exec ${influxdb.id} sh -c \"influx config ls --json | jq -r '.default.token'\"
                           """,
                           returnStdout: true
                        ).trim()
                        buildimage_deb.inside("-v /home/git:/home/git -e KAFKA_URI=kafka:9092 -e INFLUXDB_URI=http://influxdb:8086 --link ${kafka.id}:kafka --link ${influxdb.id}:influxdb") {
                            sh """
                            . \$NICOS3VENV/bin/activate
                            ./bin/nicos-keystore add influxdb --storagepw nicos --password ${token}
                            """
                            runTests('$NICOS3VENV', 'python3', GERRIT_EVENT_TYPE == 'change-merged')
                        } // image.inside
                    } // influxdb.WithRun
                } // kafka.WithRun
            } // ws
        } // stage
    }, test_docs: {
        stage(name: 'Test docs') {
            docimage = docker.image('docker.ictrl.frm2.tum.de:5443/jenkins/nicos-jenkins:nicosdocs')
            docimage.pull()
            docimage.inside() {
                runDocTest()
            } // image.inside
        } // stage
    },
    failFast: false
} finally {
    // set final vote
    if (this.pipissues) {
        publishIssues(issues: this.pipissues,
                      ignoreFailedBuilds: false,
                      ignoreQualityGate: true)
    }
    setGerritReview()
} // finally
} // node
} // timestamps
