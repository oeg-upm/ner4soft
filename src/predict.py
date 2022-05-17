from transformers import AutoTokenizer
from somenlp.somenlp.NER.models.multi_bert import BERTMultiTaskOpt2
import json
import torch

# Setup the path of the model and the tokenizer
MODEL_PATH = "models/save/Gold-Multi-Simple-SciBERT/13-05-2022_07-10-33"
TOKENIZER_PATH = "allenai/scibert_scivocab_cased"

# Load of model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH)
model = BERTMultiTaskOpt2.from_pretrained(MODEL_PATH)


def load_encoding():
    # Opening JSON file
    f = open(f'{MODEL_PATH}/encoding.json')
    # returns JSON object as
    # a dictionary
    data = json.load(f)
    f.close()
    # Iterating through the json
    # list
    labels_map = [("software", data['tag2name']['software']), ("soft_type", data['tag2name']
                                                               ['soft_type']), ("mention_type", data['tag2name']['mention_type'])]
    return labels_map


def entities(excerpt):
    text = excerpt
    # genera los tokens sin el inicial y el final [cls] y [sep]
    tokens = tokenizer.tokenize(text)
    inputs = tokenizer(text, return_tensors="pt")
    out = model(**inputs)
    logits = out[1:-2]
    tag_seq = [torch.argmax(logits[i], axis=2) for i in range(len(logits))]
    lis = [tag_seq[i].tolist()[0] for i in range(len(tag_seq))]
    lis = [lis[i][1:-1] for i in range(len(lis))]

    labels_map = load_encoding()

    preds = []
    print(text)
    for i, ls in enumerate(lis):
        print(f"\nlabels_map {labels_map[i][0]}\n")
        name = ''
        entity = ''
        idx = 0
        aux_text = text.lower()
        for j, l in enumerate(ls):
            out = labels_map[i][1][str(l)]
            if out != 'O':
                part = tokens[j]
                # print(_idx,out,part)
                if out[0] == 'B' and name != '':
                    _idx = aux_text.find(name)
                    _end = _idx + len(name)
                    if _idx == -1:
                        print(
                            'Error en las etiquetas/prediccion, NO DEBERIA DE OCURRIR')
                        name = part
                        # print(aux_text)
                        continue
                    idx += _idx
                    entity = out[2::]
                    end = idx+len(name)
                    preds.append({'name': name, 'type': entity,
                                 'start': idx, 'end': end})
                    print(entity, idx, end, name)
                    idx = end
                    name = ''
                    aux_text = aux_text[_end::]
                    # print(aux_text)
                if tokens[j][0:2] == '##':
                    part = tokens[j][2::]
                name += part
                # print(out,tokens[j])
        if entity != '':
            _idx = aux_text.find(name)
            if _idx == -1:
                print('Error en las etiquetas/prediccion, NO DEBERIA DE OCURRIR')
                continue
            idx += _idx
            preds.append({'name': name, 'type': entity,
                         'start': idx, 'end': end})
            print(entity, idx, idx+len(name), name)
        else:
            print('No existia ninguna "B-" en el map.')

    preds.sort(key=lambda x: x['start'])
    preds = [k for n, k in enumerate(preds) if k not in preds[n+1:]]
    print(preds)
    return preds

# version 1.3.0
# All code below is for TESTING PURPOSES ONLY and will be modified for our prototype
# ADDED new function addVersions
# UPDATED makeRelations to detect supportedOS relations
##


# This global variable added_info will have the extra information extracted from the relationships section of ner, as well
# as the technique and it's current version
added_info = {"technique": "relation_extraction", "version": "1.3.0"}

# This is the function newInfo which adds the knowledge gathered from our entities and relationships sections of ner as
# parameters updating our global variable


