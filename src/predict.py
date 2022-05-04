from transformers import AutoTokenizer
from somenlp.somenlp.NER.models.multi_bert import BERTMultiTaskOpt2
import json
import torch

# Setup the path of the model and the tokenizer
MODEL_PATH = "model/"
TOKENIZER_PATH = "allenai/scibert_scivocab_cased"

# Load of model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH)
model = BERTMultiTaskOpt2.from_pretrained(MODEL_PATH)

def load_encoding():
    # Opening JSON file
    f = open('model/encoding.json')
    # returns JSON object as
    # a dictionary
    data = json.load(f)
    f.close()
    # Iterating through the json
    # list
    labels_map = [("software",data['tag2name']['software']),("soft_type",data['tag2name']['soft_type']),("mention_type",data['tag2name']['mention_type'])]
    return labels_map


def entities(excerpt):
    text = excerpt
    tokens = tokenizer.tokenize(text) # genera los tokens sin el inicial y el final [cls] y [sep]
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
        for j,l in enumerate(ls):
            out = labels_map[i][1][str(l)]
            if out != 'O':
                part = tokens[j]
                # print(_idx,out,part)
                if out[0] == 'B' and name != '': 
                    _idx = aux_text.find(name)
                    _end = _idx + len(name)
                    if _idx == -1:
                        print('Error en las etiquetas/prediccion, NO DEBERIA DE OCURRIR')
                        name = part
                        # print(aux_text)
                        continue
                    idx += _idx
                    entity = out[2::]
                    end = idx+len(name)
                    preds.append({'name': name, 'type': entity, 'start': idx, 'end': end})
                    print(entity, idx, end, name)
                    idx=end
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
            idx+= _idx
            preds.append({'name': name, 'type': entity, 'start': idx, 'end': end})
            print(entity, idx, idx+len(name), name)
        else: print('No existia ninguna "B-" en el map.')

    preds.sort(key=lambda x: x['start'])
    return preds

added_info = {"technique":"relation_extraction", "version":"1.0.0"}

def newInfo(entities,relationships):
    global added_info
    relations = relationships["relationships"]
    for relation in relations:
        # print(relation["predicate"])
        if  not("softwareRequirements" in added_info) and relation["predicate"] == "softwareRequirements":
                added_info["softwareRequirements"] = []
        elif  not("hardwareRequirements" in added_info) and relation["predicate"] == "hardwareRequirements": 
                added_info["hardwareRequirements"] = []
        elif  not("supportedLanguages" in added_info) and relation["predicate"] == "supportedLanguages":
                added_info["supportedLanguages"] = []
        elif  not("supportedOS" in added_info) and relation["predicate"] == "supportedOS":
                added_info["supportedOS"] = []        
    
    
    for entity in entities:
        for relation in relations:
            if relation["predicate"] == "softwareRequirements" and entity["id"] == relation["object"] and not {"name":entity["name"]} in added_info["softwareRequirements"]:
                added_info["softwareRequirements"].append({"name":entity["name"]})
            elif relation["predicate"] == "hardwareRequirements" and entity["id"] == relation["object"] and not {"name":entity["name"]} in added_info["hardwareRequirements"]:
                added_info["hardwareRequirements"].append({"name":entity["name"]})
            elif relation["predicate"] == "supportedLanguages" and entity["id"] == relation["object"] and not {"name":entity["name"]} in added_info["supportedLanguages"]:
                added_info["supportedLanguages"].append({"name":entity["name"]})
            elif relation["predicate"] == "supportedOS" and entity["id"] == relation["object"] and not {"name":entity["name"]} in added_info["supportedLanguages"]:
                added_info["supportedOS"].append({"name":entity["name"]})    
    
    



def makeRelations(name,nerEntities):
    relationship_dict = {"relationships":[]}
    #Hacer bucle que acceda a las secciones
    idRel = 1
    
    for entity in nerEntities:
        if entity["type"] == "ProgrammingLanguage":
            relationship_dict["relationships"].append({ 
                "id": idRel,
                "subject": name,
                "predicate": "supportedLanguages",
                "object": entity["id"] 
            })
            idRel+=1
        elif entity["type"] == "Hardware":
            relationship_dict["relationships"].append({ 
                "id": idRel,
                "subject": name,
                "predicate": "hardwareRequirements",
                "object": entity["id"] 
            })
            idRel+=1
        elif entity["type"] == "SoftwareDependency":
                relationship_dict["relationships"].append({
                "id": idRel,
                "subject": name,
                "predicate": "softwareRequirements",
                "object": entity["id"] 
            })
                idRel+=1
    newInfo(nerEntities,relationship_dict)               
    return relationship_dict