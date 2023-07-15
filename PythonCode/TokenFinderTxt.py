import json
import os
from matplotlib import pyplot as plt
import time
import random


def main():
    start_time = time.time()
    path_in = "train.txt"
    path_out = "LonlySymbolTypes.txt"
    num_examples = 0
    tokentypes = {}
    tokenexamples = {}
    typename = "<Identifier:"
    symbolname = ",Symbol:"
    total_token_amount = 0
    avg_length = 0
    with open(path_in, "r", encoding ="utf-8") as f, open(path_out, "w") as fout:
        for i, line in enumerate(f):

            occurence = line.find(typename)

            while occurence != -1:
                endtok = line.find(">",occurence)
                symbol = line.find(symbolname,occurence,endtok)
                name = line[occurence+len(typename):symbol]
                token = line[symbol+len(symbolname):endtok]
                if token not in tokentypes:
                    tokentypes[token] = 1
                    if num_examples > 0:
                        tokenexamples[token] = []
                        tokenexamples[token].append([token])
                else:
                    tokentypes[token] += 1
                    if num_examples > 0 and len(tokenexamples[token]) < num_examples+1:
                        tokenexamples[token].append([name])
                    elif num_examples > 0:
                        rand1 = random.random()
                        if rand1 > 0.95:
                            rand2 = random.randint(0, num_examples-1)
                            tokenexamples[token][rand2] = [name]
                total_token_amount += 1
                avg_length *= (total_token_amount-1)/total_token_amount
                avg_length += len(name)/ total_token_amount
                occurence = line.find(typename,occurence+1)
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
        print("avg token length = ", avg_length, file=fout)


if __name__ == "__main__":
    main()
