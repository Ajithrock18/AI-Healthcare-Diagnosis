import os
import sys
import argparse
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

# ensure `src` package directory is on path when running from project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from model import create_model


def parse_args():
    p = argparse.ArgumentParser(description="Train chest X-ray classifier")
    p.add_argument("--data-dir", default=os.path.join(SCRIPT_DIR, "..", "data", "chest_xray"),
                   help="Path to chest_xray dataset root (train/val/test)")
    p.add_argument("--image-size", type=int, default=224)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--epochs", type=int, default=10)
    p.add_argument("--save-model", default=os.path.join(SCRIPT_DIR, "best_model.h5"))
    return p.parse_args()


def main():
    args = parse_args()

    train_dir = os.path.join(args.data_dir, "train")
    val_dir = os.path.join(args.data_dir, "val")

    if not os.path.isdir(train_dir):
        raise FileNotFoundError(f"Train directory not found: {train_dir}")

    # Data generators
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255.0,
        rotation_range=15,
        width_shift_range=0.1,
        height_shift_range=0.1,
        shear_range=0.01,
        zoom_range=[0.9, 1.25],
        horizontal_flip=True,
        fill_mode="reflect",
    )

    val_datagen = ImageDataGenerator(rescale=1.0 / 255.0)

    train_gen = train_datagen.flow_from_directory(
        train_dir,
        target_size=(args.image_size, args.image_size),
        batch_size=args.batch_size,
        class_mode="binary",
    )

    val_gen = val_datagen.flow_from_directory(
        val_dir,
        target_size=(args.image_size, args.image_size),
        batch_size=args.batch_size,
        class_mode="binary",
    )

    model = create_model(args.image_size)
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])    

    # Callbacks
    checkpoint = ModelCheckpoint(args.save_model, monitor="val_accuracy", save_best_only=True)
    early = EarlyStopping(monitor="val_accuracy", patience=5, restore_best_weights=True)

    model.fit(
        train_gen,
        epochs=args.epochs,
        validation_data=val_gen,
        callbacks=[checkpoint, early],
    )

    print(f"Training complete. Best model (if saved) is at: {args.save_model}")


if __name__ == "__main__":
    main()

    model.save("saved_model/pneumonia_model.h5")
    print(f"Training complete. Best model (if saved) is at: {args.save_model}")