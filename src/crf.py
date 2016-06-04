#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRF container
"""

import os
import subprocess
from subprocess import check_output, check_call
from util import write_conll, read_conll_doc
from settings import CRF_LEARN, CRF_TEST

class CRF(object):
    """
    Routines to train a CRF labeller.
    """

    def __init__(self, config):
        wd = config["paths"]["work_dir"]
        self.train_path = config["paths"]["train"]
        self.test_path = os.path.join(wd, "test.input")
        self.model_path = config["paths"]["model"]
        self.template_path = config["paths"]["template"]

    def infer(self, conll):
        """
        Uses the JAVANLP sentence object to create an appropriate CoNLL formatted input for the CRF
        """
        with open(self.test_path, "w") as f:
            write_conll(f, conll)

        output = check_output([CRF_TEST, "-m", self.model_path, self.test_path], universal_newlines=True)
        conll = read_conll_doc(output)
        assert len(conll) == 1
        conll = conll[0]

        tags = [tok[-1] for tok in conll]
        return tags

    def retrain(self):
        """
        Retrain model
        """
        check_call([CRF_LEARN, self.template_path, self.train_path, self.model_path], stdout=subprocess.DEVNULL)
        return True

def test_infer():
    """
    Test if the inference method works.
    """
    from configparser import ConfigParser
    from util import annotate_sentence
    config = ConfigParser()
    config.read_file(open('quotes.config'))

    model = CRF(config)

    line = 'Calderon praised Medina Mora for his "professionalism" which he said was "crucial for the procurement of justice and to strike at organized crime.'
    conll = annotate_sentence(line)
    tags = model.infer(conll)
    print(tags)

if __name__ == "__main__":
    test_infer()
