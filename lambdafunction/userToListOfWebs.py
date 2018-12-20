import json
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # TODO implement
    # new user if not exits
    # {
    #     "queryStringParameters": {
    #       "q": "pet"
    #      }
    # }
    # print("event: ",event)
    username=event["queryStringParameters"]["q"]
    mode = event["queryStringParameters"]["mode"]
    if mode == '2':
        send_one(username)
        return {
            'statusCode': 200,
            'body': json.dumps({"results": "email sent"}),
            'headers': {
                "Content-Type" : "application/json",
                "Access-Control-Allow-Origin" : "*",
                "Allow" : "GET, OPTIONS, POST",
                "Access-Control-Allow-Methods" : "GET, OPTIONS, POST",
                "Access-Control-Allow-Headers" : "*"
    		}
        }
    print(username)
    # username = event["username"]
    dynamodb = boto3.resource('dynamodb')
    userTable = dynamodb.Table('User')
    discountTable = dynamodb.Table('discount_table')
    urls = userTable.get_item(
        Key={
            'username': username
        }
    )
    # print(json.dumps(urls))
    webToDiscounts = {}
    if 'Item' not in urls:
        userTable.put_item(
          Item={
                'username': username,
                'urls': "[]"
            }
        )
    else:
        urls = urls['Item']['urls']
        urls = json.loads(urls)
        print("cur list urls: ", urls)
        for url in urls:
            infos = discountTable.get_item(
                Key={
                    'url': url
                }
            )
            infos = infos['Item']
            cur_list = [infos['url']] + json.loads(infos['discount'])
            webToDiscounts[infos['name']] = cur_list
    return {
        'statusCode': 200,
        'body': json.dumps({"results": webToDiscounts}),
        'headers': {
# 			"x-custom-header": "my custom header value",
# 			"Access-Control-Allow-Origin": "*",
# 			"Access-Control-Allow-Methods": "POST,GET",
# 			"Access-Control-Allow-Headers": "*",
            "Content-Type" : "application/json",
            "Access-Control-Allow-Origin" : "*",
            "Allow" : "GET, OPTIONS, POST",
            "Access-Control-Allow-Methods" : "GET, OPTIONS, POST",
            "Access-Control-Allow-Headers" : "*"
		}
    }

def send_one(RECIPIENT):
    # The HTML body of the email.
    BODY_HTML = """<html>
    <h2>The discount of your favorite sites:</h2>
    <body>
                """
    username = RECIPIENT
    dynamodb = boto3.resource('dynamodb')
    userTable = dynamodb.Table('User')
    discountTable = dynamodb.Table('discount_table')
    urls = userTable.get_item(
        Key={
            'username': username
        }
    )
    if 'Item' not in urls:
        return
    urls = urls['Item']['urls']
    urls = json.loads(urls)
    for url in urls:
        infos = discountTable.get_item(
            Key={
                'url': url
            }
        )
        infos = infos['Item']
        cur_discount = json.loads(infos['discount'])
        BODY_HTML = BODY_HTML + "<h2>" + infos['name'] + "</h2>"
        for cur in cur_discount:
            BODY_HTML = BODY_HTML + "<p>" + cur + "</p>"
        BODY_HTML = BODY_HTML + "<br>"
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = "FashionSeekerTeam <bt2484@columbia.edu>"
    # Replace recipient@example.com with a "To" address. If your account 
    # is still in the sandbox, this address must be verified.
    # RECIPIENT = "bt2484@columbia.edu"
    
    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the 
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    # CONFIGURATION_SET = "ConfigSet"
    
    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-east-1"
    
    # The subject line for the email.
    SUBJECT = "Your discount info"
    
    # The email body for recipients with non-HTML email clients.
    # txt = json.dumps(webToDiscounts)
    BODY_HTML = BODY_HTML + "</body></html>"

    # The character encoding for the email.
    CHARSET = "UTF-8"
    
    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION)
    
    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    }
                    # 'Text': {
                    #     'Charset': CHARSET,
                    #     'Data': BODY_TEXT,
                    # }
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])