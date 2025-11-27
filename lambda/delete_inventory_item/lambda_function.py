import json
import boto3

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Inventory')


def lambda_handler(event, context):
    """
    Delete a specific inventory item by ID and location_id
    """
    try:
        # Extract item_id and location_id from path parameters and query string
        item_id = event.get('pathParameters', {}).get('id')
        
        # Get location_id from query string parameters
        query_params = event.get('queryStringParameters') or {}
        location_id = query_params.get('location_id')
        
        if not item_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Missing item ID in path parameters'
                })
            }
        
        if not location_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Missing location_id in query parameters'
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
                    'message': 'location_id must be a valid integer'
                })
            }
        
        # Check if the item exists before deleting
        response = table.get_item(
            Key={
                'id': item_id,
                'location_id': location_id
            }
        )
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': f'Item with ID {item_id} and location {location_id} not found'
                })
            }
        
        # Delete the item from DynamoDB
        table.delete_item(
            Key={
                'id': item_id,
                'location_id': location_id
            }
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': f'Successfully deleted inventory item with ID {item_id}'
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
                'message': 'Error deleting inventory item',
                'error': str(e)
            })
        }