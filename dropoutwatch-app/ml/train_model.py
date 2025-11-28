"""
Train Random Forest model for dropout prediction
"""
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from app import create_app
from app.models import Student
from app.ml_model import DropoutPredictor

app = create_app()


def train_model():
    """Train Random Forest model on student data"""
    with app.app_context():
        print("Loading student data...")
        students = Student.query.all()
        
        if len(students) < 10:
            print("Not enough students to train model. Please generate demo data first.")
            return
        
        # Extract features for all students
        predictor = DropoutPredictor()
        
        X = []
        y = []
        
        for student in students:
            features = predictor.extract_features(student.id)
            if features:
                # Create feature vector
                feature_vector = [features[name] for name in predictor.feature_names]
                X.append(feature_vector)
                
                # Determine ground truth label based on risk factors
                # This is synthetic - in real scenario, you'd have historical dropout data
                attendance = features['attendance_percentage']
                avg_grade = (features['avg_assignment_score'] + features['avg_exam_score']) / 2
                
                if attendance < 70 or avg_grade < 40:
                    label = 2  # high risk
                elif attendance < 80 or avg_grade < 60:
                    label = 1  # medium risk
                else:
                    label = 0  # low risk
                
                y.append(label)
        
        X = np.array(X)
        y = np.array(y)
        
        print(f"Dataset shape: {X.shape}")
        print(f"Class distribution: {np.bincount(y)}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print("\nTraining Random Forest model...")
        
        # Train model
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            class_weight='balanced',  # Handle imbalanced classes
            n_jobs=-1
        )
        
        rf_model.fit(X_train, y_train)
        
        # Evaluate
        print("\nModel Evaluation:")
        print("=" * 50)
        
        # Training accuracy
        train_score = rf_model.score(X_train, y_train)
        print(f"Training Accuracy: {train_score:.3f}")
        
        # Test accuracy
        test_score = rf_model.score(X_test, y_test)
        print(f"Test Accuracy: {test_score:.3f}")
        
        # Cross-validation
        cv_scores = cross_val_score(rf_model, X, y, cv=5)
        print(f"Cross-Validation Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")
        
        # Predictions
        y_pred = rf_model.predict(X_test)
        
        # Classification report
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Low Risk', 'Medium Risk', 'High Risk']))
        
        # Confusion matrix
        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        
        # Feature importance
        print("\nFeature Importance:")
        feature_importance = sorted(
            zip(predictor.feature_names, rf_model.feature_importances_),
            key=lambda x: x[1],
            reverse=True
        )
        for feature, importance in feature_importance:
            print(f"  {feature:30s}: {importance:.4f}")
        
        # Save model
        model_path = 'ml/dropout_model.pkl'
        joblib.dump(rf_model, model_path)
        print(f"\n✅ Model saved to {model_path}")
        
        return rf_model


if __name__ == '__main__':
    train_model()
