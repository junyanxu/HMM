import Quandl
import numpy
import pandas
import statsmodels.api as sm
from matplotlib import cm, pyplot as plt
from matplotlib.dates import YearLocator, MonthLocator
from hmmlearn.hmm import GaussianHMM


mytoken = "AJH1cx5c8ZxqTrtaZXHr"
start_date_string = '2008-01-01'
StockName = "AAPL"
data = Quandl.get("YAHOO/"+StockName,
                  trim_start=start_date_string,
                  authtoken=mytoken)
numOfHiddenState = 4

data["Return"] = data["Adjusted Close"].diff(1).shift(-2)/data["Adjusted Close"]
data["Return0"] = data["Adjusted Close"].diff(1).shift(-1)/data["Adjusted Close"]
data["Return1"] = data["Return0"].shift(1)
data["Return2"] = data["Return0"].shift(2)
data["Return3"] = data["Return0"].shift(3)
data["Return4"] = data["Return0"].shift(4)
data["Return5"] = data["Return0"].shift(5)
data = data.dropna()


X = data[["Return"+str(i) for i in range(1, 6)]].values
model = GaussianHMM(n_components=numOfHiddenState, covariance_type="diag", n_iter=1000).fit(X)

# Predict the optimal sequence of internal hidden state
hidden_states = model.predict(X)
print("Transition matrix")
print(model.transmat_)

print("Means and vars of each hidden state")
for i in range(model.n_components):
    print("{0}th hidden state".format(i))
    print("mean = ", model.means_[i])
    print("var = ", numpy.diag(model.covars_[i]))
    print()

fig, axs = plt.subplots(model.n_components, 3)
colours = cm.rainbow(numpy.linspace(0, 1, model.n_components))
for i, (ax, colour) in enumerate(zip(axs, colours)):
    # Use fancy indexing to plot data in each state.
    mask = hidden_states == i
    ax[0].plot_date(data.index[mask], data["Adjusted Close"][mask], ".-", c=colour)
    ax[0].set_title("{0}th hidden state".format(i))
    ax[0].grid(True)
    ax[1].hist(data["Return"][mask])
    ax[2].plot(data["Return"][mask].cumsum())

plt.show()
