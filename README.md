# Binance BTC Normalized Funding Rate

This Python script fetches **Bitcoin price** and **funding rate data** from Binance, applies **quantile normalization** to the funding rate, and plots it alongside the BTC price. The script highlights extreme values (overbought and oversold conditions) where the normalized funding rate exceeds ±2 standard deviations (Z > 1.96 or Z < -1.96).

# How does it work?

Binanace alongside Bybit are the two main exchanges for retail traders in the crypto market. Unlike tradional markets crypto has an instrument known as `perpetual futures`, which are futures contracts that don't expire. Futures in the stock market have the borrowing cost embedded within the price of the asset at expiry. Since there is no expiry funding represents the borrowing cost for traders to open a long or a short position. This borrowing cost is usually set to stablize the price difference between the perpetual market and the spot market.

Specifically, funding is calculated as:
Funding = Interest Rate + Premium Index

The Interest rate on Binance is fixed at 0.03% a day. The Premium index represents the dislocation between the perpetual market and the spot market. If the perpetual markets are trading at a higher price than the spot market then the Premium index is positive and the funding rate increases(traders positioned long have to pay more in borrowing costs and traders positioned short recieve money instead of paying borrowing costs.) Conversely if the perpetual martket is at a discount, at a sufficient enough difference, traders positioned long recieve money in the form of interest and short traders must pay a borrowing cost.

Observing past behaviour traders typically take on more risk the more one directional the market gets. I.e. if BTC has been trending up with minimal pullbacks traders get positioned more aggressively long and vice-versa. 

The point of this script is to identify regions in which the funding rate is either too high or too low to be sustainable. If funding is too high and traders are positioned too aggressively long any pullback will cause a liquidation cascade to the downside and if funding is too low and traders are positioned too aggresively short any bounce will cause a 'short squeeze'.

Funding data is normalized so that the overbought and oversold zones can easily be marked at 2 standard deviations from the mean.

Below is the result as per the start of 2025: 

![image](https://github.com/user-attachments/assets/6274970b-fedb-42b9-a828-adde1ee292d8)

---

## **Features**
1. Fetches **BTC price** and **funding rate data** from Binance's public APIs.
2. Applies **quantile normalization** to the funding rate for better statistical analysis.
3. Highlights overbought (red) and oversold (green) areas based on a Z-score threshold of ±2.
4. Outputs a clear dual-axis plot of BTC price (orange) and normalized funding rate (blue).

---

## **Requirements**
- **Python Version**: Python 3.6 or higher.
- **Libraries**:
  - `requests`: For API calls to Binance.
  - `pandas`: For data manipulation.
  - `matplotlib`: For plotting graphs.
  - `scikit-learn`: For quantile normalization.

---

## **Installation**

### **macOS and Windows**
1. **Install Python**:
   - **macOS**:
     ```bash
     brew install python
     ```
   - **Windows**:
     Download and install Python from the [official website](https://www.python.org/).

2. **Install the required Python libraries**:
   ```bash
   pip install requests pandas matplotlib scikit-learn
   ```

3. **Run the script**:
- Open command prompt or the terminal and enter the following commands:
```
git clone https://github.com/Lux4J/BTC-Binance-Normalized-Funding-Rate.git

cd BTC-Binance-Normalized-Funding-Rate

python BTC_Normalized_Funding_Rate.py
```
