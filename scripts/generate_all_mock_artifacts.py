"""Generate ALL mock artifacts needed by every Streamlit dashboard page."""

import json
import random
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

ROOT = Path(__file__).resolve().parents[1]


def ensure(p: Path) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


# ── 0. data/processed/scored_transactions.parquet ────────────────────────
def gen_scored_transactions(n: int = 5000) -> Path:
    transaction_types = ["TRANSFER", "CASH_OUT", "PAYMENT", "DEBIT", "CASH_IN"]
    type_weights = [0.25, 0.30, 0.25, 0.10, 0.10]

    fraud_prob = np.concatenate([
        np.random.beta(1.5, 15, size=int(n * 0.87)),
        np.random.beta(5, 3, size=int(n * 0.08)),
        np.random.beta(9, 2, size=int(n * 0.05)),
    ])
    fraud_prob = np.clip(fraud_prob[:n], 0.0, 1.0)
    np.random.shuffle(fraud_prob)

    threshold = 0.42
    predicted_fraud = (fraud_prob >= threshold).astype(int)

    def get_risk_band(p):
        if p < 0.30: return "LOW"
        if p < 0.55: return "MEDIUM"
        if p < 0.75: return "HIGH"
        return "CRITICAL"

    amounts = np.random.exponential(scale=15_000, size=n).clip(1, 2_000_000)
    t_types = np.random.choice(transaction_types, size=n, p=type_weights)
    actual_fraud = ((fraud_prob > 0.60) & (np.random.rand(n) < 0.78)).astype(int)

    old_org = np.random.exponential(50_000, n)
    new_org = np.maximum(0, old_org - amounts)
    old_dest = np.random.exponential(60_000, n)
    new_dest = old_dest + amounts

    df = pd.DataFrame({
        "nameOrig": [f"C{100_000 + i}" for i in range(n)],
        "nameDest": [f"M{900_000 + (i % 850)}" if t == "PAYMENT" else f"C{200_000 + (i % 1200)}" for i, t in enumerate(t_types)],
        "type": t_types,
        "amount": np.round(amounts, 2),
        "oldbalanceOrg": np.round(old_org, 2),
        "newbalanceOrig": np.round(new_org, 2),
        "oldbalanceDest": np.round(old_dest, 2),
        "newbalanceDest": np.round(new_dest, 2),
        "origin_balance_delta": np.round(old_org - new_org, 2),
        "destination_balance_delta": np.round(new_dest - old_dest, 2),
        "amount_to_old_origin_balance_ratio": np.round(amounts / (old_org + 1.0), 4),
        "sender_out_degree": np.random.poisson(3, n) + 1,
        "receiver_in_degree": np.random.poisson(5, n) + 1,
        "receiver_incoming_fraud_rate": np.round(np.where(fraud_prob > 0.5, np.random.uniform(0.1, 0.8, n), np.random.uniform(0.0, 0.05, n)), 4),
        "sender_receiver_edge_fraud_rate": np.round(np.where(fraud_prob > 0.6, np.random.uniform(0.2, 0.9, n), 0.0), 4),
        "isFraud": actual_fraud,
        "fraud_probability": np.round(fraud_prob, 6),
        "predicted_fraud": predicted_fraud,
        "risk_band": [get_risk_band(p) for p in fraud_prob],
    })

    df = df.sort_values("fraud_probability", ascending=False).reset_index(drop=True)
    path = ROOT / "data/processed/scored_transactions.parquet"
    df.to_parquet(ensure(path), index=False)
    return path


