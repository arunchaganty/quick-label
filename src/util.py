#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

def conll_parse(reader):
    """
    Parses a file in CONLL input, i.e.
    'TOKEN(<TAB>FEAT)+' for each token in a sentence, followed by a new line.
    """
    
    current = []
    for row in reader:
        # Handling.
        if len(row) == 0:
            if len(current)> 0:
                yield zip(*current)
            current = []
        else:
            current.append(row)
        # End logic
    if len(current) > 0:
        yield zip(*current)

def train_crf(train_file, template_file):
    """
    Train CRF
    """

# - start shell
#   - give an input file
#   - initialize a model (unless given).
#   - label using crf_test
#   - ask the user to correct the label
#     + is fully correct?
#     + else go through tokens in order to correct
#   - append to training data
#   - keep track of test score (give scores)
#   - update model 
# -- you can quit whenever.
# -- model relearns whenever (each iteration | then async).
