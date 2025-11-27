import json
import boto3
from decimal import Decimal

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Inventory')


class DecimalEncoder(json.JSONEncoder):
    """Helper class to convert Decimal objects to float for JSON serialization"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def lambda_handler(event, context):
    """
    Get all inventory items for a specific location using GSI
    """
    try:
        # Extract location_id from path parameters
        location_id = event.get('pathParameters', {}).get('id')
        
        if not location_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Missing location ID in path parameters'
                })
            }
        
        # Convert location_id to integer
        try:
            location_id = int(location_id)
        except ValueError:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Location ID must be a valid integer'
                })
            }
        
        # Query the GSI to get items by location
        response = table.query(
            IndexName='LocationIndex',
            KeyConditionExpression='location_id = :location_id',
            ExpressionAttributeValues={
                ':location_id': location_id
            }
        )
        
        items = response.get('Items', [])
        
        # Handle pagination if there are more items
        while 'LastEvaluatedKey' in response:
            response = table.query(
                IndexName='LocationIndex',
                KeyConditionExpression='location_id = :location_id',
                ExpressionAttributeValues={
                    ':location_id': location_id
                },
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items.extend(response.get('Items', []))
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': f'Successfully retrieved inventory items for location {location_id}',
                'location_id': location_id,
                'count': len(items),
                'items': items
            }, cls=DecimalEncoder)
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
                'message': 'Error retrieving inventory items by location',
                'error': str(e)
            })
        }