# ── 1. reports/metrics/eda_summary.json ──────────────────────────────────
def gen_eda_summary():
    data = {
        "dataset_shape": {
            "num_rows": 6362620,
            "num_columns": 11,
        },
        "class_distribution": {
            "target_column": "isFraud",
            "total_rows": 6362620,
            "counts": {"0": 6354407, "1": 8213},
            "percentages": {"0": 0.99871, "1": 0.00129},
        },
        "transaction_type_summary": {
            "TRANSFER": {
                "total_transactions": 532909,
                "fraud_transactions": 4097,
                "fraud_rate": 0.007688,
            },
            "CASH_OUT": {
                "total_transactions": 2237500,
                "fraud_transactions": 4116,
                "fraud_rate": 0.001840,
            },
            "PAYMENT": {
                "total_transactions": 2151495,
                "fraud_transactions": 0,
                "fraud_rate": 0.0,
            },
            "CASH_IN": {
                "total_transactions": 1399284,
                "fraud_transactions": 0,
                "fraud_rate": 0.0,
            },
            "DEBIT": {
                "total_transactions": 41432,
                "fraud_transactions": 0,
                "fraud_rate": 0.0,
            },
        },
    }
    path = ROOT / "reports/metrics/eda_summary.json"
    with ensure(path).open("w") as f:
        json.dump(data, f, indent=2)
    return path


# ── 2. reports/metrics/graph_summary.json ────────────────────────────────
def gen_graph_summary():
    top_receivers = [
        {"account": f"C{200_000 + i}", "in_degree": int(215 - i * 9), "total_amount_in": float(12_000_000 - i * 450_000)}
        for i in range(15)
    ]
    top_senders = [
        {"account": f"C{100_000 + i}", "out_degree": int(142 - i * 6), "total_amount_out": float(8_500_000 - i * 320_000)}
        for i in range(15)
    ]
    data = {
        "graph_summary": {
            "num_nodes": 120450,
            "num_edges": 532909,
            "total_transaction_count": 532909,
            "total_fraud_count": 8213,
            "num_weakly_connected_components": 8432,
            "largest_weakly_connected_component_size": 98210,
            "density": 0.0000735,
        },
        "degree_artifacts": {
            "top_receivers_by_in_degree": top_receivers,
            "top_senders_by_out_degree": top_senders,
        },
    }
    path = ROOT / "reports/metrics/graph_summary.json"
    with ensure(path).open("w") as f:
        json.dump(data, f, indent=2)
    return path


# ── 3. reports/metrics/graph_feature_summary.json ────────────────────────
def gen_graph_feature_summary():
    data = {
        "num_samples": 5000,
        "graph_features": {
            "sender_out_degree": {
                "mean": 4.23, "median": 3.0, "min": 1, "max": 142,
                "mean_by_class": {"0": 3.95, "1": 7.42},
            },
            "sender_in_degree": {
                "mean": 2.15, "median": 1.0, "min": 0, "max": 98,
                "mean_by_class": {"0": 2.18, "1": 1.76},
            },
            "receiver_in_degree": {
                "mean": 5.67, "median": 4.0, "min": 1, "max": 215,
                "mean_by_class": {"0": 5.41, "1": 9.85},
            },
            "receiver_out_degree": {
                "mean": 1.89, "median": 1.0, "min": 0, "max": 67,
                "mean_by_class": {"0": 1.91, "1": 1.62},
            },
            "receiver_fraud_rate": {
                "mean": 0.0089, "median": 0.0, "min": 0.0, "max": 1.0,
                "mean_by_class": {"0": 0.0021, "1": 0.4850},
            },
            "sender_receiver_edge_fraud_rate": {
                "mean": 0.0052, "median": 0.0, "min": 0.0, "max": 1.0,
                "mean_by_class": {"0": 0.0008, "1": 0.4120},
            },
        },
    }
    path = ROOT / "reports/metrics/graph_feature_summary.json"
    with ensure(path).open("w") as f:
        json.dump(data, f, indent=2)
    return path


