import boto3, os, datetime, sys, logging

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def filter_users(IAM, user_name, start_time, end_time, exclude_list):
    keydetails=IAM.list_access_keys(UserName=user_name)
    key_data = []
    # Some user may have 2 access keys. So iterating over them and listing the details of active access key.
    for keys in keydetails['AccessKeyMetadata']:
        last_used = IAM.get_access_key_last_used(AccessKeyId=keys['AccessKeyId'])
        if last_used['AccessKeyLastUsed']['ServiceName'] == "N/A" :
            if (time_diff(keys['CreateDate'])) >= start_time and (time_diff(keys['CreateDate'])) <= end_time and keys['Status'] == "Inactive":
                user = {}
                user['name'] = keys['UserName']
                user['status'] = keys['Status']
                user['key'] = keys['AccessKeyId']
                user['key_age'] = time_diff(keys['CreateDate'])
                if user['name'] not in exclude_list:
                    key_data.append(user)
        else:
            if(time_diff(last_used['AccessKeyLastUsed']['LastUsedDate'])) >= start_time and keys['Status'] == "Inactive":
                user = {}
                user['name'] = keys['UserName']
                user['status'] = keys['Status']
                user['key'] = keys['AccessKeyId']
                user['key_age'] = time_diff(keys['CreateDate'])
                if user['name'] not in exclude_list:
                    key_data.append(user)
    return key_data

def get_filtered_user(user_details, IAM, expiration, exclude_list, warning):
    delete_users = []
    warn_users = []

    for user in user_details['Users']:
        keyData = []
        keyData = filter_users(IAM, user['UserName'], expiration, sys.maxsize, exclude_list)

        if len(keyData) > 0:
            delete_users += keyData

        keyData = filter_users(IAM, user['UserName'], warning, expiration - 1, exclude_list)

        if len(keyData) > 0:
            warn_users += keyData

    return (delete_users, warn_users)

def time_diff(keycreatedtime):
    # Getting the current time in utc format
    now = datetime.datetime.now(datetime.timezone.utc)
    # Calculating diff between two datetime objects.
    diff = now - keycreatedtime
    # Returning the difference in days
    return diff.days

