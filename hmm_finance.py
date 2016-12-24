import Quandl
import numpy
import pandas
import statsmodels.api as sm
from scipy import stats
from matplotlib import cm, pyplot as plt
from matplotlib.dates import YearLocator, MonthLocator
from hmmlearn.hmm import GaussianHMM


mytoken = "AJH1cx5c8ZxqTrtaZXHr"
start_date_string = '2004-01-01'
StockName = "AAPL"
data = Quandl.get("LBMA/GOLD",
                  collapse="daily",
                  trim_start=start_date_string,
                  authtoken=mytoken)

def getTrendR(line):
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        range(len(line)),line)
    return r_value


numOfHiddenState = 4
futureReturnPeriod = 1

data["Return"] = data["USD (AM)"].diff(futureReturnPeriod).shift(-futureReturnPeriod)/data["USD (AM)"]
data["Return0"] = data["USD (AM)"].diff(1).shift(-1)/data["USD (AM)"]
data["Return1"] = data["Return0"].shift(1)
data["Return2"] = data["Return0"].shift(2)
data["Return3"] = data["Return0"].shift(3)
data["Return4"] = data["Return0"].shift(4)
data["Return5"] = data["Return0"].shift(5)
data["5R"] = pandas.rolling_apply(data['USD (AM)'], 5, getTrendR)
data["10R"] = pandas.rolling_apply(data['USD (AM)'], 10, getTrendR)
data["20R"] = pandas.rolling_apply(data['USD (AM)'], 20, getTrendR)
data = data.dropna()


X = data[[
    "5R",
    "10R",
    "20R"
    ]].values

model = GaussianHMM(n_components=numOfHiddenState, covariance_type="diag", n_iter=1000).fit(X)
# Predict the optimal sequence of internal hidden state
hidden_states = model.predict(X)
print("Transition matrix")
print(model.transmat_)


print("Means and vars of each hidden state")
for i in range(model.n_components):
    print("{0}th hidden state".format(i))
    if(all(model.means_[i]>0)):
        up_component = i
    if model.means_[i][0]>0 and model.means_[i][-1] <0:
        rev_component = i
    if(all(model.means_[i]<0)):
        down_component = i
    print("mean = ", model.means_[i])
    print("var = ", numpy.diag(model.covars_[i]))
    print()

fig, axs = plt.subplots(model.n_components, 3)
colours = cm.rainbow(numpy.linspace(0, 1, model.n_components))

for i, (ax, colour) in enumerate(zip(axs, colours)):
    # Use fancy indexing to plot data in each state.
    mask = hidden_states == i
    ax[0].plot_date(data.index[mask], data["USD (AM)"][mask], ".-", c=colour)
    ax[0].set_title("{0}th hidden state".format(i))
    ax[0].grid(True)
    ax[1].hist(data["Return"][mask], bins=30)
    ax[1].set_xlim([-0.1, 0.1])
    ax[1].set_title("future return distrbution at {0}th hidden state".format(i))
    ax[2].plot(data["Return"][mask].cumsum())
    ax[2].set_title("cummulative future return at {0}th hidden state".format(i))
plt.show()

fig, axe = plt.subplots(1, 1)
data["hidden_states"] = hidden_states

def position_apply(x):
    if x== up_component or x== rev_component:
        return 1
    elif x == down_component:
        return -1
    else:
        return 0

position = data["hidden_states"].apply(position_apply)
res = pandas.DataFrame(
    {"Cum PNL":(data["Return"]*position).cumsum(),
     "Gold Price": data["USD (AM)"],
     "Position":position*0.3
    })

res.plot(ax=axe, secondary_y="Gold Price")
axe.set_title("cumulative return using hidden states as indicator")
axe.set_ylabel("return in %")
plt.show()
