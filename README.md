# PhishGuard

> PhishGuard is a local phishing-detection assistant that analyzes URLs using a combination of heuristics and a pre-trained ML model. It provides a Tkinter-based chatbot GUI for interactive URL checks and utilities for programmatic analysis.

## Features
- Interactive GUI chatbot for submitting URLs and receiving analysis (`main_gui.py`).
- Heuristic checks (SSL, domain age, keyword scanning) in `phishing_check.py`.
- ML-based prediction using a pre-trained model (`ml_model_runner.py`, `phishing_model.pkl`, `scaler.pkl`).
- Logging and feedback components to capture user interaction and results.

## Quick Start

1. Ensure you have Python 3.8+ installed.
2. Install the common dependencies (see Requirements). If you use PowerShell, run:

```powershell
python -m pip install -r requirements.txt
```

If there is no `requirements.txt`, install these packages manually:

```powershell
python -m pip install pandas scikit-learn joblib requests python-whois tldextract pillow
```

Note: `tkinter` is included with many Python distributions; on some platforms you may need to install it separately.

## Running the GUI

Launch the interactive chatbot GUI:

```powershell
python main_gui.py
```

The GUI accepts plaintext or URLs. To analyze a URL, paste it into the input and press Enter or the send button.

## Command-line / Script Usage

- Analyze a single URL with the heuristic analyzer:

```powershell
python phishing_check.py
# then enter a URL when prompted
```

- Run the ML predictor directly (uses `phishing_model.pkl` and `scaler.pkl`):

```powershell
python ml_model_runner.py
# then enter a URL when prompted
```

Programmatic prediction helper used by other modules:

```python
from ml_wrapper import predict_with_ml_script
predict_with_ml_script("http://example.com")
```

## Important Files
- `main_gui.py` — Tkinter GUI and frontend for user interaction.
- `chatbot_logic.py` — Chatbot flow, intent handling and orchestration of checks.
- `phishing_check.py` — Heuristic checks: SSL, domain age, keyword scanning, logging.
- `ml_model_runner.py` — Feature extraction and ML model inference using `phishing_model.pkl` and `scaler.pkl`.
- `ml_wrapper.py` — Small wrapper used to call the ML prediction from other modules.
- `phishing_model.pkl`, `scaler.pkl` — Pre-trained model files (required for ML predictions).
- `Dataset.csv`, `Phishing_Dataset.csv`, `cleaned_dataset.csv` — Local datasets found in the repo.
- `logs/` — Directory where runtime logs are stored.
- `utils.py`, `database.py`, `chatbot_logger.py`, `feedback_handler.py` — Helper modules for normalization, DB logging and feedback.

## Database
The project contains `database.py` and SQL usage in several modules. Configure the connection in `database.py` for your chosen backend. Depending on your DB (Postgres/MySQL), install the appropriate driver (e.g. `psycopg2-binary` or `mysql-connector-python`).

## Troubleshooting
- If ML prediction fails, verify `phishing_model.pkl` and `scaler.pkl` are present in the project root and compatible with the installed `scikit-learn`.
- SSL checks and WHOIS lookups can fail behind restrictive firewalls — those checks will gracefully fall back and log warnings.
- If `tkinter` GUI doesn't start, confirm your Python distribution includes `tkinter`.

## Development
- To retrain or update the ML model, prepare a training script that outputs `phishing_model.pkl` and `scaler.pkl` compatible with `ml_model_runner.py` feature order.
- Add unit tests around feature extraction (`ml_model_runner.extract_features_from_url`) and `phishing_check.analyze_url` for regression coverage.

## Contributing
Feel free to open issues or submit PRs. When contributing:
- Follow existing code style and naming conventions.
- Add tests for new features.

## License
See the repository `LICENSE` file at the project root for full license terms.

## Contact
For questions or to report issues, email the maintainer address included in the code comments or open an issue in the repository.
