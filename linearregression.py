import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression

data = pd.read_csv('Coord.csv')
X = data.iloc[:,1].values.reshape(-1,1)
Y = data.iloc[:,2].values.reshape(-1,1)
lr = LinearRegression()
lr.fit(X,Y)
Y_pred = lr.predict(X)

plt.scatter(X,Y)
plt.plot(X, Y_pred, color='red')
plt.show()



print(X)

print(Y)


print(Y_pred)
