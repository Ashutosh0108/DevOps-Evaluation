import boto3
import json
import uuid
import logging

# Set up logging to CloudWatch
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize the DynamoDB resource
dynamodb = boto3.resource('dynamodb')
# Use the exact table name you created
table = dynamodb.Table('DG-event-log')

def lambda_handler(event, context):
    try:
        # Log the raw event to CloudWatch for your runbook screenshots
        logger.info(f"Incoming Event: {json.dumps(event)}")
        
        # 1. Extract the mandatory fields required by the test
        detail = event.get('detail', {})
        
        event_time = event.get('time', 'N/A')
        event_source = event.get('source', 'N/A')
        event_name = event.get('detail-type', 'N/A')
        region = event.get('region', 'ap-south-1')
        
        if event_source == "aws.s3":
            # S3 events come via CloudTrail
            event_name = detail.get('eventName')
            resource_name = detail.get('requestParameters', {}).get('bucketName', 'Unknown-Bucket')
            username = detail.get('userIdentity', {}).get('userName') or \
                    detail.get('userIdentity', {}).get('principalId', 'AWS-System')
        
        elif event_source == "aws.ec2":
            # EC2 events come from State-change notifications
            event_name = f"EC2 Instance {detail.get('state')}"
            resource_name = detail.get('instance-id', 'Unknown-Instance')
            username = "EC2-Service-Notification" # State changes are often automated
        
        else:
            event_name = "Unknown Event"
            resource_name = "N/A"
            username = "N/A"
        # 2. Parse Resource Name based on whether it is S3 or EC2
        # resource_name = "N/A"
        # if event_source == 'aws.s3':
        #     resource_name = detail.get('requestParameters', {}).get('bucketName', 'Unknown-Bucket')
        # elif event_source == 'aws.ec2':
        #     resource_name = detail.get('instance-id', 'Unknown-Instance')

        # 3. Extract Username from the userIdentity block
        # user_identity = detail.get('userIdentity', {})
        # username = user_identity.get('userName', user_identity.get('principalId', 'System-Auto'))

        # 4. Prepare the item for DynamoDB (Partition Key: EventID)
        item = {
            'EventID': str(uuid.uuid4()), 
            'EventTime': event_time,
            'EventSource': event_source,
            'EventName': event_name,
            'ResourceName': resource_name,
            'Region': region,
            'Username': username
        }

        # 5. Write data into DynamoDB
        table.put_item(Item=item)
        logger.info(f"Successfully logged {event_name} to DynamoDB.")

        return {
            'statusCode': 200,
            'body': json.dumps('Event successfully logged!')
        }

    except Exception as e:
        logger.error(f"Execution Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
    
# hit me