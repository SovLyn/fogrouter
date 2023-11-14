from matplotlib import pyplot as plt
import numpy as np

time=np.loadtxt("time")

plt.plot(time, color="cornflowerblue", label="time")
plt.axvline(x=0, linestyle="--", color="crimson", label="situation change")
plt.axvline(x=200, linestyle="--", color="crimson")
plt.axvline(x=400, linestyle="--", color="crimson")
plt.axvline(x=600, linestyle="--", color="crimson")
plt.axvline(x=800, linestyle="--", color="crimson")

print(np.average(time))
plt.ylabel("time (s)")
plt.xlabel("query number")
plt.legend()
plt.show()