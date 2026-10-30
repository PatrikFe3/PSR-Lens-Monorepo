def create_model_generator(model_type: str):
    if model_type == "CNN":
        return #generate_beam()

    if model_type == "ribbed_cylinder":
        return #ribbedCylinderGenerator()

    raise ValueError(f"Invalid model type: {model_type}")