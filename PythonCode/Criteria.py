import math

import numpy as np
from scipy.stats import norm

cutoff = 40


class SimpleGaussian:
    def __init__(self, mu, sigma):
        self.backup = np.ones(cutoff) * -1
        self.found = np.zeros(cutoff)
        self.foundNorm = np.zeros(cutoff)
        self.norm = norm(loc=mu, scale=sigma)
        self.base = np.zeros(cutoff)
        for i in range(1,cutoff):
            self.base[i] = self.calc(i)
        self.mean = mu
        self.counter = 0
        self.avg = 0

    def calc(self, val):
        low = self.norm.cdf(val - 0.5)
        high = self.norm.cdf(val + 0.5)
        return high - low

    def update(self, selected, filetype):
        lengths = np.zeros(cutoff)
        length = len(selected)
        sel_lengths = self.get_lengths(selected, filetype)
        all = 0
        total = 0
        for l in sel_lengths:
            # if "value" not in s:
            #     print("token ", i, " doesnt have a value")
            #     print("token is:")
            #     print(s)
            #     quit()
            if l < cutoff and l != 0:
                lengths[l] += 1
                all += 1
                total += l
        for i in range(cutoff):
            if lengths[i] != 0:
                lengths[i] = lengths[i] / length
            assert lengths[i] < 1
        self.counter += all
        for i in range(cutoff):
            self.found[i] *= (self.counter - all)/self.counter
            self.found[i] += lengths[i]/self.counter
        self.avg *= (self.counter - all)/self.counter
        self.avg += total/self.counter

        self.foundNorm = self.base - self.found
        if self.avg < self.mean:
            for i in range(math.ceil(self.avg), cutoff): self.foundNorm[i] += 0.25
        elif self.avg > self.mean:
            for i in range(1, math.floor(self.avg)): self.foundNorm[i] += 0.25

        highest = np.max(self.found)
        self.foundNorm *= (1/highest)
        self.backup = self.foundNorm

    def get_lengths(self, tokens, filetype):
        lengths = []
        for t in tokens:
            # print(t)
            length = 0
            if filetype == "json":
                if "value" in t and t["type"] == "IdentifierToken":
                    length = len(t["value"])
                else:
                    length.append(0)
                    continue
            elif filetype == "cs":
                length = len(t)
            elif filetype == "txt":
                if ("<Identifier:" in t):
                    length = len(t[12:t.find(",")])
                else:
                    lengths.append(0)
                    continue
            lengths.append(length)
        return lengths

    def get_score(self, tokens, filetype):
        scores = []
        lengths = self.get_lengths(tokens, filetype)
        for length in lengths:
            if length >= cutoff or length <= 0:
                scores.append(0.0)
                continue
            if self.backup[length] < 0:
                self.backup[length] = self.calc(length)
            assert self.backup[length] >= 0
            assert self.found[length] < 1
            #assert self.backup[length] - self.foundNorm[length] > -1
            res = self.backup[length]# - self.foundNorm[length]
            #res += 0.5
            if res > 1:
                res = 1
            elif res < 0:
                res = 0
            scores.append(res)
        return scores



class TokenTypes:
    def __init__(self, dictionary1, dictionary2):
        self.dict1 = dictionary1.copy()
        self.dict2 = dictionary2.copy()
        self.occurences_dict = dict.fromkeys(self.dict2,0)
        self.updated = self.dict2.copy()
        self.token_count = 0

    def update(self, selected, filetype):
        #print("am in update")
        tempdict = dict.fromkeys(self.dict2,0)
        skipped = 0
        types = self.get_types(selected, filetype)
        for type in types:
            if type not in self.dict1.keys():
                skipped += 1
                continue
            else:
                tempdict[self.dict1[type]] += 1

        total_tokens = len(selected) - skipped

        if total_tokens <= 0:
            return
        self.token_count += total_tokens
        for key in tempdict.keys():
            self.occurences_dict[key] *= (self.token_count - total_tokens) / self.token_count
            self.occurences_dict[key] +=tempdict[key] / self.token_count
        tmp2 = dict.fromkeys(self.dict2,0.0)
        sum = 0
        for key in tempdict.keys():
            tmp2[key] = self.dict2[key] - tempdict[key]
            if tmp2[key] <= 0.0:
                tmp2[key] = 0.0
            sum += tmp2[key]
        if sum == 0:
            #print("sum was 0")
            return
        for key in tmp2.keys():
            tmp2[key] = tmp2[key] / sum

        self.updated = tmp2

    def get_score(self, tokens, filetype):
        scores = []
        types = self.get_types(tokens,filetype)
        for t in types:
            if t not in self.dict1 or t == "":
                scores.append(0.0)
                #print(t)
            else:
                #print(self.updated[self.dict1[t]])
                scores.append(self.updated[self.dict1[t]])
        return scores

    def get_types(self, tokens, filetype):
        types = []

        for token in tokens:
            typestr = ""
            if filetype == "json":
                typestr = token["type"]
            elif filetype == "txt":
                if "<Identifier:" in token:
                    str = ",Symbol:"
                    typestr = token[token.find(str) + len(str):-1]
            types.append(typestr)
        return types
