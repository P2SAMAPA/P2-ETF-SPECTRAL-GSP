# Spectral Graph Signal Processing (GSP) Engine

Applies graph Fourier transform to the ETF correlation graph. The graph Laplacian eigenvectors form a Fourier basis. Projecting the daily return vector onto low‑frequency eigenvectors extracts the systematic market‑wide signal. The low‑frequency reconstruction for each ETF is the score: higher positive values indicate strong alignment with the market → overweight signal.

- **Graph:** nodes = ETFs, edges = absolute correlation (> threshold)
- **Transform:** Graph Fourier via Laplacian eigenvectors
- **Score:** low‑frequency component (systematic market signal)
- **Windows:** 63, 252, 504, 1008, 2016 days (best per ETF)
- **Output:** top 3 ETFs per universe

Runs daily on GitHub Actions.

## Local execution

```bash
pip install -r requirements.txt
export HF_TOKEN=<your_token>
python trainer.py
streamlit run streamlit_app.py
