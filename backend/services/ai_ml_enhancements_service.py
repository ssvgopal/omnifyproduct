"""
AI/ML Enhancements System
Production-grade AI models, machine learning pipelines, and predictive analytics
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import numpy as np
import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
import redis
import aiohttp
import pickle
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import torch
import torch.nn as nn
import torch.optim as optim
from transformers import pipeline, AutoTokenizer, AutoModel
import openai
import anthropic
import cohere
import requests
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

logger = logging.getLogger(__name__)

class ModelType(str, Enum):
    """AI/ML model types"""
    REGRESSION = "regression"
    CLASSIFICATION = "classification"
    CLUSTERING = "clustering"
    TIME_SERIES = "time_series"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    RECOMMENDATION = "recommendation"
    ANOMALY_DETECTION = "anomaly_detection"

class ModelFramework(str, Enum):
    """ML frameworks"""
    SCIKIT_LEARN = "scikit_learn"
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"
    TRANSFORMERS = "transformers"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"

class ModelStatus(str, Enum):
    """Model status"""
    TRAINING = "training"
    TRAINED = "trained"
    DEPLOYED = "deployed"
    FAILED = "failed"
    RETIRED = "retired"

class PredictionType(str, Enum):
    """Prediction types"""
    CAMPAIGN_PERFORMANCE = "campaign_performance"
    CUSTOMER_LTV = "customer_ltv"
    CHURN_PREDICTION = "churn_prediction"
    CONVERSION_PREDICTION = "conversion_prediction"
    PRICE_OPTIMIZATION = "price_optimization"
    CONTENT_RECOMMENDATION = "content_recommendation"
    ANOMALY_DETECTION = "anomaly_detection"
    SENTIMENT_ANALYSIS = "sentiment_analysis"

@dataclass
class MLModel:
    """ML model definition"""
    model_id: str
    name: str
    description: str
    model_type: ModelType
    framework: ModelFramework
    status: ModelStatus
    version: str
    training_data_size: int
    accuracy_score: Optional[float]
    created_at: datetime
    updated_at: datetime
    hyperparameters: Dict[str, Any]
    feature_importance: Optional[Dict[str, float]]

@dataclass
class PredictionRequest:
    """Prediction request"""
    request_id: str
    model_id: str
    input_data: Dict[str, Any]
    prediction_type: PredictionType
    confidence_threshold: float
    created_at: datetime

@dataclass
class PredictionResult:
    """Prediction result"""
    prediction_id: str
    request_id: str
    model_id: str
    prediction: Any
    confidence: float
    feature_contributions: Optional[Dict[str, float]]
    created_at: datetime

class DataPreprocessor:
    """Data preprocessing for ML models"""
    
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        self.feature_columns = {}
    
    def preprocess_campaign_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Preprocess campaign data for ML"""
        try:
            # Handle missing values
            data = data.fillna(data.mean())
            
            # Encode categorical variables
            categorical_columns = data.select_dtypes(include=['object']).columns
            for col in categorical_columns:
                if col not in self.encoders:
                    self.encoders[col] = LabelEncoder()
                data[col] = self.encoders[col].fit_transform(data[col].astype(str))
            
            # Scale numerical features
            numerical_columns = data.select_dtypes(include=[np.number]).columns
            scaler = StandardScaler()
            data[numerical_columns] = scaler.fit_transform(data[numerical_columns])
            self.scalers['campaign'] = scaler
            
            return data
            
        except Exception as e:
            logger.error(f"Error preprocessing campaign data: {e}")
            raise
    
    def preprocess_customer_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Preprocess customer data for ML"""
        try:
            # Handle missing values
            data = data.fillna(data.median())
            
            # Create derived features
            if 'age' in data.columns and 'income' in data.columns:
                data['income_age_ratio'] = data['income'] / (data['age'] + 1)
            
            if 'purchase_history' in data.columns:
                data['avg_purchase_value'] = data['purchase_history'].apply(
                    lambda x: np.mean(x) if isinstance(x, list) and len(x) > 0 else 0
                )
            
            # Encode categorical variables
            categorical_columns = data.select_dtypes(include=['object']).columns
            for col in categorical_columns:
                if col not in self.encoders:
                    self.encoders[col] = LabelEncoder()
                data[col] = self.encoders[col].fit_transform(data[col].astype(str))
            
            # Scale numerical features
            numerical_columns = data.select_dtypes(include=[np.number]).columns
            scaler = StandardScaler()
            data[numerical_columns] = scaler.fit_transform(data[numerical_columns])
            self.scalers['customer'] = scaler
            
            return data
            
        except Exception as e:
            logger.error(f"Error preprocessing customer data: {e}")
            raise

class ModelTrainer:
    """ML model training and management"""
    
    def __init__(self):
        self.models = {}
        self.training_history = {}
    
    async def train_campaign_performance_model(self, data: pd.DataFrame, target_column: str) -> str:
        """Train campaign performance prediction model"""
        try:
            model_id = str(uuid.uuid4())
            
            # Prepare data
            X = data.drop(columns=[target_column])
            y = data[target_column]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train multiple models
            models = {
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'linear_regression': LinearRegression()
            }
            
            best_model = None
            best_score = -np.inf
            best_model_name = None
            
            for name, model in models.items():
                model.fit(X_train, y_train)
                score = model.score(X_test, y_test)
                
                if score > best_score:
                    best_score = score
                    best_model = model
                    best_model_name = name
            
            # Save model
            self.models[model_id] = {
                'model': best_model,
                'model_name': best_model_name,
                'score': best_score,
                'feature_columns': list(X.columns),
                'target_column': target_column
            }
            
            # Store training history
            self.training_history[model_id] = {
                'model_id': model_id,
                'model_name': best_model_name,
                'score': best_score,
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'created_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Trained campaign performance model {model_id}: {best_model_name} (score: {best_score:.3f})")
            return model_id
            
        except Exception as e:
            logger.error(f"Error training campaign performance model: {e}")
            raise
    
    async def train_customer_ltv_model(self, data: pd.DataFrame, target_column: str) -> str:
        """Train customer LTV prediction model"""
        try:
            model_id = str(uuid.uuid4())
            
            # Prepare data
            X = data.drop(columns=[target_column])
            y = data[target_column]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train model
            model = GradientBoostingRegressor(n_estimators=200, learning_rate=0.1, random_state=42)
            model.fit(X_train, y_train)
            
            # Evaluate model
            score = model.score(X_test, y_test)
            
            # Save model
            self.models[model_id] = {
                'model': model,
                'model_name': 'gradient_boosting',
                'score': score,
                'feature_columns': list(X.columns),
                'target_column': target_column
            }
            
            # Store training history
            self.training_history[model_id] = {
                'model_id': model_id,
                'model_name': 'gradient_boosting',
                'score': score,
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'created_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Trained customer LTV model {model_id} (score: {score:.3f})")
            return model_id
            
        except Exception as e:
            logger.error(f"Error training customer LTV model: {e}")
            raise
    
    async def train_churn_prediction_model(self, data: pd.DataFrame, target_column: str) -> str:
        """Train customer churn prediction model"""
        try:
            model_id = str(uuid.uuid4())
            
            # Prepare data
            X = data.drop(columns=[target_column])
            y = data[target_column]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Evaluate model
            score = model.score(X_test, y_test)
            
            # Save model
            self.models[model_id] = {
                'model': model,
                'model_name': 'random_forest',
                'score': score,
                'feature_columns': list(X.columns),
                'target_column': target_column
            }
            
            # Store training history
            self.training_history[model_id] = {
                'model_id': model_id,
                'model_name': 'random_forest',
                'score': score,
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'created_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Trained churn prediction model {model_id} (score: {score:.3f})")
            return model_id
            
        except Exception as e:
            logger.error(f"Error training churn prediction model: {e}")
            raise

class DeepLearningTrainer:
    """Deep learning model training"""
    
    def __init__(self):
        self.models = {}
        self.training_history = {}
    
    async def train_neural_network(self, data: pd.DataFrame, target_column: str, model_type: str = "regression") -> str:
        """Train neural network model"""
        try:
            model_id = str(uuid.uuid4())
            
            # Prepare data
            X = data.drop(columns=[target_column])
            y = data[target_column]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Build model
            model = keras.Sequential([
                layers.Dense(128, activation='relu', input_shape=(X.shape[1],)),
                layers.Dropout(0.3),
                layers.Dense(64, activation='relu'),
                layers.Dropout(0.3),
                layers.Dense(32, activation='relu'),
                layers.Dense(1 if model_type == "regression" else len(np.unique(y)))
            ])
            
            # Compile model
            if model_type == "regression":
                model.compile(optimizer='adam', loss='mse', metrics=['mae'])
            else:
                model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
            
            # Train model
            history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2, verbose=0)
            
            # Evaluate model
            if model_type == "regression":
                score = model.evaluate(X_test, y_test, verbose=0)[1]  # MAE
            else:
                score = model.evaluate(X_test, y_test, verbose=0)[1]  # Accuracy
            
            # Save model
            self.models[model_id] = {
                'model': model,
                'model_name': 'neural_network',
                'score': score,
                'feature_columns': list(X.columns),
                'target_column': target_column,
                'model_type': model_type
            }
            
            # Store training history
            self.training_history[model_id] = {
                'model_id': model_id,
                'model_name': 'neural_network',
                'score': score,
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'epochs': 50,
                'created_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Trained neural network {model_id} (score: {score:.3f})")
            return model_id
            
        except Exception as e:
            logger.error(f"Error training neural network: {e}")
            raise

class NLPProcessor:
    """Natural Language Processing"""
    
    def __init__(self):
        self.sentiment_analyzer = None
        self.text_classifier = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize NLP models"""
        try:
            # Initialize sentiment analysis
            self.sentiment_analyzer = pipeline("sentiment-analysis")
            
            # Initialize text classification
            self.text_classifier = pipeline("text-classification")
            
        except Exception as e:
            logger.error(f"Error initializing NLP models: {e}")
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        try:
            if not self.sentiment_analyzer:
                return {"sentiment": "neutral", "confidence": 0.5}
            
            result = self.sentiment_analyzer(text)
            
            return {
                "sentiment": result[0]["label"].lower(),
                "confidence": result[0]["score"],
                "text": text
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {"sentiment": "neutral", "confidence": 0.5}
    
    async def classify_text(self, text: str, categories: List[str] = None) -> Dict[str, Any]:
        """Classify text into categories"""
        try:
            if not self.text_classifier:
                return {"category": "unknown", "confidence": 0.5}
            
            result = self.text_classifier(text)
            
            return {
                "category": result[0]["label"],
                "confidence": result[0]["score"],
                "text": text
            }
            
        except Exception as e:
            logger.error(f"Error classifying text: {e}")
            return {"category": "unknown", "confidence": 0.5}
    
    async def extract_keywords(self, text: str, num_keywords: int = 10) -> List[str]:
        """Extract keywords from text"""
        try:
            # Simple keyword extraction (in production, use more sophisticated methods)
            words = text.lower().split()
            word_freq = {}
            
            for word in words:
                if len(word) > 3:  # Filter short words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Sort by frequency
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            
            return [word for word, freq in sorted_words[:num_keywords]]
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []

class AnomalyDetector:
    """Anomaly detection system"""
    
    def __init__(self):
        self.models = {}
        self.thresholds = {}
    
    async def detect_anomalies(self, data: pd.DataFrame, method: str = "isolation_forest") -> Dict[str, Any]:
        """Detect anomalies in data"""
        try:
            from sklearn.ensemble import IsolationForest
            from sklearn.cluster import DBSCAN
            
            if method == "isolation_forest":
                model = IsolationForest(contamination=0.1, random_state=42)
                anomalies = model.fit_predict(data)
                
                # Convert to boolean (1 = normal, -1 = anomaly)
                is_anomaly = anomalies == -1
                
            elif method == "dbscan":
                model = DBSCAN(eps=0.5, min_samples=5)
                clusters = model.fit_predict(data)
                
                # Points with cluster -1 are outliers
                is_anomaly = clusters == -1
                
            else:
                raise ValueError(f"Unsupported anomaly detection method: {method}")
            
            anomaly_indices = np.where(is_anomaly)[0]
            anomaly_data = data.iloc[anomaly_indices] if len(anomaly_indices) > 0 else pd.DataFrame()
            
            return {
                "anomaly_count": len(anomaly_indices),
                "anomaly_percentage": len(anomaly_indices) / len(data) * 100,
                "anomaly_indices": anomaly_indices.tolist(),
                "anomaly_data": anomaly_data.to_dict('records'),
                "method": method
            }
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return {"anomaly_count": 0, "anomaly_percentage": 0, "anomaly_indices": [], "anomaly_data": []}

class RecommendationEngine:
    """Recommendation system"""
    
    def __init__(self):
        self.models = {}
        self.user_item_matrix = None
    
    async def train_collaborative_filtering(self, user_data: pd.DataFrame, item_data: pd.DataFrame, 
                                          interaction_data: pd.DataFrame) -> str:
        """Train collaborative filtering model"""
        try:
            model_id = str(uuid.uuid4())
            
            # Create user-item matrix
            user_item_matrix = interaction_data.pivot_table(
                index='user_id', 
                columns='item_id', 
                values='rating', 
                fill_value=0
            )
            
            # Train model using matrix factorization
            from sklearn.decomposition import NMF
            
            model = NMF(n_components=50, random_state=42)
            model.fit(user_item_matrix)
            
            # Save model
            self.models[model_id] = {
                'model': model,
                'user_item_matrix': user_item_matrix,
                'model_name': 'collaborative_filtering'
            }
            
            logger.info(f"Trained collaborative filtering model {model_id}")
            return model_id
            
        except Exception as e:
            logger.error(f"Error training collaborative filtering model: {e}")
            raise
    
    async def get_recommendations(self, user_id: str, model_id: str, num_recommendations: int = 10) -> List[str]:
        """Get recommendations for user"""
        try:
            if model_id not in self.models:
                raise ValueError(f"Model {model_id} not found")
            
            model = self.models[model_id]['model']
            user_item_matrix = self.models[model_id]['user_item_matrix']
            
            # Get user preferences
            if user_id in user_item_matrix.index:
                user_preferences = user_item_matrix.loc[user_id]
                
                # Generate recommendations
                recommendations = model.transform(user_preferences.values.reshape(1, -1))
                
                # Get top recommendations
                top_items = np.argsort(recommendations[0])[-num_recommendations:][::-1]
                
                return [str(item) for item in top_items]
            else:
                # Return popular items for new users
                popular_items = user_item_matrix.sum().sort_values(ascending=False).head(num_recommendations)
                return [str(item) for item in popular_items.index]
                
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []

class AIMLEnhancementsService:
    """Main service for AI/ML enhancements"""
    
    def __init__(self, db: AsyncIOMotorClient, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client
        self.data_preprocessor = DataPreprocessor()
        self.model_trainer = ModelTrainer()
        self.deep_learning_trainer = DeepLearningTrainer()
        self.nlp_processor = NLPProcessor()
        self.anomaly_detector = AnomalyDetector()
        self.recommendation_engine = RecommendationEngine()
    
    async def create_ml_model(self, model_data: Dict[str, Any]) -> str:
        """Create ML model"""
        try:
            model_id = str(uuid.uuid4())
            
            model = MLModel(
                model_id=model_id,
                name=model_data["name"],
                description=model_data.get("description", ""),
                model_type=ModelType(model_data["model_type"]),
                framework=ModelFramework(model_data["framework"]),
                status=ModelStatus.TRAINING,
                version=model_data.get("version", "1.0.0"),
                training_data_size=model_data.get("training_data_size", 0),
                accuracy_score=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                hyperparameters=model_data.get("hyperparameters", {}),
                feature_importance=None
            )
            
            model_doc = {
                "model_id": model_id,
                "name": model.name,
                "description": model.description,
                "model_type": model.model_type.value,
                "framework": model.framework.value,
                "status": model.status.value,
                "version": model.version,
                "training_data_size": model.training_data_size,
                "accuracy_score": model.accuracy_score,
                "created_at": model.created_at.isoformat(),
                "updated_at": model.updated_at.isoformat(),
                "hyperparameters": model.hyperparameters,
                "feature_importance": model.feature_importance
            }
            
            await self.db.ml_models.insert_one(model_doc)
            
            logger.info(f"Created ML model {model_id}: {model.name}")
            return model_id
            
        except Exception as e:
            logger.error(f"Error creating ML model: {e}")
            raise
    
    async def train_model(self, model_id: str, training_data: pd.DataFrame, target_column: str) -> Dict[str, Any]:
        """Train ML model"""
        try:
            # Get model
            model_doc = await self.db.ml_models.find_one({"model_id": model_id})
            if not model_doc:
                raise ValueError(f"Model {model_id} not found")
            
            # Preprocess data
            processed_data = self.data_preprocessor.preprocess_campaign_data(training_data)
            
            # Train model based on type
            if model_doc["model_type"] == ModelType.REGRESSION.value:
                trained_model_id = await self.model_trainer.train_campaign_performance_model(
                    processed_data, target_column
                )
            elif model_doc["model_type"] == ModelType.CLASSIFICATION.value:
                trained_model_id = await self.model_trainer.train_churn_prediction_model(
                    processed_data, target_column
                )
            else:
                raise ValueError(f"Unsupported model type: {model_doc['model_type']}")
            
            # Update model status
            await self.db.ml_models.update_one(
                {"model_id": model_id},
                {
                    "$set": {
                        "status": ModelStatus.TRAINED.value,
                        "trained_model_id": trained_model_id,
                        "updated_at": datetime.utcnow().isoformat()
                    }
                }
            )
            
            return {
                "model_id": model_id,
                "trained_model_id": trained_model_id,
                "status": "trained",
                "training_samples": len(training_data)
            }
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            raise
    
    async def make_prediction(self, model_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction using trained model"""
        try:
            # Get model
            model_doc = await self.db.ml_models.find_one({"model_id": model_id})
            if not model_doc:
                raise ValueError(f"Model {model_id} not found")
            
            if model_doc["status"] != ModelStatus.TRAINED.value:
                raise ValueError(f"Model {model_id} is not trained")
            
            # Get trained model
            trained_model_id = model_doc.get("trained_model_id")
            if not trained_model_id or trained_model_id not in self.model_trainer.models:
                raise ValueError(f"Trained model not found for {model_id}")
            
            model_info = self.model_trainer.models[trained_model_id]
            model = model_info['model']
            feature_columns = model_info['feature_columns']
            
            # Prepare input data
            input_df = pd.DataFrame([input_data])
            
            # Ensure all required features are present
            for col in feature_columns:
                if col not in input_df.columns:
                    input_df[col] = 0  # Default value
            
            # Reorder columns to match training data
            input_df = input_df[feature_columns]
            
            # Make prediction
            prediction = model.predict(input_df)[0]
            
            # Calculate confidence (simplified)
            confidence = 0.8  # In production, calculate actual confidence
            
            return {
                "model_id": model_id,
                "prediction": float(prediction),
                "confidence": confidence,
                "input_data": input_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            raise
    
    async def analyze_sentiment_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze sentiment for multiple texts"""
        try:
            results = []
            
            for text in texts:
                sentiment_result = await self.nlp_processor.analyze_sentiment(text)
                results.append(sentiment_result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment batch: {e}")
            raise
    
    async def detect_anomalies_in_data(self, data: pd.DataFrame, method: str = "isolation_forest") -> Dict[str, Any]:
        """Detect anomalies in dataset"""
        try:
            anomaly_result = await self.anomaly_detector.detect_anomalies(data, method)
            
            return anomaly_result
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            raise
    
    async def get_ai_ml_dashboard(self, organization_id: str) -> Dict[str, Any]:
        """Get AI/ML dashboard"""
        try:
            # Get model statistics
            total_models = await self.db.ml_models.count_documents({})
            trained_models = await self.db.ml_models.count_documents({"status": ModelStatus.TRAINED.value})
            deployed_models = await self.db.ml_models.count_documents({"status": ModelStatus.DEPLOYED.value})
            
            # Get recent models
            recent_models = await self.db.ml_models.find({}).sort("created_at", -1).limit(10).to_list(length=None)
            
            # Get model performance statistics
            model_performance = {}
            for model in recent_models:
                if model.get("accuracy_score"):
                    model_type = model["model_type"]
                    if model_type not in model_performance:
                        model_performance[model_type] = []
                    model_performance[model_type].append(model["accuracy_score"])
            
            # Calculate average performance by type
            avg_performance = {}
            for model_type, scores in model_performance.items():
                avg_performance[model_type] = np.mean(scores) if scores else 0
            
            return {
                "organization_id": organization_id,
                "model_statistics": {
                    "total_models": total_models,
                    "trained_models": trained_models,
                    "deployed_models": deployed_models,
                    "training_success_rate": trained_models / total_models if total_models > 0 else 0
                },
                "model_performance": avg_performance,
                "recent_models": recent_models,
                "supported_model_types": [mt.value for mt in ModelType],
                "supported_frameworks": [mf.value for mf in ModelFramework],
                "supported_predictions": [pt.value for pt in PredictionType],
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting AI/ML dashboard: {e}")
            raise

# Global instance
ai_ml_enhancements_service = None

def get_ai_ml_enhancements_service(db: AsyncIOMotorClient, redis_client: redis.Redis) -> AIMLEnhancementsService:
    """Get AI/ML enhancements service instance"""
    global ai_ml_enhancements_service
    if ai_ml_enhancements_service is None:
        ai_ml_enhancements_service = AIMLEnhancementsService(db, redis_client)
    return ai_ml_enhancements_service
