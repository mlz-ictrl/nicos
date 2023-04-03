@Library('ecdc-pipeline')
import ecdcpipeline.ContainerBuildNode
import ecdcpipeline.PipelineBuilder

project = "nicos"

container_build_nodes = [
  'centos7-release': ContainerBuildNode.getDefaultContainerBuildNode('centos7-gcc11')
]


// Define number of old builds to keep.
num_artifacts_to_keep = '1'


// Set number of old builds to keep.
properties([[
  $class: 'BuildDiscarderProperty',
  strategy: [
    $class: 'LogRotator',
    artifactDaysToKeepStr: '',
    artifactNumToKeepStr: num_artifacts_to_keep,
    daysToKeepStr: '',
    numToKeepStr: ''
  ]
]]);


pipeline_builder = new PipelineBuilder(this, container_build_nodes)
pipeline_builder.activateEmailFailureNotifications()

builders = pipeline_builder.createBuilders { container ->
  pipeline_builder.stage("${container.key}: Checkout") {
    dir(pipeline_builder.project) {
      scm_vars = checkout scm
    }
    container.copyTo(pipeline_builder.project, pipeline_builder.project)
  }  // stage

  pipeline_builder.stage("${container.key}: Dependencies") {
    def conan_remote = "ess-dmsc-local"
    // Install test related stuff separately as we don't need all the other dev stuff
    // Also need to install some dependencies relating to other facilities.
    container.sh """
      which python
      python -m venv venv
      . venv/bin/activate
      pip install pip install --upgrade pip
      python --version
      python -m pip install -r ${project}/nicos_ess/requirements.txt
      python -m pip install pytest pytest-timeout mock lxml Pillow
    """
  } // stage

  pipeline_builder.stage("${container.key}: Test") {
    def test_output = "TestResults.xml"
    container.sh """
      . venv/bin/activate
      cd ${project}/test
      python -m pytest --junitxml=${test_output} --ignore=nicos_sinq
    """
    container.copyFrom("${project}/test/${test_output}", ".")
    xunit thresholds: [failed(unstableThreshold: '0')], tools: [JUnit(deleteOutputFiles: true, pattern: '*.xml', skipNoTestFiles: false, stopProcessingIfError: false)]
  } // stage

}  // createBuilders

node {
  dir("${project}") {
    scm_vars = checkout scm
  }

  try {
    parallel builders
  } catch (e) {
    throw e
  }

  // Delete workspace when build is done
  cleanWs()
}
