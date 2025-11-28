"""
Machine Learning model for dropout risk prediction
Based on Random Forest classifier with multiple student features
"""
import numpy as np
import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from app.models import Student, Attendance, Grade, Activity, Fee, CounselingNote, db


class DropoutPredictor:
    """Dropout risk prediction using Random Forest"""
    
    def __init__(self, model_path='ml/dropout_model.pkl'):
        self.model_path = model_path
        self.model = None
        self.feature_names = [
            'attendance_percentage',
            'avg_assignment_score',
            'avg_exam_score',
            'avg_project_score',
            'assignment_completion_rate',
            'extracurricular_participation',
            'outstanding_fees_ratio',
            'counseling_concern_level',
            'days_absent',
            'grade_trend',
            'late_submissions',
            'behavioral_incidents'
        ]
        self.load_model()
    
    def load_model(self):
        """Load trained model from disk"""
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            print(f"Model loaded from {self.model_path}")
        else:
            print(f"Model not found at {self.model_path}. Please train the model first.")
            self.model = None
    
    def extract_features(self, student_id):
        """Extract features for a student from database"""
        student = Student.query.get(student_id)
        if not student:
            return None
        
        features = {}
        
        # 1. Attendance percentage
        attendance_records = Attendance.query.filter_by(student_id=student_id).all()
        if attendance_records:
            latest_attendance = attendance_records[-1]
            features['attendance_percentage'] = latest_attendance.attendance_percentage
            features['days_absent'] = latest_attendance.total_days - latest_attendance.present_days
        else:
            features['attendance_percentage'] = 100.0
            features['days_absent'] = 0
        
        # 2. Grade scores
        grades = Grade.query.filter_by(student_id=student_id).all()
        if grades:
            assignments = [g for g in grades if g.grade_type == 'assignment']
            exams = [g for g in grades if g.grade_type == 'exam']
            projects = [g for g in grades if g.grade_type == 'project']
            
            features['avg_assignment_score'] = np.mean([g.percentage for g in assignments]) if assignments else 75.0
            features['avg_exam_score'] = np.mean([g.percentage for g in exams]) if exams else 75.0
            features['avg_project_score'] = np.mean([g.percentage for g in projects]) if projects else 75.0
            
            # Assignment completion rate
            total_assignments = len(assignments)
            features['assignment_completion_rate'] = min(total_assignments / 10.0, 1.0) if total_assignments else 0.5
            
            # Grade trend (simplified: compare recent vs older grades)
            if len(grades) >= 4:
                recent_avg = np.mean([g.percentage for g in grades[-2:]])
                older_avg = np.mean([g.percentage for g in grades[:2]])
                if recent_avg > older_avg + 5:
                    features['grade_trend'] = 1  # improving
                elif recent_avg < older_avg - 5:
                    features['grade_trend'] = -1  # declining
                else:
                    features['grade_trend'] = 0  # stable
            else:
                features['grade_trend'] = 0
            
            # Late submissions (mock - could be tracked separately)
            features['late_submissions'] = max(0, int(total_assignments * 0.2))
        else:
            features['avg_assignment_score'] = 75.0
            features['avg_exam_score'] = 75.0
            features['avg_project_score'] = 75.0
            features['assignment_completion_rate'] = 0.5
            features['grade_trend'] = 0
            features['late_submissions'] = 0
        
        # 3. Extracurricular participation
        activities = Activity.query.filter_by(student_id=student_id).all()
        if activities:
            participation_map = {'none': 0, 'low': 1, 'moderate': 2, 'active': 3}
            avg_participation = np.mean([participation_map.get(a.participation_level, 0) for a in activities])
            features['extracurricular_participation'] = avg_participation
        else:
            features['extracurricular_participation'] = 1.0
        
        # 4. Outstanding fees
        fees = Fee.query.filter_by(student_id=student_id).first()
        if fees:
            features['outstanding_fees_ratio'] = fees.outstanding_ratio
        else:
            features['outstanding_fees_ratio'] = 0.0
        
        # 5. Counseling concern level
        counseling_notes = CounselingNote.query.filter_by(student_id=student_id).all()
        if counseling_notes:
            concern_map = {'low': 0, 'medium': 1, 'high': 2}
            avg_concern = np.mean([concern_map.get(note.concern_level, 0) for note in counseling_notes])
            features['counseling_concern_level'] = avg_concern
            features['behavioral_incidents'] = len([n for n in counseling_notes if n.concern_level in ['medium', 'high']])
        else:
            features['counseling_concern_level'] = 0
            features['behavioral_incidents'] = 0
        
        return features
    
    def predict_risk(self, student_id):
        """Predict dropout risk for a student"""
        features = self.extract_features(student_id)
        if not features:
            return None
        
        # Rule-based risk factors
        risk_factors = []
        base_risk_level = 'low'
        
        # Hard rules
        if features['attendance_percentage'] < 75:
            risk_factors.append(f"Low attendance: {features['attendance_percentage']:.1f}%")
            base_risk_level = 'medium'
        
        if features['avg_exam_score'] < 40:
            risk_factors.append(f"Failing grades: {features['avg_exam_score']:.1f}%")
            base_risk_level = 'high'
        
        if features['outstanding_fees_ratio'] > 0.5:
            risk_factors.append(f"Outstanding fees: {features['outstanding_fees_ratio']*100:.0f}%")
        
        if features['counseling_concern_level'] >= 1.5:
            risk_factors.append("High counseling concern level")
            base_risk_level = 'high'
        
        if features['assignment_completion_rate'] < 0.5:
            risk_factors.append(f"Low assignment completion: {features['assignment_completion_rate']*100:.0f}%")
        
        if features['grade_trend'] == -1:
            risk_factors.append("Declining grade trend")
        
        if features['extracurricular_participation'] < 1:
            risk_factors.append("No extracurricular participation")
        
        # ML prediction (if model is loaded)
        ml_risk_level = base_risk_level
        ml_probability = [0.7, 0.2, 0.1]  # Default probabilities [low, medium, high]
        
        if self.model:
            # Prepare feature vector
            feature_vector = np.array([[
                features[name] for name in self.feature_names
            ]])
            
            # Predict
            ml_prediction = self.model.predict(feature_vector)[0]
            ml_probability = self.model.predict_proba(feature_vector)[0]
            
            # Map prediction to risk level
            risk_map = {0: 'low', 1: 'medium', 2: 'high'}
            ml_risk_level = risk_map.get(ml_prediction, 'low')
        
        # Combine rule-based and ML predictions (take the higher risk)
        risk_priority = {'low': 0, 'medium': 1, 'high': 2}
        final_risk_level = base_risk_level if risk_priority[base_risk_level] > risk_priority[ml_risk_level] else ml_risk_level
        
        # Calculate final risk score
        risk_score = ml_probability[risk_priority[final_risk_level]]
        
        return {
            'risk_level': final_risk_level,
            'risk_score': float(risk_score),
            'contributing_factors': risk_factors,
            'ml_probabilities': {
                'low': float(ml_probability[0]),
                'medium': float(ml_probability[1]),
                'high': float(ml_probability[2])
            },
            'features': features
        }


# Global predictor instance
predictor = DropoutPredictor()
