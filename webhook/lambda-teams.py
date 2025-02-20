import json
import os
import requests

def lambda_handler(event, context):
    # Define your webhook URL in your Lambda environment
    webhook_url = os.getenv("WEBHOOK_URL", None)

    if webhook_url is None:
        # Return error message if no webhook URL is set
        return {
            'statusCode': 500, 
            'body': 'Webhook URL is not set'
        }

    source_ip = event["requestContext"]["http"]["sourceIp"]
    # If you wish to only allow IPs from a specific source, set this value in the environment
    whitelisted_ips = os.getenv("WHITELISTED_IPS", None)
    # This is a comma-separated list of IPs

    if whitelisted_ips is not None:
        # Split the string into a list, and remove any leading or trailing whitespace from each IP address
        whitelisted_ips = [ip.strip() for ip in whitelisted_ips.split(",")]
        
        if source_ip not in whitelisted_ips:
            return {
                'statusCode': 403, 
                'body': 'Forbidden'
            }

    telemetry_events = json.loads(event['body'])
    
    # If it's a test, return OK
    for event in telemetry_events['telemetryEvents']:
        if event['telemetryEventType'] == 'TEST_TELEMETRY_WEBHOOK':
            return {
                'statusCode': 200,
                'body': 'OK'
            }
    
    # Pull some attributes from the event JSON
    telemetry_event_type = telemetry_events['telemetryEvents'][0]['telemetryEventType']

    telemetry_event = telemetry_events['telemetryEvents'][0]['telemetryEvent']
    object_type = telemetry_event['objectType']
    change_type = telemetry_event['changeType']
    change_time = telemetry_event['changeTime']
    change_source = telemetry_event['application']
    ultra_user = telemetry_event['user']
    ultra_object = telemetry_event['object']
    account_name = telemetry_event['account']
    
    # Define Teams card
    teams_message = {
        "summary": "{0} {1} {2} {3}".format(account_name, telemetry_event_type, object_type, change_type),
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "type": "AdaptiveCard",
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "version": "1.2",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": "**{0} {1}**".format(account_name, telemetry_event_type),
                            "weight": "Bolder",
                            "size": "Medium"
                        },
                        {
                            "type": "FactSet",
                            "facts": [
                                {"title": "Time", "value": change_time},
                                {"title": "Object Type", "value": object_type},
                                {"title": "Change Type", "value": change_type},
                                {"title": "Object", "value": ultra_object},
                                {"title": "Account", "value": account_name},
                                {"title": "User", "value": ultra_user},
                                {"title": "Application", "value": change_source}
                            ]
                        }
                    ]
                }
            }
        ]
    }

    # This section will format the specific change details
    if 'detail' in telemetry_event:
        changes_array = telemetry_event['detail']['changes']
        additional_facts = []
        for change in changes_array:
            additional_facts.append(
                {"title": "Value", "value": change['value'] if change['value'] else '-'}
            )
            additional_facts.append(
                {"title": "From", "value": change['from'] if change['from'] else '-'}
            )
            additional_facts.append(
                {"title": "To", "value": change['to'] if change['to'] else '-'}
            )
        
        # Extend the FactSet with additional change details
        teams_message['attachments'][0]['content']['body'][1]['facts'].extend(additional_facts)

    # Send the message to Teams
    response = requests.post(webhook_url, json.dumps(teams_message), headers={'Content-Type': 'application/json'})
    response.raise_for_status()
    
    return {
        'statusCode': 200,
        'body': 'OK'
    }