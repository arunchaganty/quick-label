#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contains the (static) settings for the file.
"""

import os

# Location of the binaries
ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
BIN_PATH = os.path.join(ROOT_DIR, "bin")
CRF_LEARN = os.path.join(BIN_PATH, "crf_learn")
CRF_TEST = os.path.join(BIN_PATH, "crf_test")

# JAVANLP setup
SERVER_URI = "localhost:9000"

#WORK_DIR = "workdir"
#TEMPLATE_PATH = os.path.join(WORK_DIR, "template")
#TRAIN_PATH = os.path.join(WORK_DIR, "train.conll")
#MODEL_PATH = os.path.join(WORK_DIR, "model")
#
#KEYS = {
#    's' : 'SPKR',
#    'j' : 'CTNT',
#    'k' : 'CUE',
#    'f' : 'O'
#    }

