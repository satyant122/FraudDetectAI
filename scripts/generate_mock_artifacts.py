"""
Generate realistic mock artifacts for the FraudDetectAI dashboard.

This script creates:
  - data/processed/scored_transactions.parquet
  - reports/metrics/final_risk_scoring_report.json
  - reports/metrics/baseline_vs_graph_comparison.json

Run this when the PaySim dataset is unavailable, so the Streamlit dashboard
can display representative data without running the full ML pipeline.
"""

import json
import random
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def ensure_dir(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


# ---------------------------------------------------------------------------
# 1. scored_transactions.parquet
# ---------------------------------------------------------------------------

def generate_scored_transactions(n: int = 5000) -> pd.DataFrame:
    transaction_types = ["TRANSFER", "CASH_OUT", "PAYMENT", "DEBIT", "CASH_IN"]
    type_weights      = [0.25, 0.30, 0.25, 0.10, 0.10]

    fraud_prob = np.concatenate([
        np.random.beta(1.5, 15, size=int(n * 0.87)),   # mostly low-risk
        np.random.beta(5,   3,  size=int(n * 0.08)),   # medium risk
        np.random.beta(9,   2,  size=int(n * 0.05)),   # high risk
    ])
    fraud_prob = np.clip(fraud_prob[:n], 0.0, 1.0)
    np.random.shuffle(fraud_prob)

    threshold = 0.42
    predicted_fraud = (fraud_prob >= threshold).astype(int)

    def risk_band(p):
        if p < 0.30:  return "LOW"
        if p < 0.55:  return "MEDIUM"
        if p < 0.75:  return "HIGH"
        return "CRITICAL"

    amounts = np.random.exponential(scale=15_000, size=n).clip(1, 2_000_000)
    t_types = np.random.choice(transaction_types, size=n, p=type_weights)

    # actual fraud is correlated with high probability
    actual_fraud = ((fraud_prob > 0.60) & (np.random.rand(n) < 0.78)).astype(int)

    df = pd.DataFrame({
        "transaction_id":    [f"TXN{100_000 + i}" for i in range(n)],
        "type":              t_types,
        "amount":            np.round(amounts, 2),
        "oldbalanceOrg":     np.round(np.random.exponential(50_000, n), 2),
        "newbalanceOrig":    np.round(np.random.exponential(40_000, n), 2),
        "oldbalanceDest":    np.round(np.random.exponential(60_000, n), 2),
        "newbalanceDest":    np.round(np.random.exponential(70_000, n), 2),
        "isFraud":           actual_fraud,
        "fraud_probability": np.round(fraud_prob, 6),
        "predicted_fraud":   predicted_fraud,
        "risk_band":         [risk_band(p) for p in fraud_prob],
    })

    return df.sort_values("fraud_probability", ascending=False).reset_index(drop=True)


# ---------------------------------------------------------------------------
# 2. final_risk_scoring_report.json
# ---------------------------------------------------------------------------

def generate_risk_scoring_report(df: pd.DataFrame, threshold: float = 0.42) -> dict:
    return {
        "decision_threshold": threshold,
        "num_transactions_scored": len(df),
        "risk_band_counts": df["risk_band"].value_counts().to_dict(),
        "predicted_fraud_counts": {
            str(k): int(v) for k, v in df["predicted_fraud"].value_counts().to_dict().items()
        },
        "average_fraud_probability": round(float(df["fraud_probability"].mean()), 6),
        "max_fraud_probability":     round(float(df["fraud_probability"].max()), 6),
        "min_fraud_probability":     round(float(df["fraud_probability"].min()), 6),
        "actual_fraud_rate_by_risk_band": {
            band: round(float(df[df["risk_band"] == band]["isFraud"].mean()), 4)
            for band in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
            if band in df["risk_band"].values
        },
    }


# ---------------------------------------------------------------------------
# 3. baseline_vs_graph_comparison.json
# ---------------------------------------------------------------------------

def generate_comparison_report() -> dict:
    models = ["random_forest", "gradient_boosting", "logistic_regression"]

    def make_metrics(base_ap, boost=0.0):
        ap = round(base_ap + boost + random.uniform(-0.01, 0.01), 4)
        return {
            "precision":         round(ap - random.uniform(0.03, 0.08), 4),
            "recall":            round(ap - random.uniform(0.05, 0.12), 4),
            "f1":                round(ap - random.uniform(0.02, 0.06), 4),
            "roc_auc":           round(min(ap + random.uniform(0.05, 0.12), 0.99), 4),
            "average_precision": round(ap, 4),
        }

    base_aps   = {"random_forest": 0.81, "gradient_boosting": 0.78, "logistic_regression": 0.65}
    graph_bump = {"random_forest": 0.06, "gradient_boosting": 0.07, "logistic_regression": 0.05}

    baseline_models = {m: make_metrics(base_aps[m])              for m in models}
    graph_models    = {m: make_metrics(base_aps[m], graph_bump[m]) for m in models}

    def delta(b, g):
        abs_d = round(g - b, 4)
        rel_d = round((abs_d / b) * 100, 2) if b != 0 else 0.0
        return {"baseline": b, "graph_enhanced": g, "absolute_delta": abs_d, "relative_delta_percent": rel_d}

    metric_names = ["precision", "recall", "f1", "roc_auc", "average_precision"]

    model_comparisons = {
        m: {metric: delta(baseline_models[m][metric], graph_models[m][metric])
            for metric in metric_names}
        for m in models
    }

    best_baseline = max(models, key=lambda m: baseline_models[m]["average_precision"])
    best_graph    = max(models, key=lambda m: graph_models[m]["average_precision"])

    return {
        "comparison_basis": {
            "metric_names": metric_names,
            "primary_selection_metric": "average_precision",
        },
        "common_models": models,
        "best_baseline_model_by_average_precision": {
            "model_name": best_baseline,
            "metric_name": "average_precision",
            "score": baseline_models[best_baseline]["average_precision"],
        },
        "best_graph_model_by_average_precision": {
            "model_name": best_graph,
            "metric_name": "average_precision",
            "score": graph_models[best_graph]["average_precision"],
        },
        "model_comparisons": model_comparisons,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Generating mock artifacts for FraudDetectAI dashboard...")

    # 1. Scored transactions
    scored_path = PROJECT_ROOT / "data" / "processed" / "scored_transactions.parquet"
    df = generate_scored_transactions(n=5000)
    df.to_parquet(ensure_dir(scored_path), index=False)
    print(f"  [OK] Scored transactions  -> {scored_path.relative_to(PROJECT_ROOT)}  ({len(df):,} rows)")

    # 2. Risk scoring report
    risk_report_path = PROJECT_ROOT / "reports" / "metrics" / "final_risk_scoring_report.json"
    risk_report = generate_risk_scoring_report(df)
    with ensure_dir(risk_report_path).open("w") as f:
        json.dump(risk_report, f, indent=2)
    print(f"  [OK] Risk scoring report  -> {risk_report_path.relative_to(PROJECT_ROOT)}")

    # 3. Baseline vs graph comparison
    comparison_path = PROJECT_ROOT / "reports" / "metrics" / "baseline_vs_graph_comparison.json"
    comparison_report = generate_comparison_report()
    with ensure_dir(comparison_path).open("w") as f:
        json.dump(comparison_report, f, indent=2)
    print(f"  [OK] Comparison report    -> {comparison_path.relative_to(PROJECT_ROOT)}")

    print("\nAll mock artifacts generated successfully! Run `streamlit run app/streamlit_app.py` to view the dashboard.")


if __name__ == "__main__":
    main()
