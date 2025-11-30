import json
import boto3
import uuid
from decimal import Decimal

# Initialize DynamoDB clients
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Inventory')
#Grady Mooney matt

def lambda_handler(event, context):
    """
    Add a new inventory item to the DynamoDB table
    """
    try:
        # Parse the request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})

        # Validate required fields
        required_fields = ['name', 'description', 'qty', 'price', 'location_id']
        missing_fields = [field for field in required_fields if field not in body]

        if missing_fields:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Missing required fields',
                    'missing_fields': missing_fields
                })
            }

        # Generate a unique ID using UUID (instead of ULID)
        item_id = str(uuid.uuid4())

        # Create the item object
        item = {
            'id': item_id,
            'name': body['name'],
            'description': body['description'],
            'qty': int(body['qty']),
            'price': Decimal(str(body['price'])),
            'location_id': int(body['location_id'])
        }

        # Put the item in DynamoDB
        table.put_item(Item=item)

        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Successfully added inventory item',
                'item_id': item_id,
                'item': {
                    'id': item['id'],
                    'name': item['name'],
                    'description': item['description'],
                    'qty': item['qty'],
                    'price': float(item['price']),
                    'location_id': item['location_id']
                }
            })
        }

    except ValueError as ve:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Invalid data type for quantity, price, or location_id',
                'error': str(ve)
            })
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Error adding inventory item',
                'error': str(e)
            })
        }