def newInfo(entities, relationships):
    if (type(entities) != list or type(relationships) != dict) or (not bool(relationships) or not entities):
        print("Error: faltan entidades y/o relaciones")
        return None
    global added_info

    # Here we get the relationships array from the relationships section of our JSON
    # and depending on the entities we first initialize each section with the loop
    # below depending on the relationships found
    relations = relationships["relationships"]

    for relation in relations:

        if not("softwareRequirements" in added_info) and relation["predicate"] == "softwareRequirements":
            added_info["softwareRequirements"] = []

        elif not("hardwareRequirements" in added_info) and relation["predicate"] == "hardwareRequirements":
            added_info["hardwareRequirements"] = []

        elif not("supportedLanguages" in added_info) and relation["predicate"] == "supportedLanguages":
            added_info["supportedLanguages"] = []

        elif not("supportedOS" in added_info) and relation["predicate"] == "supportedOS":
            added_info["supportedOS"] = []

        elif not("usagePlatforms" in added_info) and relation["predicate"] == "usagePlatforms":
            added_info["usagePlatforms"] = []

   # Aftewards in the following loop we initialize an empty version dictionary and an object id, in
   # order to put the version with the corresponding software/language. That's why we loop both
   # entities and relationships. In case we don't find any version we put put just the name of the
   # entity in the corresponding section

    versions = []

    for entity in entities:
        for relation in relations:

            if relation["predicate"] == "softwareRequirements" and entity["id"] == relation["object"] and not {"name": entity["name"]} in added_info["softwareRequirements"]:
                added_info["softwareRequirements"].append(
                    {"name": entity["name"]})

            elif relation["predicate"] == "hardwareRequirements" and entity["id"] == relation["object"] and not {"name": entity["name"]} in added_info["hardwareRequirements"]:
                added_info["hardwareRequirements"].append(
                    {"name": entity["name"]})

            elif relation["predicate"] == "supportedLanguages" and entity["id"] == relation["object"] and not {"name": entity["name"]} in added_info["supportedLanguages"]:
                added_info["supportedLanguages"].append(
                    {"name": entity["name"]})

            elif relation["predicate"] == "supportedOS" and entity["id"] == relation["object"] and not {"name": entity["name"]} in added_info["supportedOS"]:
                added_info["supportedOS"].append({"name": entity["name"]})

            elif relation["predicate"] == "usagePlatforms" and entity["id"] == relation["object"] and not {"name": entity["name"]} in added_info["usagePlatforms"]:
                added_info["usagePlatforms"].append({"name": entity["name"]})

            # this branch is for capturing the version if there exist a versionOf relationship
            elif relation["predicate"] == "versionOf" and entity["id"] == relation["subject"]:
                versions.append((relation["object"], entity["name"]))

    if versions:
        addVersions(entities, versions)


def addVersions(entities, versions):
    if (type(entities) != list or type(versions) != list) or not entities:
        print("Error: faltan entidades y/o relaciones")
        return None

    global added_info

    for entity in entities:
        for version in versions:
            if version[0] == entity["id"]:

                if entity["type"] == "SoftwareDependency":
                    for software in added_info["softwareRequirements"]:
                        if entity["name"] == software["name"]:
                            if not "version" in software:
                                software.update({"version": []})
                            newVersions = set(software["version"])
                            newVersions.add(version[1])
                            software["version"] = list(newVersions)

                if entity["type"] == "ProgrammingLanguage":
                    for language in added_info["supportedLanguages"]:
                        if entity["name"] == language["name"]:
                            if not "version" in language:
                                language.update({"version": []})
                            newVersions = set(language["version"])
                            newVersions.add(version[1])
                            language["version"] = list(newVersions)

                if entity["type"] == "DeploymentPlatforms":
                    for depployPlatform in added_info["usagePlatforms"]:
                        if entity["name"] == depployPlatform["name"]:
                            if not "version" in depployPlatform:
                                depployPlatform.update({"version": []})
                            newVersions = set(depployPlatform["version"])
                            newVersions.add(version[1])
                            depployPlatform["version"] = list(newVersions)

                if entity["type"] == "OperativeSystem":
                    for oSystem in added_info["supportedOS"]:
                        if entity["name"] == oSystem["name"]:
                            if not "version" in oSystem:
                                oSystem.update({"version": []})
                            newVersions = set(oSystem["version"])
                            newVersions.add(version[1])
                            oSystem["version"] = list(newVersions)


def makeRelations(nerEntities):
    if type(nerEntities) != list or not nerEntities:
        print("Error: pasar una sección de ner válida")
        return None

    # First we initialize the relationship
    relationship_dict = {"relationships": []}
    # nerEntities = section[0]["ner"]["entities"]  #This line is deleted in the joint version because we will receive it directly from our service
    idRel = 1  # Needed for our creation of relationship ids (FORMAT r + idREl)

    # In this loop when we find entities corresponding to programing, languages hardware and software. The function
    # adds them accordingly into the relationship section of ner
    for entity in nerEntities:
        if entity["type"] == "ProgrammingLanguage":
            relationship_dict["relationships"].append({
                "id": "r" + str(idRel),
                # this will be changed with id=0 (which will be the id of the named repository) in order to maintain consistency
                "subject": 0,
                "predicate": "supportedLanguages",
                "object": entity["id"]
            })
            idRel += 1
        elif entity["type"] == "Hardware":
            relationship_dict["relationships"].append({
                "id": "r" + str(idRel),
                "subject": 0,
                "predicate": "hardwareRequirements",
                "object": entity["id"]
            })
            idRel += 1
        elif entity["type"] == "SoftwareDependency":
            relationship_dict["relationships"].append({
                "id": "r" + str(idRel),
                "subject": 0,
                "predicate": "softwareRequirements",
                "object": entity["id"]
            })
            idRel += 1
        elif entity["type"] == "DeploymentPlatform":
            relationship_dict["relationships"].append({
                "id": "r" + str(idRel),
                "subject": 0,
                "predicate": "usagePlatforms",
                "object": entity["id"]
            })
            idRel += 1
        elif entity["type"] == "OperativeSystem":
            relationship_dict["relationships"].append({
                "id": "r" + str(idRel),
                "subject": 0,
                "predicate": "supportedOS",
                "object": entity["id"]
            })
            idRel += 1

    # here we call newInfo since it needs the newly created dictionary to update itself
    newInfo(nerEntities, relationship_dict)
    return relationship_dict
