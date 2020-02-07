@Library('ecdc-pipeline')
import ecdcpipeline.ContainerBuildNode
import ecdcpipeline.PipelineBuilder

project = "nicos"

python = "python3.6"

container_build_nodes = [
//  'centos7': ContainerBuildNode.getDefaultContainerBuildNode('centos7'),
  'centos7-release': ContainerBuildNode.getDefaultContainerBuildNode('centos7'),
//  'debian9': ContainerBuildNode.getDefaultContainerBuildNode('debian9'),
//  'ubuntu1804': ContainerBuildNode.getDefaultContainerBuildNode('ubuntu1804')
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
    numToKeepStr: num_artifacts_to_keep
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
    container.sh """
      pip install --user -r ${project}/requirements.txt
      pip install --user -r ${project}/requirements-dev.txt
      pip install --user -r ${project}/requirements-gui.txt
    """
  } // stage

  pipeline_builder.stage("${container.key}: Test") {
    def test_output = "TestResults.xml"
    container.sh """
      ${python} --version
      cd ${project}
      ${python} -m pytest --junitxml=${test_output}
    """
    container.copyFrom("${project}/${test_output}", ".")
    junit "${test_output}"

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
