# -*- coding: utf-8 -*-
import json

PATH = 'wago.121808.pn'
with open(PATH) as fd:
    wago_dict = {}
    for line in fd:
        try:
            polarity, word = line.rstrip().split('\t')
        except:
            continue
        wago_dict[word] = polarity
json.dump(wago_dict, open('pn_wago.json', 'w'))