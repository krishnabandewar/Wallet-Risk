# Wallet Risk Scoring from Scratch
# Author: GitHub Copilot
#
# This script fetches Compound V2/V3 transaction data for a list of wallet addresses,
# extracts features, and assigns a risk score (0-1000) to each wallet.
#
# Requirements:
#   - Python 3.8+
#   - requests, pandas, tqdm
#
# Usage:
#   1. Place your API key in the API_KEY variable.
#   2. Add wallet addresses to 'wallets.txt' (one per line).
#   3. Run: python main.py
#   4. Output: 'wallet_risk_scores.csv' and 'risk_scoring_explanation.txt'

import requests
import pandas as pd
from tqdm import tqdm
import time

API_KEY = "7CYNPAAXYBYRBVWQGVZBA1SK4M6YKKQXDA"
ETHERSCAN_API = "https://api.etherscan.io/api"
COMPOUND_EVENTS = [
    # Add Compound V2/V3 contract addresses and event signatures as needed
    # For demo, we use generic ERC20 transfer events as a placeholder
    # In production, use Compound's Comptroller, cToken, etc. contract addresses
]

# Load wallet addresses from file
with open("wallets.txt") as f:
    WALLET_ADDRESSES = [line.strip() for line in f if line.strip()]

def fetch_transactions(address):
    # Fetch normal transactions (for demo; replace with Compound-specific events for production)
    url = f"{ETHERSCAN_API}?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey={API_KEY}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return []
    data = resp.json()
    if data.get("status") != "1":
        return []
    return data["result"]

def extract_features(txns):
    # Example features: number of txns, avg value, failed txns, unique contracts interacted
    if not txns:
        return {
            "num_txns": 0,
            "avg_value": 0,
            "failed_txns": 0,
            "unique_contracts": 0,
        }
    num_txns = len(txns)
    values = [int(tx["value"]) for tx in txns]
    avg_value = sum(values) / num_txns if num_txns else 0
    failed_txns = sum(1 for tx in txns if tx["isError"] == "1")
    unique_contracts = len(set(tx["to"] for tx in txns if tx["to"]))
    return {
        "num_txns": num_txns,
        "avg_value": avg_value,
        "failed_txns": failed_txns,
        "unique_contracts": unique_contracts,
    }

def normalize_feature(val, min_val, max_val):
    if max_val == min_val:
        return 0.5
    return (val - min_val) / (max_val - min_val)

def score_wallet(features, feature_stats):
    # Example scoring: more txns, more unique contracts = lower risk; more failed txns = higher risk
    norm_txns = 1 - normalize_feature(features["num_txns"], feature_stats["num_txns"][0], feature_stats["num_txns"][1])
    norm_failed = normalize_feature(features["failed_txns"], feature_stats["failed_txns"][0], feature_stats["failed_txns"][1])
    norm_unique = 1 - normalize_feature(features["unique_contracts"], feature_stats["unique_contracts"][0], feature_stats["unique_contracts"][1])
    # Weighted sum (tune as needed)
    score = 1000 * (0.5 * norm_txns + 0.3 * norm_failed + 0.2 * norm_unique)
    return int(max(0, min(1000, score)))

def main():
    all_features = []
    print("Fetching transactions for wallets...")
    for addr in tqdm(WALLET_ADDRESSES):
        txns = fetch_transactions(addr)
        features = extract_features(txns)
        features["wallet_id"] = addr
        all_features.append(features)
        time.sleep(0.2)  # Etherscan rate limit
    df = pd.DataFrame(all_features)
    # Compute min/max for normalization
    feature_stats = {
        col: (df[col].min(), df[col].max()) for col in ["num_txns", "failed_txns", "unique_contracts"]
    }
    df["score"] = df.apply(lambda row: score_wallet(row, feature_stats), axis=1)
    df[["wallet_id", "score"]].to_csv("wallet_risk_scores.csv", index=False)
    # Write explanation
    with open("risk_scoring_explanation.txt", "w") as f:
        f.write(EXPLANATION)
    print("Done. Results saved to 'wallet_risk_scores.csv' and 'risk_scoring_explanation.txt'.")

EXPLANATION = """
Data Collection:
- Used Etherscan API to fetch all normal transactions for each wallet address.
- (For production, use Compound-specific contract events for more precise protocol activity.)

Feature Selection:
- num_txns: Total number of transactions (proxy for activity/experience).
- avg_value: Average value per transaction (not directly used in score, but available for further analysis).
- failed_txns: Number of failed transactions (proxy for risky/failed actions).
- unique_contracts: Number of unique contracts interacted with (proxy for protocol diversity).

Scoring Method:
- Features are normalized across all wallets.
- Score = 1000 * (0.5 * norm_txns + 0.3 * norm_failed + 0.2 * norm_unique)
- Lower number of txns and unique contracts, and higher failed txns, increase risk (lower score).
- Score is clipped to [0, 1000].

Justification:
- More active wallets with diverse protocol interactions and fewer failed txns are considered lower risk.
- The model is simple, interpretable, and can be extended with more protocol-specific features.
"""

if __name__ == "__main__":
    main()
