# -*- coding: utf-8 -*-


"""
@author: Pablo Calleja and Daniel Garijo
"""

import flask_restplus
import requests
import re
import json
from somef.cli import cli_get_data
from flask import Flask, request, current_app, abort
from flask_restplus import Api, Resource, fields
from flask_swagger_ui import get_swaggerui_blueprint
from predict import entities, makeRelations, added_info

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

Repo_URL = api.model('Repo_URL', {
    'repo_url': fields.Url(required=True, description='Url of the repo from which we will process the READMEs.')
})

Section_Body = api.model('Section_Body', {
    'originalHeader': fields.String,
    'excerpt': fields.String,
    'confidence': fields.List(fields.Integer),
    'technique': fields.String,
    'parentHeader': fields.String
})
Somef_Res = api.model('Somef_Res', {
    'name': fields.String,
    'description': fields.List(fields.Nested(Section_Body)),
    'acknowledgement': fields.List(fields.Nested(Section_Body)),
    'installation': fields.List(fields.Nested(Section_Body)),
    'requirement': fields.List(fields.Nested(Section_Body)),
    'usage': fields.List(fields.Nested(Section_Body))
})

Entity_Body = api.model('Entity_Body', {
    'id': fields.Integer,
    'name': fields.String,
    'type': fields.String,
    'start': fields.Integer,
    'end': fields.Integer
})

Relation_Body = api.model('Relation_Body',{
    'id': fields.String,
    'subject': fields.String,
    'predicate': fields.String,
    'object': fields.String
})

Ner_Body = api.model('Ner_Body', {
    'technique': fields.String,
    'version': fields.String,
    'entities': fields.List(fields.Nested(Entity_Body)),
    'relations': fields.List(fields.Nested(Relation_Body))
})


Ner_Section_Body = api.model('Ner_Section_Body', {
    'originalHeader': fields.String,
    'excerpt': fields.String,
    'confidence': fields.List(fields.Integer),
    'technique': fields.String,
    'parentHeader': fields.String,
    'ner': fields.Nested(Ner_Body)
})

Ner_Res = api.model('Ner_Res', {
    'name': fields.String,
    'description': fields.List(fields.Nested(Ner_Section_Body)),
    'acknowledgement': fields.List(fields.Nested(Ner_Section_Body)),
    'installation': fields.List(fields.Nested(Ner_Section_Body)),
    'requirement': fields.List(fields.Nested(Ner_Section_Body)),
    'usage': fields.List(fields.Nested(Ner_Section_Body))
})

def cli_get_results(repo_data):
    results = {
        "name": repo_data["name"]["excerpt"],
        "description": [],
        "acknowledgement": [],
        "installation": [],
        "requirement": [],
        "usage": []
    }

    for i in repo_data.keys():
            if i in results.keys() and i != "name":
                # filter those which are header analysis
                section_result = repo_data[i]
                for j in section_result:
                    if j["technique"] == "Header extraction":
                        #print(i)
                        current_list = results[i]
                        text_with_no_code = re.sub(r"```.*?```", 'CODE_BLOCK', j["excerpt"], 0, re.DOTALL)
                        result = {
                            "originalHeader": j["originalHeader"],
                            "excerpt": text_with_no_code,
                            "confidence": j["confidence"],
                            "technique": j["technique"]
                        }
                        if "parentHeader" in j: result['parentHeader'] = j['parentHeader'] 
                        current_list.append(result)
                        results[i] = current_list
    return results

def predict_results(excerpt,repo_name):
    res = {
            'technique': 'NER4Soft',
            'version': '1.4.5',
            'entities': [
                {
                    'id':0,
                    'name':repo_name,
                    'type':"SoftwareDependency",
                    'start': -1,
                    'end':-1
                }
                ]
    }
    
    _entities = entities(excerpt)
    for i,entity in enumerate(_entities):
        res['entities'].append(
            {
                'id':i+1,
                'name': entity['name'],
                'type': entity['type'],
                'start': entity['start'],
                'end': entity['end']
            }
        )
    print(_entities)
    relationships = makeRelations(res['entities'])
    res['relationships'] = relationships['relationships']

    return res

def ner_get_results(somef_data):
    results = somef_data
    for k in results.keys():
        if k != 'name':
            for i in range(len(results[k])):
                ner_data = predict_results(results[k][i]['excerpt'], results['name'])
                results[k][i]['ner'] = {
                    'technique': ner_data['technique'],
                    'version': ner_data['version'],
                    'entities': ner_data['entities'],
                    'relationships': ner_data['relationships']
                }
    results['relation_extraction'] = added_info
    return results
  

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
        return prepare_request_by_type(entities, ['PythonLibrary','Language', 'Hardware'])


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


@name_space.route("/somef/")
class Somef(Resource):

    @api.expect(Repo_URL)
    @api.response(200, 'Success', Somef_Res)
    def post(self):
        '''
        Method for obtaining a SOMEF result given a github URL
        '''
        data = request.json
        url = data.get('repo_url')
        data = cli_get_data(0.8, True, repo_url=url)
        res = cli_get_results(data)
        return res

@name_space.route("/predict/")
class Somef(Resource):

    @api.expect(Somef_Res)
    @api.response(200, 'Success', Ner_Res)
    def post(self):
        '''
        Method for generating the knowledge given a Somef result
        '''
        data = request.json
        res = ner_get_results(data)
        return res


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8080)  # ssl_context='adhoc'
