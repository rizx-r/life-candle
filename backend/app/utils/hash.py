import hashlib
import json
from app.models.schemas import UserInput

def hash_user_input(input_data: UserInput) -> str:
    # Exclude apiBaseUrl and apiKey as they don't affect the analysis result content
    # assuming modelName might affect it, so keep it.
    # actually user might want same result for same input params regardless of API key.
    
    data_dict = input_data.model_dump(exclude={'apiBaseUrl', 'apiKey'})
    
    # Sort keys to ensure consistent order
    json_str = json.dumps(data_dict, sort_keys=True, default=str)
    return hashlib.sha256(json_str.encode()).hexdigest()
