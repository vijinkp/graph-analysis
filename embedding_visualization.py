import pandas as pd
from sklearn.manifold import TSNE
from ggplot import *
from matplotlib import pyplot as plt

data = pd.read_csv('emb/2010_4.emb', skiprows=1, header=None, sep=' ')
tsne = TSNE(n_components=2, verbose=1, perplexity=40, n_iter=300)
tsne_results = tsne.fit_transform(data[[x for x in range(1,129)]].values)

labels = data[0].values
X = tsne_results[:,0]
Y = tsne_results[:,1]

fig, ax = plt.subplots()
ax.scatter(X, Y)

for i, txt in enumerate(labels):
    ax.annotate(txt, (X[i], Y[i]))

