echo "Exporting variables"
# Provide exacct branch name
case $CIRCLE_BRANCH in
    "circleci-project-setup")
        export StackName=${StackNameStage}
        export EnvName=${EnvNameStage}
        export S3Bucket=${S3BucketStage}
        export S3KeyFilterLogs=${S3KeyFilterLogsStage}
        export LambdaTriggerFilterLogs=${LambdaTriggerFilterLogsStage}
        export LambdaHandlerFilterLogs=${LambdaHandlerFilterLogsStage}
        export LogDurationFilterLogs=${LogDurationFilterLogsStage}
        export SearchJsonFilterLogs=${SearchJsonFilterLogsStage}
        export ReceipientAddressesFilterLogs=${ReceipientAddressesFilterLogsStage}
        export SenderFilterLogs=${SenderFilterLogsStage}
        export CronExpFilterLogs=${CronExpFilterLogsStage}
        export MailSubjectFilterLogs=${MailSubjectFilterLogsStage}
        export S3KeyDynamoDB=${S3KeyDynamoDBStage}
        export LambdaTriggerDynamoDB=${LambdaTriggerDynamoDBStage}
        export LambdaHandlerDynamoDB=${LambdaHandlerDynamoDBStage}
        export MaxBackupsDynamoDB=${MaxBackupsDynamoDBStage}
        export TableNamesDynamoDB=${TableNamesDynamoDBStage}
        export CronExpDynamoDB=${CronExpDynamoDBStage}
        export S3KeyDescribeTasks=${S3KeyDescribeTasksStage}
        export LambdaTriggerDescribeTasks=${LambdaTriggerDescribeTasksStage}
        export NumberOfMinutes=${NumberOfMinutesStage}
        export LambdaHandlerDescribeTasks=${LambdaHandlerDescribeTasksStage}
        export ClusterInfo=${ClusterInfoStage}
        export ClusterArn=${ClusterArnStage}
        export SenderDescribeTasks=${SenderDescribeTasksStage}
        export ReceipientAddressesDescribeTasks=${ReceipientAddressesDescribeTasksStage} 
        export MailSubjectDescribeTasks=${MailSubjectDescribeTasksStage}

        export WarningPeriod=${WarningPeriodStage}
        export ExpirationDays=${ExpirationDaysStage}
        export ExcludeList=${ExcludeListStage}
        export Deletion=${DeletionStage}
        export ReceipientEmailsKeyRotation=${ReceipientEmailsKeyRotationStage}
        export SenderEmailKeyRotation=${SenderEmailKeyRotationStage}
        export CronExpKeyRotation=${CronExpKeyRotationStage}
        export WarningPeriodInactive=$WarningPeriodInactiveStage
        export ExpirationDaysInactive=$ExpirationDaysInactiveStage
        export ExcludeListInactive=$ExcludeListInactiveStage
        export DeletionInactive=$DeletionInactiveStage
        export ReceipientEmailsKeyRotationInactive=$ReceipientEmailsKeyRotationInactiveStage
        export SenderEmailKeyRotationInactive=$SenderEmailKeyRotationInactiveStage
        export CronExpKeyRotationInactive=$CronExpKeyRotationInactiveStage
        ;;
        
    "master")
        export StackName=${StackNameProd}
        export EnvName=${EnvNameProd}
        export S3Bucket=${S3BucketProd}
        export S3KeyFilterLogs=${S3KeyFilterLogsProd}
        export LambdaTriggerFilterLogs=${LambdaTriggerFilterLogsProd}
        export LambdaHandlerFilterLogs=${LambdaHandlerFilterLogsProd}
        export LogDurationFilterLogs=${LogDurationFilterLogsProd}
        export SearchJsonFilterLogs=${SearchJsonFilterLogsProd}
        export ReceipientAddressesFilterLogs=${ReceipientAddressesFilterLogsProd}
        export SenderFilterLogs=${SenderFilterLogsProd}
        export CronExpFilterLogs=${CronExpFilterLogsProd}
        export MailSubjectFilterLogs=${MailSubjectFilterLogsProd}
        export S3KeyDynamoDB=${S3KeyDynamoDBProd}
        export LambdaTriggerDynamoDB=${LambdaTriggerDynamoDBProd}
        export LambdaHandlerDynamoDB=${LambdaHandlerDynamoDBProd}
        export MaxBackupsDynamoDB=${MaxBackupsDynamoDBProd}
        export TableNamesDynamoDB=${TableNamesDynamoDBProd}
        export CronExpDynamoDB=${CronExpDynamoDBProd}
        export S3KeyDescribeTasks=${S3KeyDescribeTasksProd}
        export LambdaTriggerDescribeTasks=${LambdaTriggerDescribeTasksProd}
        export LambdaHandlerDescribeTasks=${LambdaHandlerDescribeTasksProd}
        export NumberOfMinutes=${NumberOfMinutesProd}
        export ClusterInfo=${ClusterInfoProd}
        export ClusterArn=${ClusterArnProd}
        export SenderDescribeTasks=${SenderDescribeTasksProd}
        export ReceipientAddressesDescribeTasks=${ReceipientAddressesDescribeTasksProd} 
        export MailSubjectDescribeTasks=${MailSubjectDescribeTasksProd}

        export WarningPeriod=${WarningPeriodProd}
        export ExpirationDays=${ExpirationDaysProd}
        export ExcludeList=${ExcludeListProd}
        export Deletion=${DeletionProd}
        export ReceipientEmailsKeyRotation=${ReceipientEmailsKeyRotationProd}
        export SenderEmailKeyRotation=${ReceipientEmailsKeyRotationProd}
        export CronExpKeyRotation=${ReceipientEmailsKeyRotationProd}
        export WarningPeriodInactive=$WarningPeriodInactiveProd
        export ExpirationDaysInactive=$ExpirationDaysInactiveProd
        export ExcludeListInactive=$ExcludeListInactiveProd
        export DeletionInactive=$DeletionInactiveProd
        export ReceipientEmailsKeyRotationInactive=$ReceipientEmailsKeyRotationInactiveProd
        export SenderEmailKeyRotationInactive=$SenderEmailKeyRotationInactiveProd
        export CronExpKeyRotationInactive=$CronExpKeyRotationInactiveProd
        ;;
esac

echo "Remove previously existing zip"
rm -rf *.py.zip

echo "Zipping code for filter logs"
mv ./lambda-functions/filter_logs.py ./filter_logs-$CIRCLE_BUILD_NUM.py
zip filter_logs-$CIRCLE_BUILD_NUM.py.zip filter_logs-$CIRCLE_BUILD_NUM.py

echo "Zipping code for dynamodb backups"
mv ./lambda-functions/dynamodb_backups.py ./dynamodb_backups-$CIRCLE_BUILD_NUM.py
zip dynamodb_backups-$CIRCLE_BUILD_NUM.py.zip dynamodb_backups-$CIRCLE_BUILD_NUM.py

echo "Zipping code for ecs describe tasks"
mv ./lambda-functions/describe_tasks.py ./describe_tasks-$CIRCLE_BUILD_NUM.py
zip describe_tasks-$CIRCLE_BUILD_NUM.py.zip describe_tasks-$CIRCLE_BUILD_NUM.py

echo "Zipping code for key rotation"
mv ./lambda-functions/key_rotation_lambda.py ./key_rotation_lambda-$CIRCLE_BUILD_NUM.py
zip key_rotation_lambda-$CIRCLE_BUILD_NUM.py.zip key_rotation_lambda-$CIRCLE_BUILD_NUM.py

echo "Zipping code for inactive key rotation"
mv ./lambda-functions/inactive_key_rotation_lambda.py ./inactive_key_rotation_lambda-$CIRCLE_BUILD_NUM.py
zip inactive_key_rotation_lambda-$CIRCLE_BUILD_NUM.py.zip inactive_key_rotation_lambda-$CIRCLE_BUILD_NUM.py

echo "Deploying to S3"
aws s3 cp "cfn-deployment.yaml" s3://$S3Bucket
aws s3 cp "cfn-rule.yaml" s3://$S3Bucket
aws s3 cp "filter_logs-$CIRCLE_BUILD_NUM.py.zip" s3://$S3Bucket
aws s3 cp "dynamodb_backups-$CIRCLE_BUILD_NUM.py.zip" s3://$S3Bucket
aws s3 cp "describe_tasks-$CIRCLE_BUILD_NUM.py.zip" s3://$S3Bucket
aws s3 cp "key_rotation_lambda-$CIRCLE_BUILD_NUM.py.zip" s3://$S3Bucket
aws s3 cp "inactive_key_rotation_lambda-$CIRCLE_BUILD_NUM.py.zip" s3://$S3Bucket

