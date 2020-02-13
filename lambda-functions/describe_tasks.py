import boto3, datetime, time, logging, os, operator
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from json import loads 
from operator import itemgetter

ecs_client = boto3.client('ecs')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

now = datetime.datetime.now()
now_minus_three = now - datetime.timedelta(minutes = 3)

def describe_services(cluster_name, services):
    response = ecs_client.describe_services(
        cluster = cluster_name,
        services = services)
    return response

def list_tasks(cluster_name, service):
    response = ecs_client.list_tasks(
        cluster = cluster_name,
        serviceName = service,
        desiredStatus = 'STOPPED'
    )
    return response

def describe_tasks(cluster_name, tasks):
    responses = ecs_client.describe_tasks(
        cluster = cluster_name,
        tasks=tasks
        ).get('tasks')
    sorted_responses = []
    for r in responses:
        if 'stoppedAt' in r:
            sorted_responses.append(r)
    sorted_responses.sort(key=lambda d: d['stoppedAt'])
    logger.info("RESPONSE-1" + str(sorted_responses[-1]))
    logger.info("RESPONSE-2" + str(sorted_responses[-2]))
    if sorted_responses and len(sorted_responses) >= 2 and sorted_responses[-2]['stoppedAt'].replace(tzinfo=None) > now_minus_three.replace(tzinfo=None):
        return {'TaskArn': sorted_responses[-1]['taskArn'], 'StoppedAt': sorted_responses[-1]['stoppedAt'], 'StoppedReason': sorted_responses[-1]['stoppedReason'] }, {'TaskArn': sorted_responses[-2]['taskArn'], 'StoppedAt': sorted_responses[-2]['stoppedAt'], 'StoppedReason': sorted_responses[-2]['stoppedReason'] }
    else:
        return None, None

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
def append_message(message, task1, task2, cluster, service):
    message += "<br />Cluster Name: " + cluster
    message += "<br />Service Name: " + service 
    message += "<br />Task Arn: " + task1['TaskArn']
    message += "<br />Stopped At: " + str(task1['StoppedAt'])
    message += "<br />Stopped Reason:" + str(task1['StoppedReason'])
    message += "<br />Task Arn: " + task2['TaskArn']
    message += "<br />Stopped At: " + str(task2['StoppedAt'])
    message += "<br />Stopped Reason:" + str(task2['StoppedReason'])
    return message
    

def lambda_handler(event, context):
    environment = os.environ['EnvName']
    receipientAddresses = os.environ['ReceipientAddresses'].split(',')    
    sender = os.environ['Sender']
    send_email = False
    subject = os.environ['MailSubject']
    title = str(subject) + ' [' + str(environment) + ']'
    text = ""
    message = "The following tasks have been updated within the past 3 minutes.<br />"
    info = os.environ['Info']
    info = info.replace("'", "\"")
    info_json = loads(info)
    cluster_lists=(info_json["clusters"])
    
    for cluster_list in cluster_lists:
        cluster=cluster_list.get('cluster_name')
        services = cluster_list.get('service_names')
        for service in services:
            tasks = list_tasks(cluster, service).get('taskArns')
            logger.info("List of tasks for service :" + service + "\n" + str(tasks))
            if tasks:
                task1, task2 = describe_tasks(cluster, tasks)
                logger.info(service + "-Task1: " + str(task1))
                logger.info(service + "-Task2: " + str(task2))
                if task1 != None and task2 != None:
                    send_email = True
                    message = append_message(message, task1, task2, cluster, service)
    if send_email:
        mail_response = sendEmail(sender, receipientAddresses, title, text, message, None)
        logger.info("Mail successfully sent.\n" + str(mail_response))
