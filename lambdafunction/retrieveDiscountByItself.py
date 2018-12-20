import json
import boto3

def lambda_handler(event, context):
    # ----------------- connect to dynamo db -------------
    client = boto3.client('lambda')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('discount_table')
    
    # ----------- get all items --------
    response = table.scan()["Items"]
    
    # ----------------- crawl discount by testing lambda function ------------
    for item in response:
        url = item["url"]
        name = item["name"]
        response = client.invoke (
            FunctionName = 'testing',
            InvocationType = 'RequestResponse',
            Payload = json.dumps(url)
        )
        output = response['Payload'].read().decode("utf-8") 
        output = json.loads(output)
        # ------------------ update table --------------------
        table.put_item(
          Item={
                'name': name,
                'url': url,
                'discount': output["body"]
            }
        )