echo $LogDurationFilterLogs

echo "Deploying Cloudformation script"
aws cloudformation deploy --template-file cfn-main.yaml \
--stack-name "$StackName" \
--parameter-overrides \
EnvName="${EnvName}" \
S3Bucket="$S3Bucket"  \
S3KeyFilterLogs="filter_logs-${CIRCLE_BUILD_NUM}.py.zip" \
LambdaTriggerFilterLogs="$LambdaTriggerFilterLogs" \
LambdaHandlerFilterLogs="filter_logs-$CIRCLE_BUILD_NUM.lambda_handler" \
LogDurationFilterLogs=$LogDurationFilterLogs \
SearchJsonFilterLogs="$SearchJsonFilterLogs" \
ReceipientAddressesFilterLogs="$ReceipientAddressesFilterLogs" \
SenderFilterLogs="$SenderFilterLogs" \
CronExpFilterLogs="$CronExpFilterLogs" \
MailSubjectFilterLogs="$MailSubjectFilterLogs" \
S3KeyDynamoDB="dynamodb_backups-${CIRCLE_BUILD_NUM}.py.zip" \
LambdaTriggerDynamoDB="$LambdaTriggerDynamoDB" \
LambdaHandlerDynamoDB="dynamodb_backups-$CIRCLE_BUILD_NUM.lambda_handler" \
MaxBackupsDynamoDB="$MaxBackupsDynamoDB" \
TableNamesDynamoDB="$TableNamesDynamoDB" \
CronExpDynamoDB="$CronExpDynamoDB" \
S3KeyDescribeTasks="describe_tasks-${CIRCLE_BUILD_NUM}.py.zip" \
LambdaTriggerDescribeTasks="$LambdaTriggerDescribeTasks" \
NumberOfMinutes="$NumberOfMinutes" \
LambdaHandlerDescribeTasks="describe_tasks-$CIRCLE_BUILD_NUM.lambda_handler" \
ClusterInfo="$ClusterInfo" \
ClusterArn="$ClusterArn" \
SenderDescribeTasks="$SenderDescribeTasks" \
ReceipientAddressesDescribeTasks="$ReceipientAddressesDescribeTasks" \
MailSubjectDescribeTasks="$MailSubjectDescribeTasks" \
S3KeyKeyRotation="key_rotation_lambda-${CIRCLE_BUILD_NUM}.py.zip" \
LambdaTriggerKeyRotation="$LambdaTriggerKeyRotation" \
LambdaHandlerKeyRotation="key_rotation_lambda-$CIRCLE_BUILD_NUM.lambda_handler" \
WarningPeriod="$WarningPeriod" \
ExpirationDays="$ExpirationDays" \
ExcludeList="$ExcludeList" \
Deletion="$Deletion" \
ReceipientEmailsKeyRotation="$ReceipientEmailsKeyRotation" \
SenderEmailKeyRotation="$SenderEmailKeyRotation" \
CronExpKeyRotation="$CronExpKeyRotation" \
S3KeyKeyRotationInactive="inactive_key_rotation_lambda-$CIRCLE_BUILD_NUM.py.zip" \
LambdaTriggerKeyRotationInactive="$LambdaTriggerKeyRotationInactive" \
LambdaHandlerKeyRotationInactive="inactive_key_rotation_lambda-${CIRCLE_BUILD_NUM}.lambda_handler" \
WarningPeriodInactive="$WarningPeriodInactive" \
ExpirationDaysInactive="$ExpirationDaysInactive" \
ExcludeListInactive="$ExcludeListInactive" \
DeletionInactive="$DeletionInactive" \
ReceipientEmailsKeyRotationInactive="$ReceipientEmailsKeyRotationInactive" \
SenderEmailKeyRotationInactive="$SenderEmailKeyRotationInactive" \
CronExpKeyRotationInactive="$CronExpKeyRotationInactive" \
--capabilities CAPABILITY_NAMED_IAM
