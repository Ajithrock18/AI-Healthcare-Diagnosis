# AI Healthcare Diagnosis

This repository contains a small chest X-ray binary classifier (NORMAL vs PNEUMONIA) and helper scripts to train and run predictions.

**Project layout**

- `data/` — dataset directory (not included). Expected structure:
  - `chest_xray/`
    - `train/` with class subfolders (e.g. `NORMAL/`, `PNEUMONIA/`)
    - `val/` with class subfolders
    - `test/` with class subfolders
- `src/` — source code
  - `src/model.py` — defines `create_model(image_size=...)`
  - `src/train.py` — CLI training script (uses generators, checkpoints, early stopping)
  - `src/predict.py` — CLI prediction script for single images
- `notebooks/` — exploratory notebooks
- `requirements.txt` — Python dependencies

**Quick start**

1. Create and activate a virtual environment (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Prepare your dataset under `data/chest_xray` following the structure above.

4. Train the model (example):

```powershell
python .\src\train.py --data-dir ".\data\chest_xray" --image-size 224 --batch-size 32 --epochs 10 --save-model ".\models\chest_xray_best.h5"
```

This will save the best model to the path given by `--save-model`.

5. Predict a single image:

```powershell
python .\src\predict.py .\data\chest_xray\test\NORMAL\some_image.jpeg --model .\models\chest_xray_best.h5 --image-size 224
```

**Notes & tips**

- The default model is a simple CNN suitable for demonstration. For production/clinical use, use validated architectures and clinical evaluation.
- If you have GPU support and want GPU-accelerated TensorFlow, install the appropriate `tensorflow` GPU package or a matching wheel for your CUDA/cuDNN setup.
- `requirements.txt` contains recommended packages. Pin exact versions if you need reproducible installs.
- To preserve class label mapping for prediction, you can modify `src/train.py` to save `train_gen.class_indices` to disk and load them in `src/predict.py`.

**Development**

- Run notebooks in `notebooks/` for data exploration and model experiments.
- Add unit tests and CI if you plan to expand the project.

If you'd like, I can:
- add `models/` to `.gitignore` and commit that change,
- run a short smoke training (1 epoch) to validate the full pipeline on your machine,
- or update `predict.py` to load saved `class_indices` automatically.

---
Generated: updated README with setup and run instructions.
