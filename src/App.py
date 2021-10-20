# -*- coding: utf-8 -*-


"""
@author: Pablo Calleja and Daniel Garijo
"""

import flask_restplus
import requests
from flask import Flask, request, current_app, abort
from flask_restplus import Api, Resource, fields
from flask_swagger_ui import get_swaggerui_blueprint

flask_restplus.__version__

# # For ssl certificates
# import ssl
# context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# context.load_cert_chain('selfsigned.crt', 'private.key')

# TO DO: read from properties/config yaml file.
VALKYRE_SERVICE = 'http://localhost:8084/processText'

app = Flask(__name__)
api = Api(app=app, version='1.0', title='NER4Soft',
          description='API for recognizing named entities related to software')

name_space = api.namespace('ner4soft', description='NER APIs')

SWAGGER_UI_BLUEPRINT = get_swaggerui_blueprint(
    '/swagger',
    '/swagger.json',
    config={
        'app_name': "ner4soft"
    }
)
app.register_blueprint(SWAGGER_UI_BLUEPRINT, url_prefix='/swagger')

Text = api.model('Text', {
    'text': fields.String(required=True, description='Text to be processed',
                          default='This software is was designed for Ubuntu and Pytorch 1.0'),
})


def post_valkyrie(text):
    try:
        text = text.rstrip().replace("\n", " ")
        text = text.replace("\"", "")
        text = text.encode('utf-8')
        head = {
            'accept': 'application/json;charset=UTF-8',
            'Content-Type': 'application/json;charset=UTF-8'
        }

        url = VALKYRE_SERVICE

        post_data = "{ \"text\": \"" + str(text) + "\"}"
        x = requests.post(url, data=post_data, headers=head)
        return x.json()
    except Exception as e:
        current_app.logger.info('Error when processing request ' + str(e))
        abort(500)


def prepare_request_by_type(response_valkyre, type_ann):
    """
    Method to prepare the response depending on the type requested.
    Args:
        response_valkyre: response from the valkyre service
        type_ann: list with the types we want to filter by

    Returns:
        JSON file with the found annotations, or empty otherwise.
    """
    result = []
    if 'annotations' not in response_valkyre:
        return {}
    for annot in response_valkyre['annotations']:
        if annot['type'] in type_ann:
            result.append(annot)

    response = {
        'entities': result
    }
    return response


@name_space.route("/requirements/")
class Requirements(Resource):

    @api.expect(Text)
    def post(self):
        """
        Method for detecting software libraries and requirements from text.
        Requirements include hardware requirements too. Anything on the "requirement" section
        """
        data = request.json
        text = data.get('text')
        entities = post_valkyrie(text)
        current_app.logger.info('received a requirement request')
        return prepare_request_by_type(entities, ['PythonLibrary', 'Hardware'])


@name_space.route("/usage/")
class SoftwareEntities(Resource):

    @api.expect(Text)
    def post(self):
        """
        Method for detecting libraries, frameworks, OS, and hardware that may not be required.
        This method is a little more generic than requirements
        """
        data = request.json
        text = data.get('text')
        entities = post_valkyrie(text)
        # TO DO
        current_app.logger.info('received a software entity request')
        return prepare_request_by_type(entities, ['PythonLibrary', 'Hardware'])


@name_space.route("/agents/")
class Requirements(Resource):

    @api.expect(Text)
    def post(self):
        """
        Method for detecting any responsible agent and organization.
        These agents could appear as co-authors, in acknoweledgements (funding) or as a conference.
        """
        data = request.json
        text = data.get('text')
        entities = post_valkyrie(text)
        # TO DO
        current_app.logger.info('received an agent request')
        return prepare_request_by_type(entities, ['Person'])


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)  # ssl_context='adhoc'
