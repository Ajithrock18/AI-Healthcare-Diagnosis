import kagglehub

# Download the Chest X-Ray Pneumonia dataset
path = kagglehub.dataset_download(
    "paultimothymooney/chest-xray-pneumonia"
)

print("Dataset downloaded to:", path)
