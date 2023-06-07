import json
import os
import Criteria
import numpy as np
from matplotlib import pyplot as plt
import time
import os.path
from os import path
import chardet
import multiprocessing
from threading import Lock

# from python_utils import file_tqdm

all_avg = []
token_avg = []
shorter_avg = []
longer_avg = []
count = 0

testDict1 = {
    "NamespaceSymbol" : "class",
    "NonErrorNamedTypeSymbol" : "class",
    "Parameternull" : "parameter",
    "ParameterSymbol": "parameter",
    "LocalSymbol" : "variable",
    "MethodSymbol" : "method",
    "FieldSymbol" : "field",
    "MethodSymbolnull" : "method",
    "PropertySymbolnull" : "method",
    "PropertySymbol" : "method",
    "TypeParameterSymbol" : "class",
    "NonErrorNamedTypeSymbolnull" : "class",
    "FieldSymbolnull" : "field"
}
testDict2 = {
    "class" : 0.9,
    "method" : 0.58,
    "parameter" : 0.8,
    "field" : 0.13,
    "variable" : 0.12
}

def folder(path_in, path_out, criteria, context_length = 1000, path_mid = ""):

    if not os.path.exists(path.join(path_out, path_mid)):
        os.mkdir(path.join(path_out, path_mid))
    cutoff = 0.55
    directory = path.join(path_in, path_mid)


    for file in os.listdir(directory):
        filename = path.join(directory, file)
        if filename[0] == '.':
            continue
        if path.isfile(filename):
            global count
            if count % 10000 == 0:
                print("processed ", count, " files.")

            count += 1
            singlefile(filename,path.join(path_out,path_mid,file), criteria, context_length)
        elif path.isdir(filename):
            print("recursively starting again with filepath: ", filename)
            folder(path_in, path_out, criteria, context_length, path_mid = path.join(path_mid,file))



def singlefile(path_in, path_outs, criteria, context_length, outlength = [-1], whole_line = False):
    filetype = ""
    total_lengths = np.zeros(200)
    target_length = outlength[0]
    current_file = 0
    cutoff = 0.55
    path_out = ""
    if isinstance(path_outs, str):
        path_out = path_outs
    else:
        path_out = path_outs[0]
    outtype = ""
    if path_out.endswith("txt"):
        outtype = "txt"
    elif path_out.endswith("json"):
        outtype = "json"
    if os.path.exists(path_out):
        os.remove(path_out)

    #selected = []
    types = [[], []]
    skipped = 0
    acceptance_rateL = 0.375
    acceptance_rateH = 0.425
    accepted_total = 0
    accepted = 0
    fout = open(path_out, "w")
    with open(path_in, "r") as f:
        for i, line in enumerate(f):  # file_tqdm(f):

            if target_length != -1 and accepted_total + accepted >= target_length:
                current_file += 1
                if current_file >= len(outlength):
                    break
                target_length = outlength[current_file]
                fout.close()
                path_out = path_outs[current_file]
                if path_out.endswith("txt"):
                    outtype = "txt"
                elif path_out.endswith("json"):
                    outtype = "json"
                if os.path.exists(path_out):
                    os.remove(path_out)
                fout = open(path_out, "w")


            if i % 1000 == 0 and i != 0:
                print()
                print("finished ", i, " lines")
                print()
                print("averaged: ", np.average(all_avg))
                print("token_avg is: ", np.average(token_avg))
                print("cutoff is: ", cutoff)
                print("acceptance_rate is: ", (accepted_total/i))
                print("for last 100 it is: ", (accepted/100))

            if i % 100 == 0 and i != 0:
                accepted_total += accepted
                high = False; low = False;
                if not (((accepted/100) > acceptance_rateL) or ((accepted_total/i) > acceptance_rateL)):
                    low = True
                if not (((accepted / 100) < acceptance_rateH) or ((accepted_total / i) < acceptance_rateH)):
                    high = True
                if low and not high:
                    cutoff -= 0.01
                elif high and not low:
                    cutoff += 0.01
                accepted = 0



            tokens = []
            dp = ""
            if path_in.endswith(".json"):
                filetype = "json"
                dp = json.loads(line.strip())
            elif path_in.endswith(".cs"):
                filetype = "cs"
                dp = line.split("\t")
            elif path_in.endswith(".txt"):
                filetype = "txt"
                dp = line.split(" ")

            if len(dp) < 3:
                if filetype == "json":
                    skipped += 1
                continue
            total_scores = score(dp, criteria, total_lengths, filetype)

            if len(total_scores) == 0:
                print("total_scores is empty")
                continue
            for tok in total_scores:
                if tok != 0:
                    token_avg.append(tok)

            if np.max(total_scores) == -1.0:
                for t in tokens:
                    typ = t["type"]
                    if typ not in types[0]:
                        types[0].append(typ)
                        types[1].append(0)
                    types[1][types[0].index(typ)] += 1

            if len(dp) < context_length or whole_line or not outtype == "txt":
                decision = shorter_decision(dp, total_scores, cutoff)
            else:
                decision = longer_decision(dp, total_scores, context_length, cutoff)

            if decision:
                accepted += 1
                #selected.append(decision)
                if filetype == "json":
                    print(json.dumps(decision), file=fout)
                elif filetype == "txt":
                    if outtype == "txt":
                        print(txtprint(decision),file=fout)
                    else:
                        print(jsonprint(decision, total_scores),file=fout)
    fout.close()
                #print(decision,file=fout)
        # if filetype == "json":
        #     print(json.dumps(selected), file=fout)
        # elif filetype == "cs":
        #     for l in selected:
        #         if isinstance(l, str):
        #             print("\t".join(l), file=fout)
        #             print("\n", file=fout)
        #         else:
        #             for l2 in l:
        #                 print("".join(l2), file=fout)
        #                 print("\n", file=fout)


        # print("average length of selected tokens is: ", np.average(selected_lengths))
        # print("total average length was: ", total_avg)
        # print("the types in skipped3 were: ")
        # for x in range(len(types[0])):
        #     t = types[0][x]
        #     n = types[1][x]
        #     print(t, ": ", n)
        # print("graph of lengths in selected:")
        # print()
        # print("length of seen tokens is: ", len(selected_lengths) + skipped + skipped2 + skipped3)
        # highest = np.max(selected_lengths)
        # x = np.arange(round(highest) + 1)
        # y = np.zeros(round(highest) + 1)
        # for s in selected_lengths:
        #     y[round(s)] += 1
        # plt.title("selected lengths")
        # plt.xlabel("x axis caption")
        # plt.ylabel("y axis caption")
        # plt.plot(x, y)
        # plt.show()

