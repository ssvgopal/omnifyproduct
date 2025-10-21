"""
AI/ML Enhancements API Routes
Production-grade API endpoints for AI/ML features
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
import pandas as pd
import logging
from datetime import datetime, timedelta
import uuid

from backend.services.ai_ml_enhancements_service import (
    get_ai_ml_enhancements_service, AIMLEnhancementsService,
    ModelType, ModelFramework, PredictionType
)
from backend.core.database import get_database
from backend.core.redis_client import get_redis_client
from backend.core.auth import get_current_user
from backend.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai-ml", tags=["AI/ML Enhancements"])

@router.get("/dashboard")
async def get_ai_ml_dashboard(
    organization_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Get AI/ML dashboard"""
    try:
        service = get_ai_ml_enhancements_service(db, redis_client)
        dashboard = await service.get_ai_ml_dashboard(organization_id)
        
        return JSONResponse(content=dashboard)
        
    except Exception as e:
        logger.error(f"Error getting AI/ML dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/models")
async def create_ml_model(
    model_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Create ML model"""
    try:
        service = get_ai_ml_enhancements_service(db, redis_client)
        model_id = await service.create_ml_model(model_data)
        
        return JSONResponse(content={
            "model_id": model_id,
            "message": "ML model created successfully",
            "status": "created"
        })
        
    except Exception as e:
        logger.error(f"Error creating ML model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/models/{model_id}/train")
async def train_model(
    model_id: str,
    training_request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Train ML model"""
    try:
        service = get_ai_ml_enhancements_service(db, redis_client)
        
        # Convert training data to DataFrame
        training_data = pd.DataFrame(training_request["training_data"])
        target_column = training_request["target_column"]
        
        # Train model
        result = await service.train_model(model_id, training_data, target_column)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error training model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/models/{model_id}/predict")
async def make_prediction(
    model_id: str,
    prediction_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Make prediction using trained model"""
    try:
        service = get_ai_ml_enhancements_service(db, redis_client)
        
        input_data = prediction_request["input_data"]
        prediction = await service.make_prediction(model_id, input_data)
        
        return JSONResponse(content=prediction)
        
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sentiment/analyze")
async def analyze_sentiment(
    sentiment_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Analyze sentiment of texts"""
    try:
        service = get_ai_ml_enhancements_service(db, redis_client)
        
        texts = sentiment_request["texts"]
        results = await service.analyze_sentiment_batch(texts)
        
        return JSONResponse(content={
            "results": results,
            "total_texts": len(texts),
            "analyzed_at": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/anomaly-detection")
async def detect_anomalies(
    anomaly_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Detect anomalies in data"""
    try:
        service = get_ai_ml_enhancements_service(db, redis_client)
        
        # Convert data to DataFrame
        data = pd.DataFrame(anomaly_request["data"])
        method = anomaly_request.get("method", "isolation_forest")
        
        anomalies = await service.detect_anomalies_in_data(data, method)
        
        return JSONResponse(content=anomalies)
        
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def list_ml_models(
    organization_id: str,
    model_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """List ML models"""
    try:
        service = get_ai_ml_enhancements_service(db, redis_client)
        
        # Build query
        query = {}
        if model_type:
            query["model_type"] = model_type
        if status:
            query["status"] = status
        
        # Get models
        models = await db.ml_models.find(query).skip(offset).limit(limit).to_list(length=None)
        total_count = await db.ml_models.count_documents(query)
        
        return JSONResponse(content={
            "models": models,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        })
        
    except Exception as e:
        logger.error(f"Error listing ML models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/{model_id}")
async def get_ml_model(
    model_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Get ML model details"""
    try:
        model = await db.ml_models.find_one({"model_id": model_id})
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        return JSONResponse(content=model)
        
    except Exception as e:
        logger.error(f"Error getting ML model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/models/{model_id}")
async def update_ml_model(
    model_id: str,
    update_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Update ML model"""
    try:
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        result = await db.ml_models.update_one(
            {"model_id": model_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Model not found")
        
        return JSONResponse(content={
            "model_id": model_id,
            "message": "Model updated successfully",
            "status": "updated"
        })
        
    except Exception as e:
        logger.error(f"Error updating ML model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/models/{model_id}")
async def delete_ml_model(
    model_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Delete ML model"""
    try:
        result = await db.ml_models.delete_one({"model_id": model_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Model not found")
        
        return JSONResponse(content={
            "model_id": model_id,
            "message": "Model deleted successfully",
            "status": "deleted"
        })
        
    except Exception as e:
        logger.error(f"Error deleting ML model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model-types")
async def get_model_types():
    """Get supported model types"""
    return JSONResponse(content={
        "model_types": [mt.value for mt in ModelType],
        "frameworks": [mf.value for mf in ModelFramework],
        "prediction_types": [pt.value for pt in PredictionType]
    })

@router.post("/batch-predictions")
async def make_batch_predictions(
    batch_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Make batch predictions"""
    try:
        service = get_ai_ml_enhancements_service(db, redis_client)
        
        model_id = batch_request["model_id"]
        input_data_list = batch_request["input_data"]
        
        predictions = []
        for input_data in input_data_list:
            try:
                prediction = await service.make_prediction(model_id, input_data)
                predictions.append(prediction)
            except Exception as e:
                logger.error(f"Error in batch prediction: {e}")
                predictions.append({
                    "error": str(e),
                    "input_data": input_data
                })
        
        return JSONResponse(content={
            "predictions": predictions,
            "total_predictions": len(predictions),
            "successful_predictions": len([p for p in predictions if "error" not in p]),
            "failed_predictions": len([p for p in predictions if "error" in p])
        })
        
    except Exception as e:
        logger.error(f"Error making batch predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model-performance/{model_id}")
async def get_model_performance(
    model_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Get model performance metrics"""
    try:
        model = await db.ml_models.find_one({"model_id": model_id})
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        # Get prediction history
        predictions = await db.predictions.find({"model_id": model_id}).to_list(length=None)
        
        # Calculate performance metrics
        if predictions:
            accuracies = [p.get("confidence", 0) for p in predictions]
            avg_confidence = sum(accuracies) / len(accuracies)
            
            # Get recent performance trend
            recent_predictions = sorted(predictions, key=lambda x: x.get("created_at", ""), reverse=True)[:10]
            recent_confidence = [p.get("confidence", 0) for p in recent_predictions]
            recent_avg_confidence = sum(recent_confidence) / len(recent_confidence) if recent_confidence else 0
        else:
            avg_confidence = 0
            recent_avg_confidence = 0
        
        return JSONResponse(content={
            "model_id": model_id,
            "model_name": model.get("name", ""),
            "accuracy_score": model.get("accuracy_score", 0),
            "total_predictions": len(predictions),
            "average_confidence": avg_confidence,
            "recent_confidence": recent_avg_confidence,
            "status": model.get("status", ""),
            "created_at": model.get("created_at", ""),
            "updated_at": model.get("updated_at", "")
        })
        
    except Exception as e:
        logger.error(f"Error getting model performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/models/{model_id}/deploy")
async def deploy_model(
    model_id: str,
    deployment_config: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Deploy ML model"""
    try:
        # Update model status to deployed
        result = await db.ml_models.update_one(
            {"model_id": model_id},
            {
                "$set": {
                    "status": "deployed",
                    "deployment_config": deployment_config,
                    "deployed_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Model not found")
        
        return JSONResponse(content={
            "model_id": model_id,
            "message": "Model deployed successfully",
            "status": "deployed",
            "deployment_config": deployment_config
        })
        
    except Exception as e:
        logger.error(f"Error deploying model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/models/{model_id}/retire")
async def retire_model(
    model_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
    redis_client = Depends(get_redis_client)
):
    """Retire ML model"""
    try:
        # Update model status to retired
        result = await db.ml_models.update_one(
            {"model_id": model_id},
            {
                "$set": {
                    "status": "retired",
                    "retired_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Model not found")
        
        return JSONResponse(content={
            "model_id": model_id,
            "message": "Model retired successfully",
            "status": "retired"
        })
        
    except Exception as e:
        logger.error(f"Error retiring model: {e}")
        raise HTTPException(status_code=500, detail=str(e))
