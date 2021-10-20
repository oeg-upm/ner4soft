#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 15 10:51:02 2021

@author: Pablo
"""



from seqeval.metrics import classification_report
import logging
import os
import random
import sys


logging.basicConfig(format = '%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt = '%m/%d/%Y %H:%M:%S',
                    level = logging.INFO)
logger = logging.getLogger(__name__)



    


def ner_evaluation(y_true,  y_pred):
    '''
    

    Parameters
    ----------
    y_true : Array or Matrix
        y_true = [['O', 'O', 'O', 'B-MISC', 'I-MISC', 'I-MISC', 'O'], ['B-PER', 'I-PER', 'O']].
    y_pred : Array or Matrix
        y_pred = [['O', 'O', 'B-MISC', 'I-MISC', 'I-MISC', 'I-MISC', 'O'], ['B-PER', 'I-PER', 'O']]


    Returns
    -------
    Generates a file with precicion, recall, f1 and support .

    '''
    report = classification_report(y_true, y_pred,digits=4)
    #print(report)
    output_eval_file = os.path.join("./", "ner_eval_results.txt")
    #logger.info("\n%s", report)
    with open(output_eval_file, "w") as writer:
        logger.info("***** Eval results *****")
        logger.info("\n%s", report)
        writer.write(report)
        
