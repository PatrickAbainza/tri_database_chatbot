from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from enum import Enum
import re

app = FastAPI(title="Relational Mock Service")

# Mock database tables with sample data
mock_data = {
    "users": [
        {"id": 1, "username": "john_doe", "email": "john@example.com", "active": True},
        {"id": 2, "username": "jane_smith", "email": "jane@example.com", "active": True},
        {"id": 3, "username": "bob_wilson", "email": "bob@example.com", "active": False}
    ],
    "posts": [
        {"id": 1, "user_id": 1, "title": "First Post", "content": "Hello World!"},
        {"id": 2, "user_id": 1, "title": "Second Post", "content": "Another post"},
        {"id": 3, "user_id": 2, "title": "Jane's Post", "content": "My first post"}
    ],
    "comments": [
        {"id": 1, "post_id": 1, "user_id": 2, "content": "Great post!"},
        {"id": 2, "post_id": 1, "user_id": 3, "content": "Thanks for sharing"},
        {"id": 3, "post_id": 2, "user_id": 2, "content": "Interesting"}
    ]
}

class QueryType(str, Enum):
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

class QueryRequest(BaseModel):
    query: str = Field(..., description="SQL query to execute")
    query_type: QueryType = Field(..., description="Type of SQL query")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Query parameters")

class QueryResponse(BaseModel):
    results: Optional[List[Dict[str, Any]]] = Field(default=None, description="Query results")
    affected_rows: Optional[int] = Field(default=None, description="Number of affected rows")
    message: Optional[str] = Field(default=None, description="Additional information")

def validate_parameters(parameters: Dict[str, Any], expected_types: Dict[str, type]) -> bool:
    """Validate parameter types against expected types."""
    if not parameters:
        return True
    
    for param_name, expected_type in expected_types.items():
        if param_name in parameters:
            value = parameters[param_name]
            if not isinstance(value, expected_type):
                raise ValueError(f"Parameter '{param_name}' must be of type {expected_type.__name__}")
    return True

def parse_select_columns(query: str) -> List[str]:
    """Parse column names from SELECT clause."""
    match = re.search(r"SELECT\s+(.*?)\s+FROM", query, re.IGNORECASE | re.DOTALL)
    if not match:
        return ["*"]
    columns_str = match.group(1).strip()
    if columns_str == "*":
        return ["*"]
    columns = []
    for col in columns_str.split(','):
        col = col.strip()
        if '.' in col:
            # Handle table aliases
            alias, col_name = col.split('.')
            columns.append(col_name)
        else:
            columns.append(col)
    return columns

def parse_join_tables(query: str) -> List[str]:
    """Parse table names from JOIN clauses."""
    tables = []
    # Match table name after FROM
    from_match = re.search(r"FROM\s+(\w+)(?:\s+\w+)?", query, re.IGNORECASE)
    if from_match:
        tables.append(from_match.group(1))
    
    # Match table names after JOIN
    join_matches = re.finditer(r"JOIN\s+(\w+)(?:\s+\w+)?", query, re.IGNORECASE)
    for match in join_matches:
        tables.append(match.group(1))
    
    return tables

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "relational-mock"}

@app.post("/query", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    """Mock endpoint for executing SQL queries"""
    try:
        if request.query_type == QueryType.SELECT:
            columns = parse_select_columns(request.query)
            tables = parse_join_tables(request.query)
            
            if not tables:
                raise ValueError("No tables specified in query")

            results = []
            primary_table = tables[0]
            if primary_table not in mock_data:
                return QueryResponse(
                    results=[],
                    message="No data found"
                )

            if len(tables) == 1:
                # Simple SELECT
                results = mock_data[primary_table]
                if columns != ["*"]:
                    # Filter columns
                    results = [{k: row[k] for k in columns if k in row} for row in results]
            else:
                # JOIN operation
                join_table = tables[1]
                if join_table not in mock_data:
                    raise ValueError(f"Table {join_table} not found")

                # Perform JOIN
                for primary_row in mock_data[primary_table]:
                    for join_row in mock_data[join_table]:
                        if (join_table == "posts" and join_row["user_id"] == primary_row["id"]) or \
                           (join_table == "comments" and join_row["user_id"] == primary_row["id"]):
                            # Create joined result
                            result = {}
                            if columns == ["*"]:
                                result.update(primary_row)
                                result.update(join_row)
                            else:
                                for col in columns:
                                    if col in primary_row:
                                        result[col] = primary_row[col]
                                    if col in join_row:
                                        result[col] = join_row[col]
                            if "active" in request.query.lower():
                                if primary_row.get("active", True):  # Only include if active is True
                                    results.append(result)
                            else:
                                results.append(result)
            
            return QueryResponse(
                results=results,
                message="No data found" if not results else None
            )
        
        elif request.query_type == QueryType.INSERT:
            # Check if we're testing data types
            if "test_types" in request.query:
                expected_types = {
                    "int_val": int,
                    "float_val": float,
                    "text_val": str,
                    "bool_val": bool,
                }
                validate_parameters(request.parameters, expected_types)
            elif "users" in request.query:
                expected_types = {
                    "id": int,
                    "active": bool
                }
                if not validate_parameters(request.parameters, expected_types):
                    raise ValueError("Invalid parameter types")
            
            return QueryResponse(
                affected_rows=1,
                message="Record inserted successfully"
            )
        
        elif request.query_type == QueryType.UPDATE:
            return QueryResponse(
                affected_rows=2,
                message="Records updated successfully"
            )
        
        elif request.query_type == QueryType.DELETE:
            return QueryResponse(
                affected_rows=1,
                message="Record deleted successfully"
            )
        
        raise HTTPException(status_code=400, detail="Invalid query type")
        
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)