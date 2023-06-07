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
            # if "value" not in s:
            #     print("token ", i, " doesnt have a value")
            #     print("token is:")
            #     print(s)
            #     quit()
            lengths[len(s["value"])] += 1
        for i in range(cutoff):
            if lengths[i] != 0:
                lengths[i] = lengths[i] / length
            assert lengths[i] < 1
        self.found = lengths

    def get_score(self, tokens, filetype):
        scores = []
        for t in tokens:
            #print(t)
            length = 0
            if filetype == "json":
                if "value" in t and t["type"] == "IdentifierToken":
                    length = len(t["value"])
                else:
                    scores.append(0.0)
                    continue
            elif filetype == "cs":
                length = len(t)
            elif filetype == "txt":
                if("<Identifier:" in t):
                    length = len(t[12:t.find(",")])
                else:
                    scores.append(0.0)
                    continue

            if length >= cutoff:
                scores.append(0.0)
                continue
            if self.backup[length] < 0:
                self.backup[length] = self.calc(length)
            assert self.backup[length] >= 0
            assert self.found[length] < 1
            assert self.backup[length] - self.found[length] > -1
            res = self.backup[length] - self.found[length]
            res += 0.5
            if res > 1:
                res = 1
            elif res < 0:
                res = 0
            scores.append(res)
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
    def __init__(self, dictionary1, dictionary2):
        self.dict1 = dictionary1.copy()
        self.dict2 = dictionary2.copy()
        self.updated_dict2 = dictionary2.copy()

    def update(self, selected):
        tempdict = self.dict2.copy()
        skipped = 0
        for token in selected:
            if token["type"] not in self.dict1:
                skipped += 1
                continue
            else:
                tempdict[self.dict1[token["type"]]] += 1
        total_tokens = len(selected) - skipped
        for val in tempdict:
            tempdict[val] = tempdict[val] / total_tokens
            tempdict[val] = self.dict[val] - tempdict[val]
        self.updated_dict2 = tempdict

    def get_score(self, tokens, filetype):
        scores = []
        for token in tokens:
            type = ""
            if filetype == "json":
                type = token["type"]
            elif filetype == "txt":
                if "<Identifier:" in token:
                    type = token[token.find(",")+1:-1]
                else:
                    scores.append(0.0)
                    continue
            if type not in self.dict1:
                scores.append(0.0)
            else:
                scores.append(self.updated_dict[self.dict1[type]])
        return scores