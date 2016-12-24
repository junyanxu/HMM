# XAUUSD HMM Trend Following Strategy

This is a strategy using linear regression across multiple time horizon as
indicators and Hidden Markov Model to detect the possible hidden state of the market.

Trend following strategy need to use assets which have high momentum. I choose
XAUUSD since the market has been driven most by fundamental investments. 

# Hidden state detecting result
![hidden states](decomp.png)

# Long Short Result Using Predicted Hidden State
![PNL](PNL.png)
