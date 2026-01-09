"""
SHAP Analyzer

Uses SHAP (SHapley Additive exPlanations) for feature attribution
in root cause analysis.
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import shap
import warnings
warnings.filterwarnings('ignore')


class SHAPAnalyzer:
    """Analyzes feature importance using SHAP values"""
    
    def __init__(self, model_type: str = 'random_forest'):
        """
        Initialize SHAP analyzer
        
        Args:
            model_type: Type of model ('random_forest' or 'logistic')
        """
        self.model_type = model_type
        self.models = {}
        self.scalers = {}
        self.explainers = {}
    
    def prepare_features(self, orders_df: pd.DataFrame,
                        deliveries_df: pd.DataFrame,
                        items_df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare feature matrix from raw data
        
        Returns:
            DataFrame with features
        """
        # Merge data
        merged = orders_df.merge(deliveries_df, on='order_id', how='left')
        
        # Aggregate item-level features
        item_features = items_df.groupby('order_id').agg({
            'substituted_flag': 'any',
            'missing_flag': 'any',
            'refund_amount': 'sum',
            'ordered_qty': 'sum'
        }).reset_index()
        item_features.columns = ['order_id', 'has_substitution', 'has_missing', 
                                 'total_refund', 'total_items']
        
        merged = merged.merge(item_features, on='order_id', how='left')
        
        # Fill missing values
        merged['has_substitution'] = merged['has_substitution'].fillna(False)
        merged['has_missing'] = merged['has_missing'].fillna(False)
        merged['total_refund'] = merged['total_refund'].fillna(0)
        merged['total_items'] = merged['total_items'].fillna(0)
        
        # Create feature matrix
        features = pd.DataFrame()
        
        # Numeric features
        features['basket_value'] = merged['basket_value']
        features['distance'] = merged['distance']
        features['merchant_prep_time'] = merged['merchant_prep_time']
        features['dasher_wait'] = merged['dasher_wait']
        features['total_refund'] = merged['total_refund']
        features['total_items'] = merged['total_items']
        
        # Categorical features (one-hot encoded)
        features['batched'] = merged['batched_flag'].astype(int)
        features['has_substitution'] = merged['has_substitution'].astype(int)
        features['has_missing'] = merged['has_missing'].astype(int)
        
        # Category encoding
        category_map = {'grocery': 0, 'convenience': 1, 'retail': 2}
        features['category'] = merged['category'].map(category_map).fillna(0)
        
        # Time of day encoding
        time_map = {'breakfast': 0, 'lunch': 1, 'dinner': 2, 'late-night': 3}
        features['time_of_day'] = merged['time_of_day'].map(time_map).fillna(0)
        
        # Region encoding (simplified)
        region_map = {'SF': 0, 'NYC': 1, 'LA': 2, 'Chicago': 3, 'Boston': 4}
        features['region'] = merged['region'].map(region_map).fillna(0)
        
        # Fill any remaining NaN
        features = features.fillna(0)
        
        return features
    
    def train_model(self, X: pd.DataFrame, y: pd.Series,
                   outcome_name: str) -> Tuple:
        """
        Train model for a specific outcome
        
        Args:
            X: Feature matrix
            y: Target variable
            outcome_name: Name of outcome (e.g., 'late', 'canceled', 'refund')
        
        Returns:
            Tuple of (model, scaler, explainer)
        """
        # Remove rows with missing target
        mask = ~y.isna()
        X_clean = X[mask].copy()
        y_clean = y[mask].copy()
        
        if len(X_clean) == 0:
            return None, None, None
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_clean)
        X_scaled_df = pd.DataFrame(X_scaled, columns=X_clean.columns, index=X_clean.index)
        
        # Train model
        if self.model_type == 'logistic':
            model = LogisticRegression(max_iter=1000, random_state=42)
        else:
            # Use RandomForest for binary classification
            if y_clean.nunique() == 2:
                model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
            else:
                model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        
        model.fit(X_scaled_df, y_clean)
        
        # Create SHAP explainer
        try:
            explainer = shap.TreeExplainer(model)
        except:
            # Fallback to KernelExplainer if TreeExplainer fails
            explainer = shap.KernelExplainer(model.predict, X_scaled_df.sample(min(100, len(X_scaled_df))))
        
        self.models[outcome_name] = model
        self.scalers[outcome_name] = scaler
        self.explainers[outcome_name] = explainer
        
        return model, scaler, explainer
    
    def calculate_shap_values(self, X: pd.DataFrame,
                             outcome_name: str,
                             sample_size: Optional[int] = None) -> pd.DataFrame:
        """
        Calculate SHAP values for features
        
        Args:
            X: Feature matrix
            outcome_name: Name of outcome model
            sample_size: Optional sample size for faster computation
        
        Returns:
            DataFrame with SHAP values
        """
        if outcome_name not in self.models:
            raise ValueError(f"Model for {outcome_name} not trained yet")
        
        model = self.models[outcome_name]
        scaler = self.scalers[outcome_name]
        explainer = self.explainers[outcome_name]
        
        # Scale features
        X_scaled = scaler.transform(X)
        X_scaled_df = pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
        
        # Sample if needed
        if sample_size and len(X_scaled_df) > sample_size:
            X_sample = X_scaled_df.sample(sample_size, random_state=42)
        else:
            X_sample = X_scaled_df
        
        # Calculate SHAP values
        try:
            shap_values = explainer.shap_values(X_sample)
            
            # Handle binary classification (SHAP returns list)
            if isinstance(shap_values, list):
                shap_values = shap_values[1]  # Use positive class
            
            shap_df = pd.DataFrame(shap_values, columns=X.columns, index=X_sample.index)
        except Exception as e:
            # Fallback: use feature importance
            print(f"SHAP calculation failed: {e}, using feature importance")
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
            else:
                importances = np.abs(model.coef_[0]) if hasattr(model, 'coef_') else np.ones(len(X.columns))
            
            shap_df = pd.DataFrame(
                np.tile(importances, (len(X_sample), 1)),
                columns=X.columns,
                index=X_sample.index
            )
        
        return shap_df
    
    def get_feature_importance(self, orders_df: pd.DataFrame,
                              deliveries_df: pd.DataFrame,
                              items_df: pd.DataFrame,
                              outcome_column: str,
                              outcome_name: str) -> Dict[str, float]:
        """
        Get feature importance for a specific outcome
        
        Args:
            orders_df: Orders DataFrame
            deliveries_df: Deliveries DataFrame
            items_df: Items DataFrame
            outcome_column: Column name for outcome (e.g., 'is_late', 'canceled_flag')
            outcome_name: Name for outcome model
        
        Returns:
            Dict mapping feature names to importance scores
        """
        # Prepare features
        X = self.prepare_features(orders_df, deliveries_df, items_df)
        
        # Get outcome variable
        if outcome_column in deliveries_df.columns:
            y = deliveries_df.set_index('order_id')[outcome_column]
            # Align with X
            y = y.reindex(X.index).fillna(0)
        else:
            raise ValueError(f"Outcome column {outcome_column} not found")
        
        # Train model
        model, scaler, explainer = self.train_model(X, y, outcome_name)
        
        if model is None:
            return {}
        
        # Calculate SHAP values
        shap_df = self.calculate_shap_values(X, outcome_name, sample_size=500)
        
        # Aggregate SHAP values (mean absolute value)
        importance = {}
        for col in shap_df.columns:
            importance[col] = float(shap_df[col].abs().mean())
        
        # Normalize to sum to 1
        total = sum(importance.values())
        if total > 0:
            importance = {k: v / total for k, v in importance.items()}
        
        return importance
    
    def analyze_slice(self, orders_df: pd.DataFrame,
                     deliveries_df: pd.DataFrame,
                     items_df: pd.DataFrame,
                     cohort: Dict,
                     outcome_column: str,
                     outcome_name: str) -> Dict[str, float]:
        """
        Analyze feature importance for a specific cohort slice
        
        Args:
            orders_df: Orders DataFrame
            deliveries_df: Deliveries DataFrame
            items_df: Items DataFrame
            cohort: Cohort filter dict
            outcome_column: Outcome column name
            outcome_name: Outcome name
        
        Returns:
            Feature importance dict for this slice
        """
        # Filter data by cohort
        from metrics.cohort_slicer import CohortSlicer
        slicer = CohortSlicer()
        
        filtered_orders = slicer.filter_by_cohort(orders_df, cohort)
        order_ids = filtered_orders['order_id'].unique()
        
        filtered_deliveries = deliveries_df[deliveries_df['order_id'].isin(order_ids)]
        filtered_items = items_df[items_df['order_id'].isin(order_ids)]
        
        # Calculate importance
        return self.get_feature_importance(
            filtered_orders,
            filtered_deliveries,
            filtered_items,
            outcome_column,
            outcome_name
        )

