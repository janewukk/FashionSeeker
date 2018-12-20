import urllib
import json
import boto3
from botocore.vendored import requests
from urllib.parse import quote
from urllib.parse import urlencode


def lambda_handler(event, contest):
	# q="Michael Kors+js5316"
	q = event["q"]
	query= q.split("+")
	brand=query[0]
	user=query[1]

	# call google API to get the url and name of user input brand
	google_result = search_in_google(brand)
	print(google_result)
	if "ads" in google_result:
		url = google_result["ads"][0]["link"]
		name = google_result["ads"][0]["title"]
		print(url)
		insert_into_user(user, url)
		
		# use url as key to search in dynamodb
		# results: discounts & name
		results = search_in_db(url)
		if 'Item' not in results:
			response = get_discount(name, url)
			results = search_in_db(url)

	# google API returned empty url
	else:
		results = "Search input is not a valid brand."
		
	print(json.dumps({"results": results}, indent=2))
	return {
		'statusCode': 200,
		'body': json.dumps({"results": results}),
		'headers': {
			"x-custom-header": "my custom header value",
			"Access-Control-Allow-Origin": "*",
			"Access-Control-Allow-Methods": "POST,GET",
			"Access-Control-Allow-Headers": "x-api-key"
		}
	}


def search_in_db(url):
	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table('discount_table')
	results = table.get_item(
		Key={
			'url': url
		}
	)
	return results


def search_in_google(brand):
	params = {
		"playground": "false",
		"q": brand,
		"hl": "en",
		"gl": "us",
		"google_domain": "google.com",
		"api_key": "547e35e6ecfc2a13cd875dc18b5a4be020252c6bb8b93b68959ce3f226b9e508",
		# "api-key":"demo"
	}
	query = GoogleSearchResults(params)
	dic_result = query.get_dictionary()
	return dic_result

def get_discount(name, url):
	client = boto3.client('lambda')
	param = {
		"name": name,
		"url": url
	}
	response = client.invoke(
		FunctionName='getDiscount',
		InvocationType='RequestResponse',
		Payload=json.dumps(param)
	)
	return response

def insert_into_user(username, url):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('User')
    results = table.get_item(
        Key={
            'username': username
        }
    )
    array = [url]
    array = json.dumps(array)
    # if 'Item' not in results:
    table.put_item(
      Item={
            'username': username,
            'urls': array
        }
    )
    
    

# API Package
class GoogleSearchResults(object):
    VERSION = "1.0.0"
    BACKEND = "https://serpapi.com/search"
    SERP_API_KEY = None

    def __init__(self, params_dict):
        self.params_dict = params_dict

    def construct_url(self):
        self.params_dict['source'] = 'python'
        if self.SERP_API_KEY:
            self.params_dict['serp_api_key'] = self.SERP_API_KEY
        response = requests.get(self.BACKEND, self.params_dict)
        return response.text

    def get_results(self):
        try:
            self.construct_url()
        except requests.HTTPError as e:
            print(e, e.response.status_code)
        return self.construct_url()

    def get_html(self):
        return self.get_results()

    def get_json(self):
        self.params_dict["output"] = "json"
        return json.loads(self.get_results())

    def get_json_with_images(self):
        self.params_dict["output"] = "json_with_images"
        return json.loads(self.get_results())

    def get_dictionary(self):
        return dict(self.get_json())

    def get_dictionary_with_images(self):
        return dict(self.get_json_with_images())


# Output:
# {
#   "results": {
#     "Item": {
#       "url": "www.ae.com/American/Eagle",
#       "discount": "[\"50% Off Bras &amp; Bralettes\",\"TAKE AN ADDITIONAL 10% OFF YOUR PURCHASE WITH CODE: HOLLYJOLLY\",\"Want an extra 20% off? \",\"25% OFF ALL JEANS\",\"Get 15% off your first purchase\"]"
#     },
#     "ResponseMetadata": {
#       "RequestId": "SGORVTQVLQBD0LVJ3DPTLR3SFFVV4KQNSO5AEMVJF66Q9ASUAAJG",
#       "HTTPStatusCode": 200,
#       "HTTPHeaders": {
#         "server": "Server",
#         "date": "Thu, 20 Dec 2018 00:05:26 GMT",
#         "content-type": "application/x-amz-json-1.0",
#         "content-length": "257",
#         "connection": "keep-alive",
#         "x-amzn-requestid": "SGORVTQVLQBD0LVJ3DPTLR3SFFVV4KQNSO5AEMVJF66Q9ASUAAJG",
#         "x-amz-crc32": "1996094920"
#       },
#       "RetryAttempts": 0
#     }
#   }