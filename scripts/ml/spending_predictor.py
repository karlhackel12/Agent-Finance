#!/usr/bin/env python3
"""
Spending Predictor - ML model for predicting future expenses
Uses historical transaction data to forecast spending by category
"""

import sqlite3
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Try to import sklearn, fall back to simple statistics if not available
try:
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import IsolationForest
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not installed. Using simple statistics.")

DB_PATH = Path(__file__).parent.parent.parent / "data" / "finance.db"


class SpendingPredictor:
    """
    Machine Learning predictor for spending patterns.

    Features:
    - Predict next month spending by category
    - Detect anomalies in spending
    - Analyze trends over time
    """

    def __init__(self, lookback_months: int = 6):
        """
        Initialize predictor.

        Args:
            lookback_months: Number of months of history to use for predictions
        """
        self.lookback_months = lookback_months
        self.models: Dict[str, any] = {}
        self.historical_data: Dict[str, List[float]] = {}
        self.category_stats: Dict[str, Dict] = {}

    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def load_historical_data(self) -> Dict[str, List[Tuple[str, float]]]:
        """
        Load historical spending data from database.

        Returns:
            Dict with category -> list of (month, amount) tuples
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get spending by category and month for the last N months
        query = '''
            SELECT
                strftime('%Y-%m', t.date) as month,
                c.name as category,
                SUM(ABS(t.amount)) as total
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.type = 'expense'
            AND t.date >= date('now', ?)
            GROUP BY month, c.name
            ORDER BY month, c.name
        '''

        cursor.execute(query, (f'-{self.lookback_months} months',))
        rows = cursor.fetchall()
        conn.close()

        # Organize by category
        data: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
        for row in rows:
            data[row['category']].append((row['month'], row['total']))

        self.historical_data = data
        return data

    def prepare_features(self, category: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare features for ML model.

        Args:
            category: Category name

        Returns:
            Tuple of (X features, y targets)
        """
        if category not in self.historical_data:
            return np.array([]), np.array([])

        data = self.historical_data[category]
        if len(data) < 2:
            return np.array([]), np.array([])

        # Create features: month index (0, 1, 2, ...)
        X = np.array(range(len(data))).reshape(-1, 1)
        y = np.array([amount for _, amount in data])

        return X, y

    def train_model(self, category: str) -> bool:
        """
        Train prediction model for a category.

        Args:
            category: Category name

        Returns:
            True if model was trained successfully
        """
        X, y = self.prepare_features(category)

        if len(X) < 2:
            return False

        if SKLEARN_AVAILABLE:
            model = LinearRegression()
            model.fit(X, y)
            self.models[category] = model
        else:
            # Simple linear regression fallback
            n = len(X)
            x_mean = np.mean(X)
            y_mean = np.mean(y)

            numerator = np.sum((X.flatten() - x_mean) * (y - y_mean))
            denominator = np.sum((X.flatten() - x_mean) ** 2)

            if denominator == 0:
                slope = 0
            else:
                slope = numerator / denominator

            intercept = y_mean - slope * x_mean
            self.models[category] = {'slope': slope, 'intercept': intercept}

        # Calculate statistics
        self.category_stats[category] = {
            'mean': float(np.mean(y)),
            'std': float(np.std(y)),
            'min': float(np.min(y)),
            'max': float(np.max(y)),
            'months': len(y)
        }

        return True

    def train_all(self) -> Dict[str, bool]:
        """
        Train models for all categories.

        Returns:
            Dict with category -> training success
        """
        if not self.historical_data:
            self.load_historical_data()

        results = {}
        for category in self.historical_data.keys():
            results[category] = self.train_model(category)

        return results

    def predict_next_month(self, category: str) -> Dict:
        """
        Predict spending for next month.

        Args:
            category: Category name

        Returns:
            Dict with prediction, confidence, and bounds
        """
        if category not in self.models:
            if not self.train_model(category):
                return {
                    'predicted': 0,
                    'confidence': 0,
                    'lower_bound': 0,
                    'upper_bound': 0,
                    'error': 'Insufficient data'
                }

        data = self.historical_data.get(category, [])
        next_idx = len(data)

        if SKLEARN_AVAILABLE:
            model = self.models[category]
            predicted = model.predict([[next_idx]])[0]
        else:
            model = self.models[category]
            predicted = model['slope'] * next_idx + model['intercept']

        # Calculate confidence based on data variance
        stats = self.category_stats.get(category, {})
        std = stats.get('std', 0)
        mean = stats.get('mean', predicted)

        # Confidence: lower if high variance relative to mean
        if mean > 0:
            cv = std / mean  # Coefficient of variation
            confidence = max(0, min(1, 1 - cv))
        else:
            confidence = 0.5

        # Bounds: +/- 1.5 standard deviations
        lower_bound = max(0, predicted - 1.5 * std)
        upper_bound = predicted + 1.5 * std

        return {
            'predicted': round(predicted, 2),
            'confidence': round(confidence, 2),
            'lower_bound': round(lower_bound, 2),
            'upper_bound': round(upper_bound, 2),
            'historical_mean': round(mean, 2),
            'historical_std': round(std, 2)
        }

    def predict_all_categories(self) -> Dict[str, Dict]:
        """
        Predict spending for all categories.

        Returns:
            Dict with category -> prediction details
        """
        if not self.historical_data:
            self.load_historical_data()

        predictions = {}
        total_predicted = 0

        for category in self.historical_data.keys():
            pred = self.predict_next_month(category)
            predictions[category] = pred
            total_predicted += pred.get('predicted', 0)

        predictions['_total'] = {
            'predicted': round(total_predicted, 2),
            'categories': len(predictions) - 1
        }

        return predictions

    def detect_anomalies(self, threshold: float = 2.0) -> List[Dict]:
        """
        Detect anomalous spending in recent transactions.

        Args:
            threshold: Number of standard deviations to consider anomalous

        Returns:
            List of anomalous transactions
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get recent transactions
        query = '''
            SELECT
                t.id, t.date, t.description, ABS(t.amount) as amount,
                c.name as category
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.type = 'expense'
            AND t.date >= date('now', '-30 days')
            ORDER BY t.date DESC
        '''

        cursor.execute(query)
        transactions = [dict(row) for row in cursor.fetchall()]
        conn.close()

        anomalies = []

        for tx in transactions:
            category = tx['category']
            stats = self.category_stats.get(category, {})

            if not stats:
                continue

            mean = stats.get('mean', 0)
            std = stats.get('std', 0)

            if std == 0:
                continue

            # Z-score
            z_score = (tx['amount'] - mean) / std

            if abs(z_score) > threshold:
                anomalies.append({
                    'id': tx['id'],
                    'date': tx['date'],
                    'description': tx['description'],
                    'amount': tx['amount'],
                    'category': category,
                    'z_score': round(z_score, 2),
                    'reason': f'{abs(z_score):.1f}x desvio padrão' if z_score > 0 else f'Abaixo da média',
                    'expected_range': f'R$ {mean - std:.0f} - R$ {mean + std:.0f}'
                })

        return sorted(anomalies, key=lambda x: abs(x['z_score']), reverse=True)

    def analyze_trends(self) -> Dict[str, Dict]:
        """
        Analyze spending trends by category.

        Returns:
            Dict with category -> trend analysis
        """
        if not self.historical_data:
            self.load_historical_data()

        trends = {}

        for category, data in self.historical_data.items():
            if len(data) < 3:
                trends[category] = {
                    'trend': 'insufficient_data',
                    'change_pct': 0
                }
                continue

            amounts = [amount for _, amount in data]

            # Compare recent (last 2 months) vs older (rest)
            recent = amounts[-2:] if len(amounts) >= 2 else amounts
            older = amounts[:-2] if len(amounts) > 2 else amounts

            recent_avg = np.mean(recent)
            older_avg = np.mean(older)

            if older_avg > 0:
                change_pct = ((recent_avg - older_avg) / older_avg) * 100
            else:
                change_pct = 0

            # Determine trend direction
            if change_pct > 10:
                trend = 'increasing'
            elif change_pct < -10:
                trend = 'decreasing'
            else:
                trend = 'stable'

            trends[category] = {
                'trend': trend,
                'change_pct': round(change_pct, 1),
                'recent_avg': round(recent_avg, 2),
                'historical_avg': round(older_avg, 2),
                'description': f'{change_pct:+.0f}% vs últimos {len(older)} meses'
            }

        return trends

    def generate_report(self) -> Dict:
        """
        Generate comprehensive prediction report.

        Returns:
            Complete analysis report
        """
        self.load_historical_data()
        self.train_all()

        return {
            'generated_at': datetime.now().isoformat(),
            'lookback_months': self.lookback_months,
            'predictions': self.predict_all_categories(),
            'anomalies': self.detect_anomalies(),
            'trends': self.analyze_trends(),
            'category_stats': self.category_stats
        }


def main():
    """Run predictions and print report."""
    print("=" * 60)
    print("SPENDING PREDICTOR - Análise de Gastos")
    print("=" * 60)

    predictor = SpendingPredictor(lookback_months=6)
    report = predictor.generate_report()

    # Print predictions
    print("\n📊 PREVISÕES PARA O PRÓXIMO MÊS:")
    print("-" * 40)

    predictions = report['predictions']
    for category, pred in sorted(predictions.items()):
        if category.startswith('_'):
            continue
        conf = pred.get('confidence', 0)
        conf_icon = '🟢' if conf > 0.7 else '🟡' if conf > 0.4 else '🔴'
        print(f"{category.title():15} R$ {pred['predicted']:>8,.0f} {conf_icon} ({conf*100:.0f}% conf)")

    total = predictions.get('_total', {})
    print("-" * 40)
    print(f"{'TOTAL':15} R$ {total.get('predicted', 0):>8,.0f}")

    # Print trends
    print("\n📈 TENDÊNCIAS:")
    print("-" * 40)

    for category, trend in report['trends'].items():
        if trend['trend'] == 'increasing':
            icon = '📈'
        elif trend['trend'] == 'decreasing':
            icon = '📉'
        else:
            icon = '➡️'

        print(f"{icon} {category.title():15} {trend.get('description', 'N/A')}")

    # Print anomalies
    anomalies = report['anomalies']
    if anomalies:
        print(f"\n⚠️ ANOMALIAS DETECTADAS ({len(anomalies)}):")
        print("-" * 40)

        for a in anomalies[:5]:  # Top 5
            print(f"  {a['date']} | {a['description'][:30]:30} | R$ {a['amount']:,.0f}")
            print(f"           Motivo: {a['reason']}")

    print("\n" + "=" * 60)

    return report


if __name__ == "__main__":
    main()
