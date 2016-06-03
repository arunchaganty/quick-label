#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRF container
"""

import os
import sys
import subprocess
from subprocess import check_output, check_call
from util import sentence_to_conll, annotate_sentence
from settings import CRF_LEARN, CRF_TEST, WORK_DIR, MODEL_PATH, TEMPLATE_PATH, TRAIN_PATH

class CRF(object):
    """
    Routines to train a CRF labeller.
    """

    def __init__(self):
        self.train_path = open(TRAIN_PATH, "a")

    def update(self, sentence, tags):
        """
        Update the training data with this sentence and these gold tags.
        """
        for token, tag in zip(sentence["tokens"], tags):
            token["_tag"] = tag
        sentence_to_conll(self.train_path, sentence)
        self.train_path.write("\n")
        self.train_path.flush()

    def infer(self, sentence):
        """
        Uses the JAVANLP sentence object to create an appropriate CoNLL formatted input for the CRF
        """
        TEST_PATH = os.path.join(WORK_DIR, "test.input")
        with open(TEST_PATH, "w") as f:
            sentence_to_conll(f, sentence)

        output = check_output([CRF_TEST, "-m", MODEL_PATH, TEST_PATH], universal_newlines=True)
        output = [x.strip() for x in output.split("\n")]

        n_tokens = len(sentence["tokens"])
        tags = [output[2*i+1] for i in range(n_tokens)] # Every odd line is the tag.
        return tags

    def retrain(self):
        """
        Retrain model
        """
        check_call([CRF_LEARN, TEMPLATE_PATH, TRAIN_PATH, MODEL_PATH], stdout=subprocess.DEVNULL)
        return True

def do_command(args):
    model = CRF()

    for line in args.input:
        sentence = annotate_sentence(line)
        tags = model.infer(sentence)
        print(tags)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser( description='' )
    parser.add_argument('--input', type=argparse.FileType('r'), default=sys.stdin, help="")
    parser.add_argument('--output', type=argparse.FileType('w'), default=sys.stdout, help="")
    parser.set_defaults(func=do_command)

    #subparsers = parser.add_subparsers()
    #command_parser = subparsers.add_parser('command', help='' )
    #command_parser.set_defaults(func=do_command)

    ARGS = parser.parse_args()
    ARGS.func(ARGS)
