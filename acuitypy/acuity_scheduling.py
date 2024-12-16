import hashlib
import hmac
import html
import json
import requests
import typing
import urllib

HeaderValue = typing.Dict[str, str | typing.List[str]]
OptionsValue = typing.Dict[str, str | HeaderValue]


class AcuityScheduling:
    def __init__(self, user_id: str, api_key: str, url_base: str = 'https://acuityscheduling.com'):
        self.user_id = user_id
        self.api_key = api_key
        self.url_base = url_base

    def request(self, path: str, options: OptionsValue = {}):
        if path[0] == '/':
            path = path[1:]
        url = f"{self.url_base}/api/v1/{path}"

        default_options = {
            'json': True,
            'username': self.user_id,
            'password': self.api_key
        }

        return self._request(url, options | default_options)

    def _request(self, url: str, options: OptionsValue):
        # Set the defaults
        default_options = {
            'method':   'GET',
            'username': None,
            'password': None,
            'json':     False,
            'headers':  {},
            'data':     None,
            'query':    None
        }
        options = default_options | options
        method = options['method'].upper()
        headers = options['headers']
        query = options['query']
        data = options['data']
        json = options['json'] is True

        if json and not data and method == 'PUT':
            data = []

        if data or isinstance(data, dict):
            if json:
                headers['Content-Type'] = 'application/json'
                if not isinstance(data, str):
                    data = json.dumps(data)
            else:
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
                if not isinstance(data, str):
                    data = urllib.parse.urlencode(data, doseq=True)

        if query and isinstance(query, dict):
            url += "?" + urllib.parse.urlencode(query, doseq=True)

        header = ()
        for key, value in headers:
            header.append(f"{key}: {value}")

        headers['User-Agent'] = 'AcuityScheduling-py'

        resp = None
        match method:
            case 'GET' | 'DELETE':
                resp = requests.request(
                    method,
                    url,
                    headers=headers,
                    auth=(options['username'], options['password'])
                )
            case 'POST' | 'PUT':
                resp = requests.request(
                    method,
                    url,
                    headers=headers,
                    body=data,
                    auth=(options['username'], options['password'])
                )
            case _:
                raise ValueError(f"Invalid HTTP request method: {method}")

        self.last_status_code = resp.status_code
        body = resp.json() if json else resp.content

        return body
    
    def verify_message_signature(secret: str, body: str, signature: str):
        hmac_digest = hmac.new(secret.encode(), body.encode(), hashlib.sha256).digest()
        base64_encoded = base64.b64encode(hmac_digest).decode()

        if base64_encoded != signature:
            raise ValueError('This message was forged!')

    def get_embed_code(owner: str, options: OptionsValue = {}):
        query = { 'owner': owner }
        options = { 'height': '800', 'width': '100%' } | options

        for key, option in options:
            if key == 'query':
                query = query | option
            else:
                options[key] = html.escape(option)

        query = urllib.parse(query, doseq=True)


        return (
            f"<iframe src=\"https://app.acuityscheduling.com/schedule.php?{query}\" width=\"{options['width']}\" height=\"{options['height']}\" frameBorder=\"0\"></iframe>"
		    '<script src="https://embed.acuityscheduling.com/js/embed.js" type="text/javascript"></script>'
        )

AcuityScheduling.verify_message_signature = staticmethod(AcuityScheduling.verify_message_signature)
AcuityScheduling.get_embed_code = staticmethod(AcuityScheduling.get_embed_code)
