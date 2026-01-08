from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout


def create_model(image_size: int = 224) -> Sequential:
    """Create a simple CNN for binary classification.

    Args:
        image_size: int image height and width (assumes square images)

    Returns:
        Compiled Keras Sequential model (not compiled here).
    """
    input_shape = (image_size, image_size, 3)
    model = Sequential([
        Conv2D(32, (3, 3), activation="relu", input_shape=input_shape),
        MaxPooling2D(2, 2),
        Conv2D(64, (3, 3), activation="relu"),
        MaxPooling2D(2, 2),
        Conv2D(128, (3, 3), activation="relu"),
        MaxPooling2D(2, 2),
        Flatten(),
        Dense(128, activation="relu"),
        Dropout(0.5),
        Dense(1, activation="sigmoid"),
    ])
    return model
