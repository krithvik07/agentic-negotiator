from sklearn.metrics import (
    confusion_matrix, 
    roc_curve, 
    auc, 
    precision_recall_curve, 
    average_precision_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)
import numpy as np

def calculate_confusion_matrix(y_true, y_pred_proba, threshold=0.5):
    """Calculate confusion matrix."""
    y_pred = (y_pred_proba >= threshold).astype(int)
    return confusion_matrix(y_true, y_pred)

def calculate_roc_auc(y_true, y_scores):
    """Calculate ROC curve and AUC."""
    fpr, tpr, _ = roc_curve(y_true, y_scores)
    roc_auc = auc(fpr, tpr)
    return fpr, tpr, roc_auc

def calculate_pr_metrics(y_true, y_scores):
    """Calculate precision-recall metrics."""
    precision, recall, _ = precision_recall_curve(y_true, y_scores)
    avg_precision = average_precision_score(y_true, y_scores)
    return precision, recall, avg_precision

def calculate_all_metrics(y_true, y_pred_proba, threshold=0.5):
    """Calculate all classification metrics."""
    y_pred = (y_pred_proba >= threshold).astype(int)
    
    return {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, zero_division=0),
        'recall': recall_score(y_true, y_pred, zero_division=0),
        'f1': f1_score(y_true, y_pred, zero_division=0),
        'roc_auc': calculate_roc_auc(y_true, y_pred_proba)[2],
        'avg_precision': average_precision_score(y_true, y_pred_proba)
    }