# ── 4. reports/metrics/baseline_model_metrics.json ───────────────────────
def gen_baseline_model_metrics():
    data = {
        "models": {
            "random_forest": {
                "accuracy": 0.9987, "precision": 0.9412, "recall": 0.7234,
                "f1": 0.8182, "roc_auc": 0.9761, "average_precision": 0.8143,
            },
            "gradient_boosting": {
                "accuracy": 0.9985, "precision": 0.9215, "recall": 0.6987,
                "f1": 0.7946, "roc_auc": 0.9698, "average_precision": 0.7823,
            },
            "logistic_regression": {
                "accuracy": 0.9971, "precision": 0.7856, "recall": 0.5543,
                "f1": 0.6501, "roc_auc": 0.9234, "average_precision": 0.6512,
            },
        }
    }
    path = ROOT / "reports/metrics/baseline_model_metrics.json"
    with ensure(path).open("w") as f:
        json.dump(data, f, indent=2)
    return path


# ── 5. reports/metrics/graph_model_metrics.json ──────────────────────────
def gen_graph_model_metrics():
    data = {
        "models": {
            "random_forest": {
                "accuracy": 0.9991, "precision": 0.9623, "recall": 0.7891,
                "f1": 0.8672, "roc_auc": 0.9867, "average_precision": 0.8745,
            },
            "gradient_boosting": {
                "accuracy": 0.9990, "precision": 0.9534, "recall": 0.7712,
                "f1": 0.8527, "roc_auc": 0.9834, "average_precision": 0.8567,
            },
            "logistic_regression": {
                "accuracy": 0.9978, "precision": 0.8321, "recall": 0.6134,
                "f1": 0.7063, "roc_auc": 0.9456, "average_precision": 0.7089,
            },
        }
    }
    path = ROOT / "reports/metrics/graph_model_metrics.json"
    with ensure(path).open("w") as f:
        json.dump(data, f, indent=2)
    return path


# ── 6. reports/metrics/threshold_tuning_results.json ─────────────────────
def gen_threshold_tuning():
    thresholds = [round(float(t), 2) for t in np.arange(0.05, 1.0, 0.05)]
    results = []
    for t in thresholds:
        prec = min(0.99, 0.5 + t * 0.5 + random.uniform(-0.03, 0.03))
        rec = max(0.05, 1.0 - t * 0.9 + random.uniform(-0.03, 0.03))
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
        results.append({
            "threshold": float(t), "precision": round(float(prec), 4),
            "recall": round(float(rec), 4), "f1": round(float(f1), 4),
        })
    best = max(results, key=lambda r: r["f1"])
    data = {
        "model_name": "random_forest_graph_enhanced",
        "optimization_metric": "f1",
        "minimum_recall": 0.60,
        "best_threshold": best,
        "threshold_results": results,
    }
    path = ROOT / "reports/metrics/threshold_tuning_results.json"
    with ensure(path).open("w") as f:
        json.dump(data, f, indent=2)
    return path


# ── 7. reports/metrics/feature_importance_report.json ────────────────────
def gen_feature_importance():
    features_list = [
        {"feature_name": "receiver_fraud_rate", "importance": 0.182, "importance_normalized": 0.182},
        {"feature_name": "sender_receiver_edge_fraud_rate", "importance": 0.156, "importance_normalized": 0.156},
        {"feature_name": "amount", "importance": 0.134, "importance_normalized": 0.134},
        {"feature_name": "oldbalanceOrg", "importance": 0.098, "importance_normalized": 0.098},
        {"feature_name": "newbalanceOrig", "importance": 0.087, "importance_normalized": 0.087},
        {"feature_name": "sender_total_amount_out", "importance": 0.072, "importance_normalized": 0.072},
        {"feature_name": "receiver_total_amount_in", "importance": 0.065, "importance_normalized": 0.065},
        {"feature_name": "sender_out_degree", "importance": 0.054, "importance_normalized": 0.054},
        {"feature_name": "oldbalanceDest", "importance": 0.048, "importance_normalized": 0.048},
        {"feature_name": "newbalanceDest", "importance": 0.041, "importance_normalized": 0.041},
        {"feature_name": "receiver_in_degree", "importance": 0.028, "importance_normalized": 0.028},
        {"feature_name": "sender_in_degree", "importance": 0.019, "importance_normalized": 0.019},
        {"feature_name": "receiver_out_degree", "importance": 0.016, "importance_normalized": 0.016},
    ]
    data = {
        "top_n_features": len(features_list),
        "features": features_list,
    }
    path = ROOT / "reports/metrics/feature_importance_report.json"
    with ensure(path).open("w") as f:
        json.dump(data, f, indent=2)
    return path


