import json
import os
from matplotlib import pyplot as plt
import time


def main():
    start_time = time.time()
    path_in = "python50k_eval.json"
    path_out = "tokentypes.txt"
    tokentypes = {}
    total_token_amount = 0
    with open(path_in, "r") as f, open(path_out, "w") as fout:
        for i, line in enumerate(f):
            dp = json.loads(line.strip())
            for token in dp:
                if ("value" not in token) or ("children" in token):
                    continue
                if token["type"] not in tokentypes:
                    tokentypes[token["type"]] = 1
                else:
                    tokentypes[token["type"]] += 1
                total_token_amount += 1
            if i % 1000 == 0 and i != 0:
                print()
                print("finished ", i, " of ", 500000, " lines")
                print()

        for key in tokentypes:
            value = tokentypes[key]
            percentage = (value / total_token_amount) * 100
            print(key, ": ", value, " occurences making up ", percentage, "% of all tokens", file=fout)


if __name__ == "__main__":
    main()
