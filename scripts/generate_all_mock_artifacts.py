"""Generate ALL mock artifacts needed by every Streamlit dashboard page."""

import json
import random
from pathlib import Path

import numpy as np
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


# ── 1. reports/metrics/eda_summary.json ──────────────────────────────────
def gen_eda_summary():
    data = {
        "num_transactions": 6362620,
        "num_features": 11,
        "fraud_rate": 0.00129,
        "class_distribution": {"0": 6354407, "1": 8213},
        "transaction_type_counts": {
            "CASH_OUT": 2237500,
            "PAYMENT": 2151495,
            "CASH_IN": 1399284,
            "TRANSFER": 532909,
            "DEBIT": 41432,
        },
        "amount_statistics": {
            "mean": 179861.90,
            "std": 603858.23,
            "min": 0.0,
            "25%": 13389.57,
            "50%": 74871.94,
            "75%": 208721.26,
            "max": 92445516.64,
        },
        "missing_values": {},
        "fraud_by_type": {
            "TRANSFER": 4097,
            "CASH_OUT": 4116,
            "PAYMENT": 0,
            "CASH_IN": 0,
            "DEBIT": 0,
        },
    }
    path = ROOT / "reports/metrics/eda_summary.json"
    with ensure(path).open("w") as f:
        json.dump(data, f, indent=2)
    return path


# ── 2. reports/metrics/graph_summary.json ────────────────────────────────
def gen_graph_summary():
    data = {
        "num_nodes": 120450,
        "num_edges": 532909,
        "average_degree": 8.85,
        "density": 0.0000735,
        "num_connected_components": 8432,
        "largest_component_size": 98210,
        "average_clustering_coefficient": 0.0021,
        "transaction_types_in_graph": ["TRANSFER", "CASH_OUT"],
        "fraud_edges": 8213,
        "non_fraud_edges": 524696,
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
            "sender_out_degree":       {"mean": 4.23, "std": 6.81, "min": 1, "max": 142},
            "sender_in_degree":        {"mean": 2.15, "std": 4.32, "min": 0, "max": 98},
            "receiver_in_degree":      {"mean": 5.67, "std": 9.45, "min": 1, "max": 215},
            "receiver_out_degree":     {"mean": 1.89, "std": 3.21, "min": 0, "max": 67},
            "sender_total_amount_out": {"mean": 185432.1, "std": 412305.6, "min": 100.0, "max": 8500000.0},
            "receiver_total_amount_in":{"mean": 210543.8, "std": 520412.3, "min": 50.0, "max": 12000000.0},
            "receiver_fraud_rate":     {"mean": 0.0089, "std": 0.045, "min": 0.0, "max": 1.0},
            "sender_receiver_edge_fraud_rate": {"mean": 0.0052, "std": 0.038, "min": 0.0, "max": 1.0},
        },
        "correlation_with_fraud": {
            "sender_out_degree": 0.12,
            "sender_in_degree": 0.05,
            "receiver_in_degree": -0.03,
            "receiver_out_degree": 0.08,
            "sender_total_amount_out": 0.15,
            "receiver_total_amount_in": 0.09,
            "receiver_fraud_rate": 0.42,
            "sender_receiver_edge_fraud_rate": 0.38,
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
    thresholds = [round(t, 2) for t in np.arange(0.05, 1.0, 0.05)]
    results = []
    for t in thresholds:
        prec = min(0.99, 0.5 + t * 0.5 + random.uniform(-0.03, 0.03))
        rec = max(0.05, 1.0 - t * 0.9 + random.uniform(-0.03, 0.03))
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
        results.append({
            "threshold": t, "precision": round(prec, 4),
            "recall": round(rec, 4), "f1": round(f1, 4),
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
    features = {
        "receiver_fraud_rate": 0.182,
        "sender_receiver_edge_fraud_rate": 0.156,
        "amount": 0.134,
        "oldbalanceOrg": 0.098,
        "newbalanceOrig": 0.087,
        "sender_total_amount_out": 0.072,
        "receiver_total_amount_in": 0.065,
        "sender_out_degree": 0.054,
        "oldbalanceDest": 0.048,
        "newbalanceDest": 0.041,
        "receiver_in_degree": 0.028,
        "sender_in_degree": 0.019,
        "receiver_out_degree": 0.016,
    }
    data = {
        "model_name": "random_forest_graph_enhanced",
        "importance_type": "feature_importances_",
        "features": features,
        "top_n": 13,
    }
    path = ROOT / "reports/metrics/feature_importance_report.json"
    with ensure(path).open("w") as f:
        json.dump(data, f, indent=2)
    return path


# ── 8. reports/metrics/top_risky_transaction_explanations.json ───────────
def gen_explanations():
    explanations = []
    for i in range(10):
        prob = round(0.95 - i * 0.04 + random.uniform(-0.01, 0.01), 4)
        explanations.append({
            "transaction_id": f"TXN{100000 + i}",
            "fraud_probability": prob,
            "predicted_fraud": 1,
            "risk_band": "CRITICAL" if prob >= 0.75 else "HIGH",
            "type": random.choice(["TRANSFER", "CASH_OUT"]),
            "amount": round(random.uniform(50000, 500000), 2),
            "explanation": {
                "top_features": [
                    {"feature": "receiver_fraud_rate", "shap_value": round(random.uniform(0.15, 0.35), 4)},
                    {"feature": "amount", "shap_value": round(random.uniform(0.08, 0.20), 4)},
                    {"feature": "sender_receiver_edge_fraud_rate", "shap_value": round(random.uniform(0.05, 0.15), 4)},
                    {"feature": "oldbalanceOrg", "shap_value": round(random.uniform(0.02, 0.10), 4)},
                    {"feature": "sender_out_degree", "shap_value": round(random.uniform(0.01, 0.08), 4)},
                ],
                "summary": f"Transaction flagged as {'CRITICAL' if prob >= 0.75 else 'HIGH'} because: "
                           f"receiver has high fraud rate, large transfer amount, "
                           f"sender-receiver relationship has previous fraud signal.",
            },
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
    names = [f"C{random.randint(100000,999999)}" for _ in range(15)]
    vals = sorted([random.randint(20, 215) for _ in range(15)], reverse=True)
    return gen_degree_chart("Top Receivers by In-Degree", "Receiver", "top_receivers_by_in_degree.png", names, vals, "#4C78A8")


def gen_top_senders():
    names = [f"C{random.randint(100000,999999)}" for _ in range(15)]
    vals = sorted([random.randint(15, 142) for _ in range(15)], reverse=True)
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