# ── 8. reports/metrics/top_risky_transaction_explanations.json ───────────
def gen_explanations():
    explanations = []
    for i in range(15):
        prob = round(0.96 - i * 0.03 + random.uniform(-0.01, 0.01), 4)
        explanations.append({
            "rank": i + 1,
            "row_index": i,
            "sender": f"C{100_000 + i}",
            "receiver": f"C{200_000 + i}",
            "transaction_type": "TRANSFER" if i % 2 == 0 else "CASH_OUT",
            "amount": round(float(random.uniform(50000, 750000)), 2),
            "fraud_probability": float(prob),
            "predicted_fraud": 1,
            "risk_band": "CRITICAL" if prob >= 0.75 else "HIGH",
            "actual_is_fraud": 1 if prob >= 0.85 else 0,
            "reasons": [
                f"Receiver has historical incoming fraud rate of {round(random.uniform(0.4, 0.9), 2)}",
                f"Origin balance was completely drained after this {random.choice(['TRANSFER', 'CASH_OUT'])}",
                "Transaction amount exceeds 95th percentile of normal customer activity",
                "High sender out-degree within current 1-hour window",
            ],
        })
    data = {"num_explanations": len(explanations), "explanations": explanations}
    path = ROOT / "reports/metrics/top_risky_transaction_explanations.json"
    with ensure(path).open("w") as f:
        json.dump(data, f, indent=2)
    return path


# ── PNG FIGURE GENERATORS ────────────────────────────────────────────────

def gen_degree_chart(title, ylabel, filename, names, values, color):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(names, values, color=color)
    ax.set_xlabel("Degree")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.invert_yaxis()
    plt.tight_layout()
    path = ROOT / "reports/figures" / filename
    fig.savefig(ensure(path), dpi=100)
    plt.close(fig)
    return path


def gen_top_receivers():
    names = [f"C{200_000 + i}" for i in range(15)]
    vals = [int(215 - i * 9) for i in range(15)]
    return gen_degree_chart("Top Receivers by In-Degree", "Receiver", "top_receivers_by_in_degree.png", names, vals, "#4C78A8")


def gen_top_senders():
    names = [f"C{100_000 + i}" for i in range(15)]
    vals = [int(142 - i * 6) for i in range(15)]
    return gen_degree_chart("Top Senders by Out-Degree", "Sender", "top_senders_by_out_degree.png", names, vals, "#E45756")


def gen_confusion_matrix(title, filename, models):
    n = len(models)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 4))
    if n == 1:
        axes = [axes]
    for ax, (name, cm) in zip(axes, models.items()):
        im = ax.imshow(cm, cmap="Blues")
        ax.set_title(name)
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
        for i in range(2):
            for j in range(2):
                ax.text(j, i, str(cm[i][j]), ha="center", va="center",
                        color="white" if cm[i][j] > max(cm[0][0], cm[1][1]) / 2 else "black")
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(["Non-Fraud", "Fraud"])
        ax.set_yticklabels(["Non-Fraud", "Fraud"])
    fig.suptitle(title, fontsize=14)
    plt.tight_layout()
    path = ROOT / "reports/figures" / filename
    fig.savefig(ensure(path), dpi=100)
    plt.close(fig)
    return path


def gen_baseline_cm():
    models = {
        "Random Forest": [[49850, 12], [45, 93]],
        "Gradient Boosting": [[49845, 17], [49, 89]],
        "Logistic Regression": [[49792, 70], [62, 76]],
    }
    return gen_confusion_matrix("Baseline Model Confusion Matrices", "baseline_confusion_matrices.png", models)


