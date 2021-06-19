from flask import Flask, request
import json
import requests as req

from config import config
from services.fb import FbApp

app = Flask(__name__)

Fb = None

def configure_fb_app():
    global Fb
    Fb = FbApp(config['fb_page_access_token'], config['fb_graph_url'])  


@app.route('/webhook', methods = ['POST'])
def webhook_endpoint():
    body = request.get_json()

    if (body['object'] == 'page'):
        #  Iterates over each entry - there may be multiple if batched
        for entry in body['entry']:
            # Gets the message. entry.messaging is an array, but 
            # will only ever contain one message, so we get index 0
            webhook_event = entry['messaging'][0]
            print(webhook_event)

            # Get the sender PSID
            sender_psid = webhook_event['sender']['id']
            print(f'Sender PSID: {sender_psid}')

            # Check if the event is a message or postback and
            # pass the event to the appropriate handler function
            if(webhook_event['message']):
                handle_message(sender_psid, webhook_event['message'])       
            elif (webhook_event.postback):
                handle_postback(sender_psid, webhook_event['postback'])

        # Returns a '200 OK' response to all requests
        return 'EVENT_RECEIVED', 200
    else:
        # Returns a '404 Not Found' if event is not from a page subscription
        return 'Not Found', 404

# Adds support for GET requests to our webhook
@app.route('/webhook')
def verify_webhook():
    # Parse the query params
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    # Checks if a token and mode is in the query string of the request
    if (mode and token):
    
        # Checks the mode and token sent is correct
        if (mode == 'subscribe' and token == config['facebook_verification_token']):
      
            # Responds with the challenge token from the request
            print('WEBHOOK_VERIFIED')
            return challenge, 200
        else:
            # Responds with '403 Forbidden' if verify tokens do not match      
            return 'Forbidden', 403

# Handles messages events
def handle_message(sender_psid, received_message):
    response = None
    response_text = None

    # Check if the message contains text
    if('text' in received_message):
        response_text = f'I will provide you the audio from the sent handwritten text image.'
    elif('attachments' in received_message):
        #  Gets the URL of the message attachment
        attachment_url = received_message['attachments'][0]['payload']['url']
        response_text = f'I received your attachment, but right now handwritten text to audio feature is not implemented. Please try after some days. \nHere is the url of your attachment: {attachment_url}'
    else:
        response_text = f'Sorry, we does not support this type of message right now. Please try sending different type of messages.'

    if (response_text == None):
        response_text = 'Sorry, there is some internal problem. We are not operating right now.\nPlease try again after sometime.'
    
    response = {
        "text": response_text
    }

    print(f'sending message to recipient {sender_psid}: {response["text"]}')

    # Sends the response message
    Fb.send_message(sender_psid, response)

# Handles messaging_postbacks events
def handle_postback(sender_psid, received_postback):
    response = { "text": "You sent unsupported media type. Please only send text to receive reply." }
    
    # Send the message to acknowledge the postback
    Fb.send_message(sender_psid, response)


if __name__ == '__main__':
    configure_fb_app()
    port = int(config['port'])
    if(config['env'] == 'prod'):
        # app.run(host = '0.0.0.0', port = 1337, debug = False)
        app.run(host = '0.0.0.0', port = port, debug = False)
    else:
        app.run(host = '127.0.0.1', port = port, debug = True)  # debug set to True will auto-recompile
                                                                # application upon any change