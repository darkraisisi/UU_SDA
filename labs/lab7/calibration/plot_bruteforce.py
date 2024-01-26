import matplotlib.pyplot as plt
import numpy as np

# t = np.loadtxt('bruteforce.txt')
l = np.loadtxt('bruteforce_last.txt')
# plt.plot(t[0],t[1], '-o', color='orange', label="year 2 & 3")
plt.plot(l[0],l[1], '-o', color='green', label="year 3")
plt.legend()
plt.show()