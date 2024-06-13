import joblib
import numpy as np

# Load the best models and polynomial features
best_models = {
    'circle': joblib.load("slides/mermaid/poly_model/circle_poly_model.pkl"),
    'diamond': joblib.load("slides/mermaid/poly_model/diamond_poly_model.pkl"),
    'double_circle': joblib.load("slides/mermaid/poly_model/double_circle_poly_model.pkl")
}

best_poly_features = {
    'circle': joblib.load("slides/mermaid/poly_model/circle_poly_features.pkl"),
    'diamond': joblib.load("slides/mermaid/poly_model/diamond_poly_features.pkl"),
    'double_circle': joblib.load("slides/mermaid/poly_model/double_circle_poly_features.pkl")
}

# Function for inference
def predict_ideal_lines(shape, chars, words):
    # Check if the shape is valid
    if shape not in best_models or shape not in best_poly_features:
        raise ValueError(f"No model found for shape: {shape}")
    
    # Load the model and polynomial features for the given shape
    model = best_models[shape]
    poly = best_poly_features[shape]
    
    # Prepare the input data
    input_data = np.array([[chars]])
    input_data_poly = poly.transform(input_data)
    
    # Predict using the model
    prediction = model.predict(input_data_poly)[0]
    
    # Apply the min method and ensure the prediction is an integer
    final_prediction = int(min(round(prediction), words))
    
    return final_prediction

# # Example usage
# shape = 'circle'
# chars = 100
# words = 25
# predicted_ideal_lines = predict_ideal_lines(shape, chars, words)
# print(f'Predicted IdealLines for {shape} with {chars} chars and {words} words: {predicted_ideal_lines}')
