import numpy as np
from scipy.stats import norm

cutoff = 40


class SimpleGaussian:
    def __init__(self, mu, sigma):
        self.backup = np.ones(cutoff) * -1
        self.found = np.zeros(cutoff)
        self.norm = norm(loc=mu, scale=sigma)

    def calc(self, val):
        low = self.norm.cdf(val - 0.5)
        high = self.norm.cdf(val + 0.5)
        return high - low

    def update(self, selected):
        lengths = np.zeros(cutoff)
        length = len(selected)

        for i, s in enumerate(selected):
            if "value" not in s:
                print("token ", i, " doesnt have a value")
                print("token is:")
                print(s)
                quit()
            lengths[len(s["value"])] += 1
        for i in range(cutoff):
            if lengths[i] != 0:
                lengths[i] = lengths[i] / length
            assert lengths[i] < 1
        self.found = lengths

    def get_score(self, tokens):
        scores = []
        for t in tokens:
            # print(t)
            if "value" in t:
                length = len(t["value"])
                if length >= cutoff:
                    scores.append(-1.0)
                    continue
                if self.backup[length] < 0:
                    self.backup[length] = self.calc(length)
                assert self.backup[length] >= 0
                assert self.found[length] < 1
                assert self.backup[length] - self.found[length] > -1
                scores.append(self.backup[length] - self.found[length])
            else:
                scores.append(-1.0)

        return scores


class PrioLater:
    def __init__(self, avg):
        self.avg = avg

    def update(self, selected):
        return
    def get_score(self, tokens):
        length = len(tokens)
        scores = []
        for tok in tokens:
            scores.append(len(tok["value"])/length)
        return scores

class TokenTypes:
    def __init__(self, dictionary):
        self.dict = dictionary.copy()
        self.updated_dict = dictionary.copy()

    def update(self, selected):
        tempdict = self.dict.copy()
        skipped = 0
        for token in selected:
            if token["type"] not in tempdict:
                skipped += 1
                continue
            else:
                tempdict[token["type"]] += 1
        total_tokens = len(selected) - skipped
        for val in tempdict:
            tempdict[val] = tempdict[val] / total_tokens
            tempdict[val] = self.dict[val] - tempdict[val]
        self.updated_dict = tempdict

    def get_score(self, tokens):
        scores = []
        for token in tokens:
            if token["type"] not in self.dictionary:
                scores.append(-1)
            else:
                scores.append(self.updated_dict[token["type"]])
        return scores