#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 17 10:58:37 2021

@author: Pablo
"""

import json
import requests

import doccano_formatter
import re
import json
import os
from collections import Counter
import evaluator
from itertools import groupby
import argparse

from nltk.corpus import stopwords


DEBUG = False

def read_file(file):
  sentences=[]
  with open(file, 'r', encoding='utf8') as f:
    for line in f:
      line= line.replace('\n','')
     
      
      sentences.append(line.strip())
    f.close()

    return sentences  

def write_file(filename, sentences):
    with open(filename, 'w', encoding='utf8') as f:
        for s in sentences:
            f.write(s)
            f.write('\n')

    f.close()




def covert_annotations(res):
    lis=[]
    print(res)
    for re in res['annotations']:
        lis2=[]
        lis2.append(re['init'])
        
        lis2.append(re['end'])
        lis2.append(re['type'])
        lis.append(lis2)
    return lis
    
    

def valkyr_call(text):
    

    
    datt = "{ \"text\": \""+text+"\"}"
    
    sat= {
           'text': text
         
           
           }
    
    
    hed = {
           'accept': 'application/json;charset=UTF-8'
           ,'Content-Type': 'application/json;charset=UTF-8'
           
           }
    
    url='https://ner4soft-service.linkeddata.es/processText'
    

    
    response = requests.post(url, json=sat, headers=hed)
    
    return response.json()
          

    






def execute_ner4soft(lines):


   
    
    
    
    res_lines=[]
    for line in lines[0:20]:
        
        f= json.loads(line)
        text= f['data']
        res =valkyr_call(text)
        lis= covert_annotations(res)
        f['label']=lis
        
        # convert into JSON:
        y = json.dumps(f)
        res_lines.append(y)        
    
    
    write_file('result.jsonl',res_lines)
    



class TokenSequence:
    
    
    def __init__(self, tokens, labels=None,):
        self.tokens=tokens
        if labels is None:  
            self.labels=[]
            for i in range(0,len(tokens)):
                self.labels.append('O')
        else:
            self.labels=labels
            self.evaluation_labels=labels
    
    def setEvaluation_labels(self,labels):
        self.evaluation_labels=labels
    
    def restart_labels(self):
        self.labels=[]
        for i in range(0,len(self.tokens)):
            self.labels.append('O')
            
            
            
    def annotate_BIOtext_with_Terms(self,listTerms, annotationType):
        '''
        ugly method. TO BE IMPROVED.
        Annotate the terms (string) that are in the list of terms in the list of tokens 
        following the tags of BIO FORMAT 

        Parameters
        ----------
        listTerms : TYPE
            DESCRIPTION.
        annotationType : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        '''
   
        for term in listTerms:
            
            wordTerms= term.split(' ')
            
            if len(wordTerms)>1:
                
                res=[]
                ## CODIGO MALO
                if len(wordTerms) == 2:
                    res = list(zip(self.tokens, self.tokens[len(wordTerms)-1:]))
                
                if len(wordTerms) == 3:
                    res = list(zip(self.tokens,  self.tokens[len(wordTerms)-2:], self.tokens[len(wordTerms)-1:]))
                if len(wordTerms) == 4:
                    res = list(zip(self.tokens,  self.tokens[len(wordTerms)-3:], self.tokens[len(wordTerms)-2:], self.tokens[len(wordTerms)-1:]))
                if len(wordTerms) == 5:
                    res = list(zip(self.tokens,  self.tokens[len(wordTerms)-4:], self.tokens[len(wordTerms)-3:], self.tokens[len(wordTerms)-2:],self.tokens[len(wordTerms)-1:]))

                
                counter=0
                for re in res:
                    
                    if tuple(wordTerms)== re:
                        ## found
                        self.labels[counter]='B'+annotationType
                        for insides in range(0,len(wordTerms)-1):
                            self.labels[counter+insides+1]='I'+annotationType
                            
                    
                    counter+=1
            else:
                counter=0
                for tok in self.tokens:                    
                   
                    if wordTerms[0]== tok:
                        ## found
                        self.labels[counter]='B'+annotationType
                        
                    counter+=1

        
        return self.labels

 

            
            
    
    



def readConll(file):
    '''
    Reads a CONLL file and returns A list of TokenSequence

    Parameters
    ----------
    file : TYPE
        DESCRIPTION.

    Returns
    -------
    sentences : TYPE
        DESCRIPTION.

    '''

    sentences=[]
    sentenceLabel=[]
    sentenceToken=[]
    with open(file, 'r') as f:
        for line in f:
            if line.strip() == '':
                print(sentenceToken)
                
                print(sentenceLabel)
                sentences.append( TokenSequence(sentenceToken,sentenceLabel))
                sentenceLabel=[]
                sentenceToken=[]
                break
                continue
            splt = line.replace('\n','').split(' ')
            #print(line)
            sentenceToken.append(splt[0])
            #if len(splt) == 3: 
                #  sentenceLabel.append(splt[2])
                #else:
            sentenceLabel.append(splt[1])
            
    f.close()
    return sentences



def evaluation(token_sequences):
    """
    token_sequences: list of TokenSequence
    """
    CompleteResults = []
    CompleteGold = []

    for i in token_sequences:
        CompleteResults.append(i.labels)
        CompleteGold.append(i.evaluation_labels)

    return evaluator.iw_evaluation(CompleteGold, CompleteResults)

def evaluation(token_sequences1,token_sequences2):
    """
    token_sequences: list of TokenSequence
    """
    CompleteResults = []
    CompleteGold = []

    for i in token_sequences1:
        CompleteResults.append(i.labels)
        #CompleteGold.append(i.evaluation_labels)
    for i in token_sequences2:
        #CompleteResults.append(i.labels)
        CompleteGold.append(i.labels)

    return evaluator.ner_evaluation(CompleteGold, CompleteResults)



def main():
    """
    Parse the arguments
    :return:
    """
    parser = argparse.ArgumentParser(description='t')
    parser.add_argument('--gs', help="The path to the gs file.")  # 'gold.jsonl'

    #parser.add_argument('--conference_dir', help="The path to the gs file.")
   

    args = parser.parse_args()
    if args.gs:
        
        
        
        ##
        lines = read_file(args.gs)
        ##
        execute_ner4soft(lines)
        
        ##
        doccano_formatter.convert_jsonl_to_conll(args.gs,'gs.conll')
        doccano_formatter.convert_jsonl_to_conll('result.jsonl','result.conll')
        
        
        toq2 = readConll('resp.conll')
        toq1 = readConll('eval.conll')
        
        evaluation(toq2,toq1)
        
        
    else:
        parser.print_usage()
        parser.print_help()


if __name__ == '__main__':
    main()





#execute_ner4soft(path)






