#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 11 13:23:48 2021

@author: Pablo Calleja
"""



import json
import nltk






def tokenize(txt):
    res= nltk.word_tokenize(txt)
    return res

def get_entities_in_offset(entities,text, start, end):
    result=[]
    #print('---'+str(start)+' '+str(end))
    for entity in entities:
        start_e= entity[0]
        end_e= entity[1]
        #print(str(start_e)+' '+str(end_e))
        if start_e >= start and end_e <= end:
            ent=entity
            ent.append(text[start_e:end_e])
            result.append(ent)
    return result


def annotate_entities(tokens, entities,sentence,offset_total):
    labels=[]
    print('Annotating sentence:')
    print(sentence)
    for token in tokens:
        labels.append('O')
    for entity in entities:
        
        start_e= entity[0] - offset_total
        entity_text= entity[3]
        
        tag=entity[2]
        substring = tokenize(sentence[:start_e]+' ')
       
        n_toks_to= len(substring)
        entity_tok= tokenize(entity_text)
        entity_len= len(entity_tok)
        
        
        ## These two ifs are for tokenization problems: 
            # the annotations does not cover a true token: 3 (annotation) in 3.2.0 (token), and maybe is the last one
        if n_toks_to >= len(tokens):
            continue
        
        if entity_tok[0] != tokens[n_toks_to]:
            print('Warning: error in tokenizer')
            print(str(entity_text) +' in:: '+ str(tokens))
            
            continue
        
        
      
        
        labels[n_toks_to]='B-'+tag
        if entity_len > 1:
            for counts in range(1,entity_len):
                labels[n_toks_to+counts]= 'I-'+tag
        
    
    
    return labels     
        



def read_file(file):
  sentences=[]
  with open(file, 'r',encoding='utf8') as f:
    for line in f:
      line= line.replace('\n','')
     
      
      sentences.append(json.loads(line))
    f.close()
    return sentences  


def write_file(filename, sentences):
    with open(filename, 'w', encoding='utf8') as f:
        for s in sentences:
            f.write(s)
            f.write('\n')

    f.close()

def convert_jsonl_to_conll(file,outputfile):
    

    datafile =read_file(file)
    
    
    token_list=[]
    label_list=[]
    
    for data in datafile:
        
        labels= data['label']
        text =data['data']
        
        
        sentences= text.split('\n')
        
        listofentities= labels
        
        
        offset_total=0
        for sentence in sentences:
            offset_plus= len(sentence) 
            
            tokens=tokenize(sentence)
            if len(tokens)==0:
                offset_total+=1
                continue
            offset_end=offset_total+ offset_plus
           
            
            entities2= get_entities_in_offset(listofentities, text, offset_total, offset_end)
            
            
            lab=annotate_entities(tokens, entities2,sentence,offset_total)    
            
            offset_total=offset_end+1
            
            token_list.append(tokens)
            label_list.append(lab)
            
    lines=[]
    for tokens,labels in zip(token_list,label_list):
        
        for token,label in zip(tokens,labels):
            lines.append(token+' '+label)

        lines.append('\n')
    write_file(outputfile,lines)
    