def txtprint(content):
    if not isinstance(content[0],str):
        for l in content:
            txtprint(l)
            return
    rem = "<Identifier:"
    newlist = [""] * len(content)
    for i in range(len(content)-1):
        t = content[i]
        if rem in t:
            t = t[len(rem):t.find(",")]
        newlist[i] = t
    outString = " ".join(newlist)
    return outString

def jsonprint(content, scores):
    pre = int(len(scores)*0.15)
    best = np.argmax(scores[pre:]) + pre
    inputstring = txtprint(content[:best])
    gtstring =  txtprint(content[best:])
    gtstring = gtstring[:gtstring.find(";")+1]
    tmp = {"input" : inputstring, "gt" : gtstring}
    return json.dumps(tmp)


def score(line, criteria, total_lengths, filetype):

    total_scores = np.zeros(len(line))
    for c in criteria:
        scores = np.array(c.get_score(line, filetype))
        total_scores += scores
    return total_scores




def shorter_decision(line, scores, cutoff):
    sequence_score = 0
    non_zeroes = 0
    for i in range(len(scores)):
        if scores[i] != 0:
            sequence_score += scores[i]
            non_zeroes += 1
    if non_zeroes != 0:
        avg_score = sequence_score / non_zeroes
    else:
        return []
    all_avg.append(avg_score)
    shorter_avg.append(avg_score)
    if avg_score > cutoff:
        return line
    else:
        return []

def longer_decision(line, scores, context_length, cutoff):
    sequence_score = 0
    zeroes = 0
    for i in range(context_length):
        sequence_score += scores[i]
        if scores[i] == 0:
            zeroes += 1
    assert zeroes >= 0
    assert zeroes < context_length
    avg_score = sequence_score / (context_length - zeroes)
    avg_scores = [avg_score]

    lower_end = 1
    for i in range(context_length, len(scores)):
        assert (i - lower_end) == context_length-1
        sequence_score -= scores[lower_end-1]
        sequence_score += scores[i]
        if scores[i] == 0:
            zeroes += 1
        elif scores[lower_end-1] == 0:
            zeroes -= 1
        if zeroes < context_length:
            avg_score = sequence_score / (context_length - zeroes)
            avg_scores.append(avg_score)
        else:
            avg_scores.append(0)
        lower_end += 1
    all_avg.append(np.average(avg_scores))
    longer_avg.append(np.average(avg_scores))
    selected = greedy_select(avg_scores, context_length, cutoff, 0,  len(avg_scores))
    seqs = []
    for s in selected:
        salt = s + 1000
        seqs.append(line[salt-context_length:salt])

    return seqs


def greedy_select(scores, context_length, cutoff, lbound, hbound):
    if lbound >= hbound:
        return []
    highest = lbound + np.argmax(scores[lbound:hbound])
    if highest < cutoff:
        return []

    lower = highest - context_length
    upper = highest + context_length
    selected = []
    if lower > lbound:
        selected += greedy_select(scores, context_length, cutoff, lbound, lower)
    selected.append(highest)
    if upper < hbound:
        selected += greedy_select(scores, context_length, cutoff, upper, hbound)
    return selected


def valid_subtree(tree):
    return True


cont = 1000
if __name__ == "__main__":
    context_length = 1000
    start_time = time.time()
    _in_ = "D:\\large_files\\400k.txt"
    #_out_ = "outputCs.txt"
    _out_ = ["train.txt", "dev.txt", "dev.json" ,"test.json"]
    _outlength_ = [95000, 5000, 5000, 45000]
    if path.isfile(_in_):
        crit = [Criteria.SimpleGaussian(14.31, 3), Criteria.TokenTypes(testDict1, testDict2)]
        singlefile(_in_, _out_, crit, context_length, _outlength_)
    else:
        crit = [Criteria.SimpleGaussian(14.31, 3)]
        folder(_in_, _out_, crit)
    print("it took ", time.time() - start_time, "seconds to run this program")