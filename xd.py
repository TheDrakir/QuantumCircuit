import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from matplotlib import rc
# rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
# ## for Palatino and other serif fonts use:
# #rc('font',**{'family':'serif','serif':['Palatino']})
# rc('text', usetex=True)
plt.rc('text', usetex=True)
fig = plt.figure(figsize=(7, 1))
text = fig.text(0.5, 0.5, "Hello", color='black', size=30)
plt.show()