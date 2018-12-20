import json
import boto3

def lambda_handler(event, context):
    print(event)
    name = event["name"]
    url = event["url"]

    client = boto3.client('lambda')
    response = client.invoke (
        FunctionName = 'testing',
        InvocationType = 'RequestResponse',
        Payload = json.dumps(url)
    )
    
    output = response['Payload'].read().decode("utf-8") 
    output = json.loads(output)
    
    # print(output["body"])

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('discount_table')
    table.put_item(
      Item={
            'name': name,
            'url': url,
            'discount': output["body"]
        }
    )
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('discount_table')
    results = table.get_item(
        Key={
        'url': url
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }
