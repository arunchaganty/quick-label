#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The QuickLabel entry point 
"""

from crf import CRF
from edit_shell import EditShell
from util import annotate_sentence
from settings import KEYS

def do_command(args):
    model = CRF()

    for sent_raw in args.input:
        sent_raw.strip()

        sent = annotate_sentence(sent_raw)
        pretty_sentence = ["{}/{}".format(token["word"], token["pos"]) for token in sent["tokens"]]
        tags = model.infer(sent)
        with EditShell(KEYS) as shell:
            _, tags = shell.run(pretty_sentence, tags)
        model.update(sent, tags)
        model.retrain()

if __name__ == "__main__":
    import sys, argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--input', type=argparse.FileType('r'), default=sys.stdin, help="A file with a list of sequences to be labelled.")
    parser.add_argument('--output', type=argparse.FileType('w'), default=sys.stdout, help="Final output written in CONLL format.")
    parser.add_argument('--template', type=str, default='templates', help="Path to feature templates")
    parser.add_argument('--working-directory', type=str, default='working_directory', help="Directory to store intermediate files, etc.")
    parser.set_defaults(func=do_command)

    ARGS = parser.parse_args()
    ARGS.func(ARGS)
