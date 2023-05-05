import json
import os
from matplotlib import pyplot as plt
import time
import random


def main():
    start_time = time.time()
    path_in = "C:\\Users\\milan\\Desktop\\cleanerAsts.json"
    path_out = "SymbolTypes.txt"
    num_examples = 0
    tokentypes = {}
    tokenexamples = {}
    typename = "SymbolType"
    total_token_amount = 0
    with open(path_in, "r", encoding ="utf-8") as f, open(path_out, "w") as fout:
        for i, line in enumerate(f):

            dp = json.loads(line.strip())

            for token in dp:
                if (typename not in token):# or ("children" in token):
                    continue
                if token[typename] not in tokentypes:
                    tokentypes[token[typename]] = 1
                    if num_examples > 0:
                        tokenexamples[token[typename]] = []
                        tokenexamples[token[typename]].append([token[typename]])
                else:
                    tokentypes[token[typename]] += 1
                    if num_examples > 0 and len(tokenexamples[token[typename]]) < num_examples+1:
                        tokenexamples[token[typename]].append([token["value"]])
                    elif num_examples > 0:
                        rand1 = random.random()
                        if rand1 > 0.95:
                            rand2 = random.randint(0, num_examples-1)
                            tokenexamples[token[typename]][rand2] = [token["value"]]
                total_token_amount += 1
            #if i % 1000 == 0 and i != 0:
            print()
            print("finished ", i, " lines")
            print()

        for key in tokentypes:
            value = tokentypes[key]
            percentage = (value / total_token_amount) * 100
            print(key, ": ", value, " occurences making up ", percentage, "% of all tokens", file=fout)
            if num_examples > 0:
                for ind, example in enumerate(tokenexamples[key]):
                    print("\t", ind, ":", example, file=fout)


if __name__ == "__main__":
    main()
