from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Dict, List, Any, Optional
import numpy as np

app = FastAPI(title="Weaviate Mock Service")

# Mock vector database with some sample data
mock_objects = [
    {
        "id": "1",
        "class": "Document",
        "vector": np.random.rand(128).tolist(),  # 128-dimensional vector
        "properties": {
            "content": "Sample document about AI technology",
            "category": "technology"
        }
    },
    {
        "id": "2",
        "class": "Document",
        "vector": np.random.rand(128).tolist(),
        "properties": {
            "content": "Article about machine learning applications",
            "category": "technology"
        }
    },
    {
        "id": "3",
        "class": "Document",
        "vector": np.random.rand(128).tolist(),
        "properties": {
            "content": "Research paper on natural language processing",
            "category": "research"
        }
    }
]

def validate_float_vector(v: Any) -> List[float]:
    """Validate that input is a list of valid floats."""
    if not isinstance(v, list):
        raise ValueError("Vector must be a list")
    if not v:
        raise ValueError("Vector cannot be empty")
    if len(v) != 128:
        raise ValueError(f"Vector dimension must be 128, got {len(v)}")
    
    try:
        # Try to convert all elements to float
        float_vector = [float(x) for x in v]
        # Check for inf, -inf, nan
        for i, val in enumerate(float_vector):
            if not np.isfinite(val):
                raise ValueError(f"Vector element at index {i} must be a finite number")
        return float_vector
    except (TypeError, ValueError) as e:
        raise ValueError(f"Invalid vector element: {str(e)}")

class VectorQuery(BaseModel):
    vector: List[float] = Field(..., description="Query vector for similarity search")
    class_name: str = Field(..., description="Class name to search in")
    limit: Optional[int] = Field(default=10, description="Maximum number of results to return")
    distance_threshold: Optional[float] = Field(default=0.8, description="Maximum distance threshold")

    @field_validator('vector')
    @classmethod
    def validate_vector(cls, v):
        return validate_float_vector(v)

    @field_validator('limit')
    @classmethod
    def validate_limit(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Limit must be positive")
        return v

    @field_validator('distance_threshold')
    @classmethod
    def validate_threshold(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError("Distance threshold must be between 0 and 1")
        return v

class SearchResult(BaseModel):
    id: str
    class_name: str
    distance: float
    properties: Dict[str, Any]

class SearchResponse(BaseModel):
    results: List[SearchResult]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "weaviate-mock"}

@app.post("/query", response_model=SearchResponse)
async def vector_search(query: VectorQuery):
    """Mock endpoint for vector similarity search"""
    try:
        # Query vector is already validated by Pydantic model
        query_vector = np.array(query.vector)
        
        # Calculate mock distances
        results = []
        for obj in mock_objects:
            if obj["class"] == query.class_name:
                # Calculate cosine similarity
                obj_vector = np.array(obj["vector"])
                distance = 1 - np.dot(query_vector, obj_vector) / (
                    np.linalg.norm(query_vector) * np.linalg.norm(obj_vector)
                )
                
                if distance <= query.distance_threshold:
                    results.append(SearchResult(
                        id=obj["id"],
                        class_name=obj["class"],
                        distance=float(distance),
                        properties=obj["properties"]
                    ))
        
        # Sort by distance and limit results
        results.sort(key=lambda x: x.distance)
        results = results[:query.limit]
        
        return SearchResponse(results=results)
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)