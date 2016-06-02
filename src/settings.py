#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contains the global settings for the file.
"""

import os

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))

# Location of the binaries
BIN_PATH = os.path.join(ROOT_DIR, "bin")
CRF_LEARN = os.path.join(BIN_PATH, "crf_learn")
CRF_TEST = os.path.join(BIN_PATH, "crf_test")

# JAVANLP setup
JAVANLP_HOME = os.path.join(ROOT_DIR, 'deps', 'stanford-corenlp')

# Also update JAVANLP_HOME
os.environ.update(JAVANLP_HOME=JAVANLP_HOME)

