import requests as req

class FbApp:
    
    def __init__(self, page_access_token, fb_graph_url):
        self.page_access_token = page_access_token
        self.fb_graph_url = fb_graph_url

    def get_page_token(self):
        return self.page_access_token

    def send_message(self, sender_psid, data):
        # Construct the message body
        request_body = {
            "recipient": {
                "id": sender_psid
            },
            "message": data
        }

        qs = { "access_token": self.page_access_token}
        res = req.post(
            url = self.fb_graph_url, 
            params = qs,
            json = request_body
        )

        if(res.status_code == 200):
            print(f'Successfully sent a message to user "{sender_psid}"')
        elif(res.status_code == 400):
            print('The facebook graph url is not found')
