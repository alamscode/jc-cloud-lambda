import boto3, datetime, os, logging, pprint, sys
from json import loads 

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def validateLogGroups(logsClient, logsToSearch):
    if len(logsToSearch) > 0:
        groupnames = []
        paginator = logsClient.get_paginator('describe_log_groups')
        responseIterator = paginator.paginate()

        for response in responseIterator:
            response = response["logGroups"]
            for logGroup in response:
                if logGroup['logGroupName'] in logsToSearch: groupnames.append(logGroup['logGroupName'])

        return groupnames
    else:
        return []

def createQuery(searchList):
    query = 'filter '
    for item in searchList:
        query += "@message like '" + item + "'"
        if item != searchList[-1]:
            query += ' or '
    return query.strip()

def queryLogStream(logsClient, logGroupName, startTime, endTime, query):
    endWaiting = ['Complete','Failed','Cancelled']
    startQueryResponse = logsClient.start_query(
        logGroupName=logGroupName,
        startTime=startTime,
        endTime=endTime,
        queryString = query)
    id  = startQueryResponse['queryId']
    queryStatus = 'Waiting' 
    while queryStatus == 'Waiting':
        getQueryResultResponse = logsClient.get_query_results(
            queryId=id
        )
        if getQueryResultResponse['status'] in endWaiting:
            queryStatus = 'End Waiting'
    return getQueryResultResponse

def createMultipartMessage(
        sender: str, recipients: list, title: str, text: str=None, html: str=None, attachments: list=None)\
        -> MIMEMultipart:
    """
    Creates a MIME multipart message object.
    Uses only the Python `email` standard library.
    Emails, both sender and recipients, can be just the email string or have the format 'The Name <the_email@host.com>'.

    :param sender: The sender.
    :param recipients: List of recipients. Needs to be a list, even if only one recipient.
    :param title: The title of the email.
    :param text: The text version of the email body (optional).
    :param html: The html version of the email body (optional).
    :param attachments: List of files to attach in the email.
    :return: A `MIMEMultipart` to be used to send the email.
    """
    multipartContentSubtype = 'alternative' if text and html else 'mixed'
    msg = MIMEMultipart(multipartContentSubtype)
    msg['Subject'] = title
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    # Record the MIME types of both parts - text/plain and text/html.
    # According to RFC 2046, the last part of a multipart message, in this case the HTML message, is best and preferred.
    if text:
        part = MIMEText(text, 'plain')
        msg.attach(part)
    if html:
        part = MIMEText(html, 'html')
        msg.attach(part)

    # Add attachments
    for attachment in attachments or []:
        with open(attachment, 'rb') as f:
            part = MIMEApplication(f.read())
            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment))
            msg.attach(part)

    return msg

def sendEmail(sender: str, recipients: list, title: str, text: str=None, html: str=None, attachments: list=None) -> dict:
    msg = createMultipartMessage(sender, recipients, title, text, html, attachments)
    sesClient = boto3.client('ses') 
    return sesClient.send_raw_email(
        Source=sender,
        Destinations=recipients,
        RawMessage={'Data': msg.as_string()}
        ) 

def getLoggroups(logsDict):
    logGroups = []
    for logDict in logsDict:
        logGroups.append(logDict['groupname'])
    return logGroups
        
def lambda_handler(event, context):
    logger = logging.getLogger()
    logDuration = os.environ['LogDuration']
    
    runtimeRegion = os.environ['AWS_REGION']
    searchJson = os.environ['SearchJson']
    searchJson = searchJson.replace("'", "\"")
    logsJson = loads(searchJson)['groups']
    
    startTime = datetime.datetime.now() - datetime.timedelta(minutes=int(logDuration))
    startTime = int(startTime.timestamp() * 1000)
    endTime = datetime.datetime.now()
    endTime = int(endTime.timestamp() * 1000)       
    
    receipientAddresses = os.environ['ReceipientAddresses'].split(',')    
    sender = os.environ['Sender']
    environment = os.environ['EnvName']
    subject = os.environ['MailSubject']
    title = str(subject) + ' [' + str(environment) + ']'
    text = ""
    message = ""
    logsClient = boto3.client('logs', region_name=runtimeRegion)
    logGroups = getLoggroups(logsJson)
    logGroups = validateLogGroups(logsClient, logGroups)
    if len(logGroups) == 0:
        return (400, {'message': 'No valid log group found'})
    sendMail = False

    try:
        for logGroup in logsJson:
            searchList = logGroup['keywords']
            query = createQuery(searchList).strip() 
            response = queryLogStream(logsClient, logGroup['groupname'], startTime, endTime, query)
            stats = response['statistics']
            results= response['results']
            
            pprint.pprint('\nLOG-GROUP-NAME: ' + str(logGroup['groupname']) + '\n' + str(stats))
            if int(stats['recordsMatched']) > 0:
                message += '<br><br><h2>Log Group Name: ' + logGroup['groupname'] + '<br>' + 'Matching Terms Found: ' + str(int(stats['recordsMatched'])) + '</h2><br><br>'
                for result in results:
                    message += "------------- <br>"
                    for res in result:
                        message += 'Field: ' + str(res['field']) + '<br>' + 'Value: ' + str(res['value']) + '<br>'
                    message += "------------- <br>"
                    
                sendMail = True
                
        if sendMail:
            mailResponse = sendEmail(sender, receipientAddresses, title, text, message, None)
            print("Mail successfully sent." + '\n' + str(mailResponse))
    except Exception as e:
        logger.error("Exception: {}".format(e),  exc_info=sys.exc_info())
        return {
        "status": 500
        }
        
    return {
        "status": 200
    }
