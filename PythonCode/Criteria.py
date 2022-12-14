import numpy as np
from scipy.stats import norm


class SimpleGaussian:
    def __init__(self, mu, sigma):
        self.sigma = sigma
        self.mu = mu
        self.backup = np.ones((50)) * -1
        self.found = np.zeros((50))
        self.norm = norm(loc=mu, scale=sigma)

    def calc(self, val):
        low = self.norm.cdf(val - 0.5)
        high = self.norm.cdf(val + 0.5)
        return high - low

    def update(self, selected):
        lengths = np.zeros((50))
        length = len(selected)
        for i,s in enumerate(selected):
            if "value" not in s:
                print("token ", i, " doesnt have a value")
                print("token is:")
                print(s)
                quit()
            lengths[len(s["value"])] += 1
        for l in lengths:
            if l != 0:
                l = l / length
        self.found = lengths

    def get_score(self, tokens, i):
        scores = []
        for t in tokens:
            #print(t)
            if "value" in t:
                length = len(t["value"])
                if(length >= 50):
                    #print("ran into error in line", i, ": Value longer than 50")
                    #print("it will we given a score of -1")
                    #print(t["value"])
                    scores.append(-1.0)
                    continue
                if self.backup[length] == -1:
                    self.backup[length] = self.calc(length)
                    #if i % 1000 == 0 and i !=0:
                    #    print("score is: ", self.backup[length] - self.found[length])
                #if i % 1000 == 0 and i != 0:
                #    print("score is: ", self.backup[length] - self.found[length])
                #    print("length is: ", length)
                scores.append(self.backup[length] - self.found[length])
            else:
                scores.append(-1.0)

                #print("line ", i," token: ", t)
                #print("doesnt have a value")
        #if i % 1000 == 0 and i !=0:
        #    print("i is: ", i)
        #    print("scores are: ")
        #    print(scores)
        #    print()

        return scores
