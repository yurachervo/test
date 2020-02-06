pipeline {
    agent { label 'windows' }
    stages {
        stage('first'){
            steps{
                echo "$JOB_NAME"
                echo "$JENKINS_URL"
                echo "${currentBuild.number}"
                echo "${JOB_URL}"
                sh "echo ${JOB_URL} , ${currentBuild.number} >> fileName.txt"
                }
        }
        stage('second'){
            environment {
                //HEX_FILE = file'*.komplett.*.hex'
                ffiles = findFiles(glob: '*Na*.txt')
               // hex_file = files[0]
            }
            steps{
                script{
                try {
                    
                        script{
                             // fileOperations([fileCopyOperation(excludes: '', flattenFiles: true, includes: '*.hex', targetLocation: "${WORKSPACE}/111")])
                            def files = findFiles(glob: '111/*komplett*.hex')
                            //echo "${files}"
                            hex_file = files[0]
                            echo "${hex_file}"
                         
                        }
                        fileOperations([fileRenameOperation(source: "${hex_file}", destination: '111/family.hex')])
                        //echo "${env.HEX_FILE}"
                        echo "${hex_file}"
                }
                
                catch(err) {
                echo "hex file not found"
                }
            }
                }
            }
        }
    }
