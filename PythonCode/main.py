import json
import os
import Criteria
import numpy as np
from matplotlib import pyplot as plt
import time


# from python_utils import file_tqdm


def main():
    start_time = time.time()
    path_in = "python50k_eval.json"
    path_out = "output.json"
    criteria = [Criteria.SimpleGaussian(9.87, 3)]
    total_lengths = np.zeros(200)

    if os.path.exists(path_out):
        os.remove(path_out)

    selected = []
    skipped = 0
    skipped2 = 0
    skipped3 = 0
    types = [[], []]
    with open(path_in, "r") as f, open(path_out, "w") as fout:
        for i, line in enumerate(f):  # file_tqdm(f):
            token_ids = []
            tokens = []
            dp = json.loads(line.strip())
            if len(dp) < 3:
                skipped += 1
                continue
            for j, tok in enumerate(dp):

                if ("value" not in tok) or ("children" in tok):
                    continue

                if "value" not in tok:
                    print("somethings going very wrong in line: ", i, " index is: ", j)
                    print("length of dp is: ", len(dp))
                    print("tok is: ", tok)
                    quit()
                if len(tok["value"]) > np.size(total_lengths):
                    total_lengths = np.append(total_lengths, np.zeros(len(tok["value"]) - np.size(total_lengths) + 1))
                total_lengths[len(tok["value"])] += 1

                token_ids.append(j)
                tokens.append(tok)
            if len(tokens) == 0:
                skipped2 += 1
                continue
            total_scores = np.array([])
            for c in criteria:
                scores = np.array(c.get_score(tokens))
                if total_scores.shape != scores.shape:
                    total_scores = np.zeros(scores.shape)
                total_scores = total_scores + scores

            if np.max(total_scores) == -1.0:
                for t in tokens:
                    typ = t["type"]
                    if typ not in types[0]:
                        types[0].append(typ)
                        types[1].append(0)
                    types[1][types[0].index(typ)] += 1

                skipped3 += 1
                continue
            selected.append(tokens[np.argmax(total_scores)])
#            print(json.dumps(dp[0:token_ids[np.argmax(total_scores)] + 1]), file=fout)

            if i % 1000 == 0 and i != 0:
                print()
                print("finished ", i, " of ", 500000, " lines")
                print()
                print(skipped, " lines were skipped as they had less than 3 tokens")
                print(skipped2, "lines were skipped as no selection was possible")
                print(skipped3, "lines were skipped due to the best score being -1")

                for c in criteria:
                    c.update(selected)

        selected_lengths = np.array([])
        for s in selected:
            selected_lengths = np.append(selected_lengths, len(s["value"]))

        total_avg = 0
        total_num = 0
        for x in range(np.size(total_lengths) - 1):
            total_avg += total_lengths[x] * x
            total_num += total_lengths[x]
        total_avg /= total_num

        print()
        print("successfully executed program")
        print("it took ", time.time() - start_time, "seconds to run this program")
        print("selected has a length of: ", len(selected), " expected is a length of: ", 50000)
        print("average length of selected tokens is: ", np.average(selected_lengths))
        print("total average length was: ", total_avg)
        print("the types in skipped3 were: ")
        for x in range(len(types[0])):
            t = types[0][x]
            n = types[1][x]
            print(t, ": ", n)
        print("graph of lengths in selected:")
        print()
        print("length of seen tokens is: ", len(selected_lengths) + skipped + skipped2 + skipped3)
        highest = np.max(selected_lengths)
        x = np.arange(round(highest) + 1)
        y = np.zeros(round(highest) + 1)
        for s in selected_lengths:
            y[round(s)] += 1
        plt.title("selected lengths")
        plt.xlabel("x axis caption")
        plt.ylabel("y axis caption")
        plt.plot(x, y)
        plt.show()



if __name__ == "__main__":
    main()
