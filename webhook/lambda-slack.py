import json
import urllib3

slack_webhook_url = "https://hooks.slack.com/services/MY-SLACK-ENDPOINT"

headers = {
  'Content-Type': "application/json",
  'Accept': "*/*",
  'Cache-Control': "no-cache",
  'Host': "hooks.slack.com",
  'Accept-Encoding': "gzip, deflate"
}

def lambda_handler(event, context):
  http = urllib3.PoolManager()

  telemetryEvents = event

  # Pull some attributes from the event JSON
  telemetryEventType = telemetryEvents['telemetryEvents'][0]['telemetryEventType']

  telemetryEvent = telemetryEvents['telemetryEvents'][0]['telemetryEvent']
  objectType = telemetryEvent['objectType']
  changeType = telemetryEvent['changeType']
  changeTime = telemetryEvent['changeTime']
  changeSource = telemetryEvent['application']
  ultraUser = telemetryEvent['user']
  ultraObject = telemetryEvent['object']
  accountName = telemetryEvent['account']

  # Refer to https://api.slack.com/block-kit to learn about slack blocks and messages
  slackBlocks = [
       { "type": "header",
         "text": {
            "type": "plain_text",
            "text": "{0} {1} {2} {3}".format(accountName, telemetryEventType, objectType, changeType),
            "emoji": True
         }
       },
       { "type": "section",
         "fields": [
            { "type": "mrkdwn", "text": "*Time*" },
            { "type": "mrkdwn", "text": changeTime },
            { "type": "mrkdwn", "text": "*Object Type*" },
            { "type": "mrkdwn", "text": objectType },
            { "type": "mrkdwn", "text": "*Change Type*" },
            { "type": "mrkdwn", "text": changeType },
            { "type": "mrkdwn", "text": "*Object*" },
            { "type": "mrkdwn", "text": ultraObject }
          ]
       },
       { "type": "section",
         "fields": [
            { "type": "mrkdwn", "text": "*Account*" },
            { "type": "mrkdwn", "text": accountName },
            { "type": "mrkdwn", "text": "*User*" },
            { "type": "mrkdwn", "text": ultraUser },
            { "type": "mrkdwn", "text": "*Application*" },
            { "type": "mrkdwn", "text": changeSource }
          ]
       }
    ]

  # This section will format the specfic change details
  if 'detail' in telemetryEvent:
    slackBlocks.append({ "type": "divider"})
    changesArray = telemetryEvent['detail']['changes']
    for change in changesArray:
      slackBlocks.append({ "type": "section",
                           "fields": [{"type": "mrkdwn", "text": "*Value*"},
                                      {"type": "mrkdwn", "text": change['value'] if change['value'] else '-'},
                                      {"type": "mrkdwn","text": "*From*"},
                                      {"type": "mrkdwn", "text": change['from'] if change['from'] else '-'},
                                      {"type": "mrkdwn","text": "*To*"},
                                      {"type": "mrkdwn", "text": change['to'] if change['to'] else '-'}
                                     ]
                        })

  # Format the raw event as some slack markdown
  slackBlocks.append({ "type": "divider" })
  slackBlocks.append({ "type": "section",
                       "text": { "type": "mrkdwn", "text": "```{0}```".format(event) }
                    })

    telemetrySlackObject = {
        "blocks": slackBlocks
    }

    # post the formatted event to slack
    response = http.request('POST',
                        slack_webhook_url,
                        body = json.dumps(telemetrySlackObject),
                        headers = headers,
                        retries=False)

    responseFromSlackHook = {"status":response.status, "body":response.data.decode("utf-8")}

    return {
        'statusCode': 200,
        'body': json.dumps(responseFromSlackHook)
    }
