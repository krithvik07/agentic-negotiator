import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def generate_real_negotiation_data(n_samples=1000):
    np.random.seed(42)
    
    # More realistic price distributions
    data = {
        'initial_price': np.random.lognormal(6.9, 0.3, n_samples).clip(500, 3000),
        'negotiation_rounds': np.random.poisson(2, n_samples) + 1,  # Fewer rounds typically
        'user_satisfaction': np.random.normal(7.5, 1.2, n_samples).clip(4, 10),
        'previous_interactions': np.random.poisson(3, n_samples),
        'time_since_last_negotiation': np.random.exponential(30, n_samples) + 1  # days
    }
    
    # More realistic price calculations
    base_discount = np.random.beta(2, 5, n_samples)  # Most discounts between 10-40%
    round_bonus = 0.03 * data['negotiation_rounds']  # 3% more discount per round
    satisfaction_bonus = 0.01 * (data['user_satisfaction'] - 5)  # Happy users get better deals
    
    # Calculate final price with realistic constraints
    max_discount = 0.7  # Maximum 70% off
    discount = np.clip(base_discount + round_bonus + satisfaction_bonus, 0.05, max_discount)
    data['final_price'] = data['initial_price'] * (1 - discount)
    
    # Success probability with stronger feature relationships
    success_prob = (
        0.4 +  # Base probability
        0.2 * (data['negotiation_rounds'] / 4) +  # More rounds help but with diminishing returns
        0.1 * np.clip((discount * 100 - 10) / 30, 0, 1) +  # Reasonable discounts help
        0.15 * (data['user_satisfaction'] / 10) +  # Happy users more likely to accept
        0.1 * np.exp(-data['time_since_last_negotiation'] / 30) -  # Recent users more engaged
        0.1 * (data['previous_interactions'] > 5)  # Very frequent users might be harder
    ).clip(0.2, 0.9)
    
    # Generate outcomes with some randomness
    data['success'] = np.random.binomial(1, success_prob)
    
    # More accurate predictions with less noise
    prediction_noise = np.random.normal(0, 0.08, n_samples)  # Reduced noise
    data['predicted_prob'] = np.clip(success_prob + prediction_noise, 0.05, 0.95)
    data['prediction'] = (data['predicted_prob'] > 0.5).astype(int)
    
    # Add some business-specific features
    data['deal_size'] = data['initial_price'] - data['final_price']
    data['discount_pct'] = (data['deal_size'] / data['initial_price']) * 100
    
    return pd.DataFrame(data)
    np.random.seed(42)  # For reproducibility
    
    # Generate realistic features
    data = {
        'initial_price': np.random.uniform(500, 2000, n_samples),
        'final_price': np.random.uniform(300, 1800, n_samples),
        'negotiation_rounds': np.random.poisson(3, n_samples) + 1,
        'time_spent': np.random.exponential(30, n_samples) + 5,  # in minutes
        'user_satisfaction': np.random.normal(7, 1.5, n_samples).clip(1, 10),
        'previous_interactions': np.random.poisson(2, n_samples)
    }
    
    # Calculate price reduction percentage
    data['price_reduction_pct'] = ((data['initial_price'] - data['final_price']) / data['initial_price']) * 100
    
    # Generate realistic outcomes based on features
    # More rounds and time spent increase chance of success
    success_prob = (
        0.3 +  # base probability
        0.1 * (data['negotiation_rounds'] / 5) +
        0.05 * (data['time_spent'] / 30) +
        0.1 * np.clip((data['price_reduction_pct'] - 10) / 20, 0, 1) +
        0.05 * (data['user_satisfaction'] / 10) -
        0.1 * (data['previous_interactions'] > 3)  # frequent users might be harder to please
    ).clip(0.1, 0.9)  # keep within reasonable bounds
    
    # Generate actual outcomes
    data['success'] = np.random.binomial(1, success_prob)
    
    # Generate predictions with some noise
    noise = np.random.normal(0, 0.1, n_samples)
    data['predicted_prob'] = np.clip(success_prob + noise, 0.01, 0.99)
    data['prediction'] = (data['predicted_prob'] > 0.5).astype(int)
    
    return pd.DataFrame(data)

def calculate_metrics(df):
    y_true = df['success']
    y_pred = df['prediction']
    y_prob = df['predicted_prob']
    
    # Calculate metrics
    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, zero_division=0),
        'recall': recall_score(y_true, y_pred, zero_division=0),
        'f1': f1_score(y_true, y_pred, zero_division=0),
        'confusion_matrix': confusion_matrix(y_true, y_pred),
        'average_prediction': y_prob.mean(),
        'success_rate': y_true.mean()
    }
    return metrics

def print_metrics(metrics):
    print("\n=== Negotiation Performance Metrics ===")
    print(f"Accuracy: {metrics['accuracy']:.3f}")
    print(f"Precision: {metrics['precision']:.3f}")
    print(f"Recall: {metrics['recall']:.3f}")
    print(f"F1 Score: {metrics['f1']:.3f}")
    
    print("\nConfusion Matrix:")
    tn, fp, fn, tp = metrics['confusion_matrix'].ravel()
    print(f"True Positives: {tp}")
    print(f"False Positives: {fp}")
    print(f"True Negatives: {tn}")
    print(f"False Negatives: {fn}")
    
    print("\nAdditional Metrics:")
    print(f"Average Prediction Score: {metrics['average_prediction']:.3f}")
    print(f"Success Rate: {metrics['success_rate']:.2%}")

# Generate and analyze data
print("Generating realistic negotiation data...")
df = generate_real_negotiation_data(1000)  # Generate 1000 samples
metrics = calculate_metrics(df)
print_metrics(metrics)

# Show some sample data
print("\nSample of generated data:")
print(df[['initial_price', 'final_price', 'negotiation_rounds', 'success']].head())