def create_multipart_message(
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
    multipart_content_subtype = 'alternative' if text and html else 'mixed'
    msg = MIMEMultipart(multipart_content_subtype)
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

def send_mail(
        sender: str, recipients: list, title: str, text: str=None, html: str=None, attachments: list=None) -> dict:
    msg = create_multipart_message(sender, recipients, title, text, html, attachments)
    ses_client = boto3.client('ses') 
    return ses_client.send_raw_email(
        Source=sender,
        Destinations=recipients,
        RawMessage={'Data': msg.as_string()}
        ) 

def list_addresses():
    ses_client = boto3.client('ses')
    response = ses_client.list_identities(
        IdentityType = 'EmailAddress',
        MaxItems=100
        )
    return response

def delete_access_key(IAM, name, key):
    response = IAM.delete_access_key(
                    UserName=name,
                    AccessKeyId=key
    )
    return response

def create_access_key(IAM, name):
    response = IAM.create_access_key(
                    UserName=name
    )
    return response

def print_key_info(name, id, secret):
    print("\nCreated Keys for User: " + name)                
    print("AccessKey: " + id)
    print("SecretAccessKey: " + secret)

def append_to_delete_message(message, expiration,deletion, today):

    if deletion == "True":
        message += 'As per our key rotation policy, the following keys were non-compliant and were deleted on ' + today + '.<br>'
    else:
        message += 'As per our key rotation policy, the following keys are non-compliant. <br>'

    message += 'MAX KEY AGE: <b>' + str(expiration) + '</b> days'
    message += '<p><strong>Report:</strong></p>'
    message += '<table border="1" style="border-collapse: collapse; width: 40%;font-family:Calibri;">'

    message += '<tbody>'
    message += '<tr style="background-color:silver;font-family:Calibri;">'
    message += '<td style="text-align: center; width: 2%;font-family:Calibri;"><strong>No.</strong></td>'
    message += '<td style="text-align: center; width: 70%;font-family:Calibri;"><strong>User Name</strong></td>'
    message += '<td style="text-align: center; width: 26%;font-family:Calibri;"><strong>User Key</strong></td>'
    message += '<td style="text-align: center; width: 2%;font-family:Calibri;"><strong>Key Age</strong></td>'
    message += '</tr>'
    return message

def append_to_delete_table(message, user, i):
    message += '<tr style="font-family:Calibri;">'
    message += '<td style="background-color: rgb(255,69,0); text-align: center; width: 2%;font-family:Calibri;">' + str(i) +  '</td>'
    message += '<td style="background-color: rgb(205,92,92); text-align: center; width: 70%;font-family:Calibri;">' + user['name'] +  '</td>'
    message += '<td style="text-align: center; width: 26%;font-family:Calibri;">' + user['key'] + '</td>'
    message += '<td style="text-align: center; width: 2%;font-family:Calibri;">' + str(user['key_age']) + '</td>'
    message += '</tr>'
    return message

def append_to_warn_message(message):
    message += 'As per our key rotation policy, the following keys are about to expire in given amount of days. <br>'
    message += '<body style="font-family:Calibri;">'
    message += '<p><strong>Warning for AWS Access Keys to be deleted:</strong></p>'
    message += '<table border="1" style="border-collapse: collapse; width: 40%;font-family:Calibri;">'
    message += '<tbody>'
    message += '<tr style="background-color:silver;font-family:Calibri;">'
    message += '<td style="text-align: center; width: 2%;font-family:Calibri;"><strong>No.</strong></td>'
    message += '<td style="text-align: center; width: 70%;font-family:Calibri;"><strong>User Name</strong></td>'
    message += '<td style="text-align: center; width: 26%;font-family:Calibri;"><strong>Warning Key</strong></td>'
    message += '<td style="text-align: center; width: 2%;font-family:Calibri;"><strong>Days Left</strong></td>'
    message += '</tr>'
    return message

def append_to_warn_table(message, user, i, expiration):
    message += '<tr style="font-family:Calibri;">'
    message += '<td style="background-color: rgb(255,228,181); text-align: center; width: 2%;font-family:Calibri;">' + str(i) +  '</td>'
    message += '<td style="background-color: rgb(255,255,224); text-align: center; width: 70%;font-family:Calibri;">' + user['name'] +  '</td>'
    message += '<td style="text-align: center; width: 26%;font-family:Calibri;">' + user['key'] + '</td>'
    message += '<td style="text-align: center; width: 2%;font-family:Calibri;">' + str(expiration-user['key_age']) + '</td>'
    message += '</tr>'
    return message

def append_excluded_users(message, exclude_list):
    if len(exclude_list) != 0:
        i = 1
        message += 'Hi! <br>The following users are excluded from our key rotation policy. <br>'
        for name in exclude_list:
            message += str(i) + '. ' + name + '<br>'
            i += 1
        message += '<br>'
    return message

def lambda_handler(event, context):
    IAM = boto3.client('iam')
    message = '<body style="font-family:Calibri;">' + ' <br>'

    exclude_list = os.environ['exclude_list'].replace(" ", "") #comma delimited string of users
    exclude_list = exclude_list.split(',')    
    deletion = os.environ['deletion'] #true/false    
    expiration = int(os.environ['expiration']) #kb del krni hai
    warning_period = int(os.environ['warning_period'])#2 days
    warning = int(expiration) - warning_period
    receipient_addresses = os.environ['receipient_addresses'].split(',')  #comma delimited string of emails  
    sender = os.environ['sender'] #sender email address

    today = datetime.datetime.today().strftime('%m/%d/%Y')
    title = 'Access Keys Information'
    text = ""

    message += append_excluded_users(message, exclude_list)
    attachments = None

    user_details = IAM.list_users(MaxItems=300)
    delete_users = []
    warn_users = []

    filteredData = get_filtered_user(user_details, IAM, expiration, exclude_list, warning)
    delete_users = filteredData[0]
    warn_users = filteredData[1]

    if len(warn_users) == 0 and len(delete_users) == 0:
        print("All access keys compliant to the rotation policy.")

    if len(delete_users) > 0:
        message = append_to_delete_message(message, expiration,deletion,today)

        i = 1
        if deletion != "True":
            title = 'Access Keys Information'        
        for user in delete_users:
            message = append_to_delete_table(message, user, i)
            i += 1
            if deletion == "True":
                # Deleting Non compliant keys
                delete_access_key(IAM, user['name'], user['key'])

        message += '</tr>'
        message += '</table>'
        message += '<br>'

    if len(warn_users) > 0:
        title = 'Access Keys Information'        
        message = append_to_warn_message(message)
        i = 1

        for user in warn_users:
            message = append_to_warn_table(message, user, i, expiration)
            i += 1

        message += '</tr>'
        message += '</tbody>'
        message += '</table>'
        message += '<br>'

    if len(delete_users) > 0 or len(warn_users) > 0:
        # Sending email
        mail_response = send_mail(sender, receipient_addresses, title, text, message, attachments)
        print(mail_response)

        