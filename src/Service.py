# -*- coding: utf-8 -*-




"""
Created on Wed Mar 31 10:23:50 2021

@author: Pablo
"""


import tensorflow

import tensorflow as tf
tf.__version__

import transformers as tr
tr.__version__


import logging
import os
import sys
import pdb
import subprocess

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
from seqeval.metrics import f1_score, precision_score, recall_score
from torch import nn

from transformers import (
    AutoConfig,
    AutoModelForTokenClassification,
    AutoModel,
    AutoTokenizer,
    EvalPrediction,
    HfArgumentParser,
    Trainer,
    TrainingArguments,
    set_seed,
)
#from utils_ner import NerDataset, Split, get_labels
from utils import MyNerDataset,  Split, get_labels

##### Frases

from transformers import TransfoXLConfig, TransfoXLModel
from transformers import TransfoXLTokenizer, TransfoXLModel
import torch



'''

!pip install tensorflow

!pip install seqeval

!pip install torch

!pip install transformers==3.0.0 


!pip install tqdm
!pip install ipywidgets

'''




class NERModel:
    
    
    Model=None
    Trainer=None
    Config=None
    Labels=None
    
    
    
    # parameterized constructor
    def __init__(self, name, path,path2):
        self.Name = name
        self.ModelPath = path
        self.CorpusPath= path2
      ##### Frases

        self.TokenizadorFrases = TransfoXLTokenizer.from_pretrained('transfo-xl-wt103')
     
        
         ## logging
        
        
        logger = logging.getLogger(__name__)
        
         # Setup logging
        logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s",
            datefmt="%m/%d/%Y %H:%M:%S",
            level=logging.WARN # if training_args.local_rank in [-1, 0] else logging.WARN,
            )
        
        
     
    def align_predictions(self,predictions: np.ndarray, label_ids: np.ndarray) -> Tuple[List[int], List[int]]:
        preds = np.argmax(predictions, axis=2)

        batch_size, seq_len = preds.shape

        out_label_list = [[] for _ in range(batch_size)]
        preds_list = [[] for _ in range(batch_size)]
        
        for i in range(batch_size):
            for j in range(seq_len):
                if label_ids[i, j] != nn.CrossEntropyLoss().ignore_index:
                    out_label_list[i].append(self.label_map[label_ids[i][j]])
                    preds_list[i].append(self.label_map[preds[i][j]])

        return preds_list, out_label_list
    
    '''
    def prepare(self,TheSentence):
        
        newSetence = self.TokenizadorFrases.tokenize(TheSentence)
        
        
        f = open("mytest/test.txt", "w")
        for s in newSetence:
            f.write(s+' O\n')
        f.close()


      '''  
        
    
    def predict(self, text):
        
        newSetence = self.TokenizadorFrases.tokenize(text)
        
        ## ejecucion
        
       
        
        directory= self.CorpusPath #'mytest/'
        test_dataset = MyNerDataset(
            data_dir=directory,
            tokens=newSetence,
            tokenizer=self.tokenizer,#,
            labels=self.labels,
            model_type=self.Config.model_type,
            max_seq_length=128,
            overwrite_cache=True,
            mode=Split.test,
        )
        
        predictions, label_ids, metrics = self.Trainer.predict(test_dataset)
        
        
        
        preds_list, outlist = self.align_predictions(predictions, label_ids)
        
        
        return newSetence, preds_list[0]
  
    def initModel(self):
        
        #directory= 'mytest/'
        labels= 'labels.txt'
        
        modelPath= self.ModelPath    #  'NCBI-disease/'
        output_dir=self.CorpusPath 
        
        
        labels = get_labels(labels)
        self.labels=labels
        self.label_map: Dict[int, str] = {i: label for i, label in enumerate(labels)}
        self.num_labels = len(labels)
        
        
        ##### Frases

        
        
        
        self.Config = AutoConfig.from_pretrained(
            modelPath,#model_args.config_name if model_args.config_name else model_args.model_name_or_path,
            num_labels=self.num_labels,
            id2label=self.label_map,
            label2id={label: i for i, label in enumerate(self.labels)},
            cache_dir=None, #model_args.cache_dir,
            )
        
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            modelPath,#model_args.tokenizer_name if model_args.tokenizer_name else model_args.model_name_or_path,
            cache_dir=None,#model_args.cache_dir,
            use_fast=False,    #model_args.use_fast,
            )
        
        
        model = AutoModelForTokenClassification.from_pretrained(
                modelPath,
                from_tf=bool(".ckpt" in modelPath),
                config=self.Config,
                cache_dir=None,
            )
        
        
        #TrainingArguments(output_dir='mytest/res', overwrite_output_dir=False, do_train=False, do_eval=False, do_predict=True, evaluate_during_training=False, per_device_train_batch_size=8, per_device_eval_batch_size=8, per_gpu_train_batch_size=None, per_gpu_eval_batch_size=None, gradient_accumulation_steps=1, learning_rate=5e-05, weight_decay=0.0, adam_epsilon=1e-08, max_grad_norm=1.0, num_train_epochs=3.0, max_steps=-1, warmup_steps=0, logging_dir='runs/Mar29_13-47-29_1143a78f5f8c', logging_first_step=False, logging_steps=500, save_steps=500, save_total_limit=None, no_cuda=False, seed=42, fp16=False, fp16_opt_level='O1', local_rank=-1, tpu_num_cores=None, tpu_metrics_debug=False, dataloader_drop_last=False)
        tfa = TrainingArguments( output_dir=output_dir, overwrite_output_dir=False, do_train=False, do_eval=False, do_predict=True,evaluate_during_training=False,   per_device_train_batch_size=8, per_device_eval_batch_size=8, per_gpu_train_batch_size=None, per_gpu_eval_batch_size=None, gradient_accumulation_steps=1, learning_rate=5e-05, weight_decay=0.0, adam_epsilon=1e-08, max_grad_norm=1.0, num_train_epochs=3.0, max_steps=-1, warmup_steps=0, logging_dir='runs/Mar29_13-47-29_1143a78f5f8c', logging_first_step=False, logging_steps=500, save_steps=500, save_total_limit=None, no_cuda=False, seed=42, fp16=False, fp16_opt_level='O1', local_rank=-1, tpu_num_cores=None, tpu_metrics_debug=False, dataloader_drop_last=False)
        self.Trainer = Trainer(
                model=model,
                args=tfa,
                #train_dataset=None,
                #eval_dataset=None,
                #compute_metrics=None,
            )
        
        



##### Model
'''

NerModel = NERModel('myNer','NCBI-disease/','mytest/')

NerModel.initModel()

TheSentence= ('Clustering of missense mutations in the ataxia-telangiectasia gene in a sporadic T-cell leukaemia')



NerModel.predict(TheSentence)



TheSentence= ('I have head tumors')

#NerModel.prepare(TheSentence)

NerModel.predict(TheSentence)


#NerModel.predict(TheSentence)


'''


