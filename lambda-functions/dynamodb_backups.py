import datetime, boto3, logging, sys, os

logger = logging.getLogger()
logger.setLevel(logging.INFO)
dynamo = boto3.client('dynamodb')

def lambda_handler(event, context):
    if os.environ['dynamodb_backup_required'] == True:
        if os.environ['MAX_BACKUPS'] == None:
            raise Exception("Max number of tables not specified in environmental variable.")
        MAX_BACKUPS = os.environ['MAX_BACKUPS']
        if os.environ['TableNames'] == None:
            raise Exception("No table name specified in environmental variable.")
        table_names = os.environ['TableNames']
        table_names = table_names.split(",")

        for table_name in table_names:
            create_backup(table_name)
            delete_old_backups(table_name, MAX_BACKUPS)

def create_backup(table_name):    
    try:
        logger.info("Backing up table: {}".format(table_name))
        backup_name = table_name + '-' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        response = dynamo.create_backup(TableName=table_name, BackupName=backup_name)
        logger.info("Backup successful.\nResponse: {}\n".format(response))
    except Exception as e:
        logger.error("Exception: {}".format(e), exc_info=sys.exc_info())

def delete_old_backups(table_name, MAX_BACKUPS):
    try:
        logger.info("Deleting old backups for table: {}".format(table_name))
        backups = dynamo.list_backups(TableName=table_name)
        backup_count = len(backups['BackupSummaries'])
        logger.info('Total backup count: {}'.format(backup_count))

        if backup_count <= MAX_BACKUPS:
            logger.info("No stale backups. Exiting.")
            return

        sorted_list = sorted(backups['BackupSummaries'], key=lambda k: k['BackupCreationDateTime'])

        old_backups = sorted_list[:MAX_BACKUPS]

        for backup in old_backups:
            arn = backup['BackupArn']
            logger.info("ARN of Backup to delete: " + arn)
            deleted_arn = dynamo.delete_backup(BackupArn=arn)
            status = deleted_arn['BackupDescription']['BackupDetails']['BackupStatus']
            logger.info("Status: {}".format(status))
    except Exception as e:
        logger.error("Exception: {}".format(e), exc_info=sys.exc_info())
    return