import numpy as np
from scipy.stats import norm
from matplotlib import pyplot as plt


def calc(norm, val):
    low = norm.cdf(val - 0.5)
    high = norm.cdf(val + 0.5)
    return high - low


gauss = norm(9.87, 3)
vals = np.zeros(30)

for i in range(1, 30):
    vals[i] = calc(gauss, i)


x = np.arange(30)
plt.title("selected lengths")
plt.xlabel("x axis caption")
plt.ylabel("y axis caption")
plt.plot(x, vals)
plt.show()
