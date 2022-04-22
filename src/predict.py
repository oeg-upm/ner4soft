from transformers import AutoTokenizer, AutoModelForSequenceClassification
from somenlp.NER.models.multi_bert import BERTMultiTaskOpt2
import json
import torch

# Setup the path of the model and the tokenizer
MODEL_PATH = "tfg/ner4soft/src/model/pytorch_model.bin"
TOKENIZER_PATH = "allenai/scibert_scivocab_cased"

# Load of model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH)
model = BERTMultiTaskOpt2.from_pretrained(MODEL_PATH)

def load_encoding():
    # Opening JSON file
    f = open('tfg/ner4soft/src/model/encoding.json')
    # returns JSON object as
    # a dictionary
    data = json.load(f)
    f.close()
    # Iterating through the json
    # list
    labels_map = [("software",data['tag2name']['software']),("soft_type",data['tag2name']['soft_type']),("mention_type",data['tag2name']['mention_type'])]
    return labels_map


def predict(excerpt):
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
    print(tokens)
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

p = predict("Data collection: CrystalClear (Rigaku, 2005 ▶); cell refinement: CrystalClear; data reduction: CrystalClear; program(s) used to solve structure: SHELXS97 (Sheldrick, 2008 ▶); program(s) used to refine structure: SHELXL97 (Sheldrick, 2008 ▶); molecular graphics: ORTEP-3 for Windows (Farrugia, 1997 ▶) and PLATON (Spek, 2009 ▶); software used to prepare material for publication: SHELXL97.")
print(p)