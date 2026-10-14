import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Any

def plot_confusion_matrix(y_true: np.ndarray, 
                         y_pred_proba: np.ndarray, 
                         classes: List[str] = None,
                         title: str = 'Confusion Matrix',
                         save_path: Optional[str] = None) -> None:
    """Plot confusion matrix."""
    if classes is None:
        classes = ['Rejected', 'Accepted']
    
    y_pred = (y_pred_proba >= 0.5).astype(int)
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=classes, yticklabels=classes)
    plt.title(title)
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()

def plot_roc_curve(fpr: np.ndarray, tpr: np.ndarray, roc_auc: float,
                  title: str = 'ROC Curve',
                  save_path: Optional[str] = None) -> None:
    """Plot ROC curve."""
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, 
             label=f'ROC curve (AUC = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(title)
    plt.legend(loc="lower right")
    
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()

def plot_precision_recall_curve(precision: np.ndarray, recall: np.ndarray,
                              avg_precision: float,
                              title: str = 'Precision-Recall Curve',
                              save_path: Optional[str] = None) -> None:
    """Plot precision-recall curve."""
    plt.figure(figsize=(8, 6))
    plt.step(recall, precision, where='post', 
             label=f'AP = {avg_precision:.2f}')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.ylim([0.0, 1.05])
    plt.xlim([0.0, 1.0])
    plt.title(f'{title} (AP = {avg_precision:.2f})')
    plt.legend(loc="upper right")
    
    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()

def generate_performance_report(y_true: np.ndarray, 
                              y_scores: np.ndarray,
                              output_dir: str = 'reports/figures/') -> Dict[str, Any]:
    """Generate and save performance report."""
    from .metrics import (
        calculate_confusion_matrix,
        calculate_roc_auc,
        calculate_pr_metrics,
        calculate_all_metrics
    )
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Calculate metrics
    metrics = calculate_all_metrics(y_true, y_scores)
    fpr, tpr, roc_auc = calculate_roc_auc(y_true, y_scores)
    precision, recall, avg_precision = calculate_pr_metrics(y_true, y_scores)
    
    # Generate plots
    plot_confusion_matrix(
        y_true, y_scores,
        save_path=f"{output_dir}/confusion_matrix.png"
    )
    
    plot_roc_curve(
        fpr, tpr, roc_auc,
        save_path=f"{output_dir}/roc_curve.png"
    )
    
    plot_precision_recall_curve(
        precision, recall, avg_precision,
        save_path=f"{output_dir}/pr_curve.png"
    )
    
    # Save metrics to file
    import json
    metrics_path = f"{output_dir}/metrics.json"
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    return metrics