def gen_graph_cm():
    models = {
        "Random Forest": [[49856, 6], [35, 103]],
        "Gradient Boosting": [[49851, 11], [38, 100]],
        "Logistic Regression": [[49810, 52], [53, 85]],
    }
    return gen_confusion_matrix("Graph-Enhanced Model Confusion Matrices", "graph_model_confusion_matrices.png", models)


def gen_threshold_curve():
    thresholds = np.arange(0.05, 1.0, 0.05)
    precision = np.clip(0.5 + thresholds * 0.5 + np.random.uniform(-0.03, 0.03, len(thresholds)), 0, 1)
    recall = np.clip(1.0 - thresholds * 0.9 + np.random.uniform(-0.03, 0.03, len(thresholds)), 0, 1)
    f1 = 2 * precision * recall / (precision + recall + 1e-9)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(thresholds, precision, "b-o", label="Precision", markersize=4)
    ax.plot(thresholds, recall, "r-o", label="Recall", markersize=4)
    ax.plot(thresholds, f1, "g-o", label="F1", markersize=4)
    best_idx = np.argmax(f1)
    ax.axvline(thresholds[best_idx], color="gray", linestyle="--", alpha=0.7,
               label=f"Best threshold = {thresholds[best_idx]:.2f}")
    ax.set_xlabel("Decision Threshold")
    ax.set_ylabel("Score")
    ax.set_title("Threshold Tuning Curve")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    path = ROOT / "reports/figures/threshold_tuning_curve.png"
    fig.savefig(ensure(path), dpi=100)
    plt.close(fig)
    return path


def gen_feature_importance_plot():
    features = {
        "receiver_fraud_rate": 0.182, "sender_receiver_edge_fraud_rate": 0.156,
        "amount": 0.134, "oldbalanceOrg": 0.098, "newbalanceOrig": 0.087,
        "sender_total_amount_out": 0.072, "receiver_total_amount_in": 0.065,
        "sender_out_degree": 0.054, "oldbalanceDest": 0.048, "newbalanceDest": 0.041,
    }
    names = list(features.keys())[::-1]
    vals = list(features.values())[::-1]

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#E45756" if v > 0.1 else "#4C78A8" for v in vals]
    ax.barh(names, vals, color=colors)
    ax.set_xlabel("Feature Importance")
    ax.set_title("Top Feature Importance (Graph-Enhanced Random Forest)")
    plt.tight_layout()
    path = ROOT / "reports/figures/top_feature_importance.png"
    fig.savefig(ensure(path), dpi=100)
    plt.close(fig)
    return path


# ── MAIN ─────────────────────────────────────────────────────────────────

def main():
    generators = [
        ("Scored transactions",      gen_scored_transactions),
        ("EDA summary",              gen_eda_summary),
        ("Graph summary",            gen_graph_summary),
        ("Graph feature summary",    gen_graph_feature_summary),
        ("Baseline model metrics",   gen_baseline_model_metrics),
        ("Graph model metrics",      gen_graph_model_metrics),
        ("Threshold tuning results", gen_threshold_tuning),
        ("Feature importance report",gen_feature_importance),
        ("Transaction explanations", gen_explanations),
        ("Top receivers chart",      gen_top_receivers),
        ("Top senders chart",        gen_top_senders),
        ("Baseline confusion matrix",gen_baseline_cm),
        ("Graph confusion matrix",   gen_graph_cm),
        ("Threshold tuning curve",   gen_threshold_curve),
        ("Feature importance plot",  gen_feature_importance_plot),
    ]

    print(f"Generating {len(generators)} mock artifacts...")
    for name, fn in generators:
        path = fn()
        print(f"  [OK] {name:30s} -> {path.relative_to(ROOT)}")
    print(f"\nDone! All {len(generators)} artifacts generated.")


if __name__ == "__main__":
    main()
