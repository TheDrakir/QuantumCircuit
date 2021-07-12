import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
sns.set()
data=pd.DataFrame({'A':[1,4,5,2,5,6,3,5,6,3,3],
                 'B':[4,3,7,3,5,2,4,3,5,5,2],
                 'C':[5,8,9,3,5,7,3,5,3,4,4],
                 'D':[5,4,3,6,7,3,5,2,6,6,4],
                 'E':[4,5,7,3,6,3,2,4,5,2,1],
                 'F':[7,6,4,7,4,7,9,3,2,2,3],
                 'G':[4,5,2,5,8,9,1,2,4,4,3],
                 'H':[6,4,2,6,2,6,1,3,8,9,6],
                 'I':[4,3,5,2,7,8,3,4,2,5,3],
                 'J':[4,2,5,7,8,4,5,2,5,1,2],
                 'K':[4,5,8,2,3,1,4,5,8,3,2]})
f, ax = plt.subplots(figsize=(13,11))
sns.heatmap(data.corr(), annot=True, ax=ax)
ax.set_title('default')
plt.show()