# Wallet Risk Scoring From Scratch

## Overview
This project analyzes a list of Ethereum wallet addresses and assigns each a risk score (0-1000) based on their on-chain transaction history, with a focus on lending protocol activity (Compound V2/V3). The workflow is fully automated in Python.

## How It Works
1. **Data Collection**
   - Fetches all normal transactions for each wallet using the Etherscan API.
   - (For production, you should use Compound-specific contract events for more precise protocol activity.)

2. **Feature Engineering**
   - **num_txns**: Total number of transactions (proxy for activity/experience).
   - **avg_value**: Average value per transaction (for further analysis, not directly used in scoring).
   - **failed_txns**: Number of failed transactions (proxy for risky/failed actions).
   - **unique_contracts**: Number of unique contracts interacted with (proxy for protocol diversity).

3. **Risk Scoring**
   - Features are normalized across all wallets.
   - Score formula: `Score = 1000 * (0.5 * norm_txns + 0.3 * norm_failed + 0.2 * norm_unique)`
   - Lower number of txns and unique contracts, and higher failed txns, increase risk (lower score).
   - Score is clipped to [0, 1000].

4. **Output**
   - Results are saved to `wallet_risk_scores.csv` (columns: wallet_id, score).
   - A brief explanation of the methodology is saved to `brief_explanation.txt`.

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Place your Etherscan API key in the `API_KEY` variable in `main.py`.
3. Add wallet addresses (one per line) to `wallets.txt`.
4. Run the script:
   ```bash
   python main.py
   ```
5. Check the output files: `wallet_risk_scores.csv` and `brief_explanation.txt`.

## Files
- `main.py`: Main script for data collection, feature extraction, and scoring.
- `wallets.txt`: List of wallet addresses to analyze.
- `wallet_risk_scores.csv`: Output file with risk scores.
- `brief_explanation.txt`: Explanation of methodology and scoring logic.
- `requirements.txt`: Python dependencies.

## Notes
- The current implementation uses Etherscan's normal transaction API for demonstration. For production, use Compound protocol event logs for more accurate risk assessment.
- The scoring model is simple and interpretable, and can be extended with more protocol-specific features as needed.
