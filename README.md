# Tennis Scanner Assistant

A working manual-input scanner and paper-trading assistant.

## What it does

- Checks the locked hard rules
- Returns TRADE, WAIT, or NO TRADE
- Calculates the 100-point Stability Score
- Applies price-adjusted thresholds
- Suggests 3%, 5%, or 7% bankroll sizing
- Saves recommendations and tracks results
- Includes beta read-only API Tennis and Polymarket data tabs

## What it does not do

- Place trades
- Access your wallet
- Store private keys
- Guarantee profit
- Automatically map every live tennis stat yet

## Fastest setup: GitHub + Streamlit

1. Download and unzip `tennis_scanner_assistant.zip`.
2. Create a free GitHub account.
3. Create a new **private** repository named `tennis-scanner-assistant`.
4. Open the repository, choose **Add file**, then **Upload files**.
5. Upload everything from inside the unzipped folder. Do not upload only the ZIP. `streamlit_app.py` must appear at the top level.
6. Commit the files.
7. Sign in to Streamlit Community Cloud with GitHub.
8. Choose **Create app**.
9. Select the repository and set the app file to `streamlit_app.py`.
10. Deploy. Open the resulting link on your iPhone.

## Optional API Tennis key

The main scanner works without a key. To use the beta live-feed tab, add this in Streamlit app settings under **Secrets**:

```toml
API_TENNIS_KEY = "paste-your-key-here"
```

Never upload an API key to GitHub.

## Important limitation

The free cloud app's local database can reset during restarts or redeployments. Download the paper log as CSV regularly. A later version should use a persistent hosted database.

## Local computer use

```bash
python -m venv .venv
pip install -r requirements.txt
streamlit run streamlit_app.py
```
