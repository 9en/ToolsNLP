# -*- coding: utf-8 -*-

import doctest
import ToolsNLP

if __name__ == "__main__":
    doctest.testmod(ToolsNLP.mecab_wrapper, verbose=True)
    doctest.testmod(ToolsNLP.topic_model, verbose=True)
