# -*- coding: utf-8 -*-


"""
@author: Pablo Calleja and Daniel Garijo
"""

import flask_restplus

flask_restplus.__version__
import requests
from flask import Flask, request
from flask_restplus import Api, Resource, fields
from flask_swagger_ui import get_swaggerui_blueprint

## For ssl certificates
# import ssl
# context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# context.load_cert_chain('selfsigned.crt', 'private.key')

app = Flask(__name__)
api = Api(app=app, version='1.0', title='NER4Soft', description='API')

name_space = api.namespace('ner4soft', description='NER APIs')

SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    '/swagger',
    '/swagger.json',
    config={
        'app_name': "ner4soft"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix='/swagger')

Text = api.model('Text', {
    'text': fields.String(required=True, description='Text to be processed', default='hello world'),
})


def postValkyrie(text):
    # 'test string\n'.rstrip()
    text = text.rstrip().replace("\n", " ")
    text = text.replace("\"", "")
    text = text.encode('utf-8')

    # print(text)
    head = {
        'accept': 'application/json;charset=UTF-8',
        'Content-Type': 'application/json;charset=UTF-8'

    }

    url = 'http://localhost:8084/processText'

    datas = "{ \"text\": \"" + str(text) + "\"}"
    x = requests.post(url, data=datas, headers=head)

    return x.json()


@name_space.route("/requirements/")
class Requirements(Resource):

    @api.expect(Text)
    def post(self):
        """
        To libraries
        """
        data = request.json
        text = data.get('text')

        entities = postValkyrie(text)

        # TheSentence= ('Clustering of missense mutations in the ataxia-telangiectasia gene in a sporadic T-cell leukaemia')

        # sentence, labels= NerModelJNLPBA.predict(text)

        result = []

        if 'annotations' not in entities:
            return {}
        for annot in entities['annotations']:
            if annot['type'] == 'PythonLibrary':
                result.append(annot)

        response = {
            'entities': result
        }
        return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8090)  # ssl_context='adhoc'
