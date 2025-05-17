import numpy as np
from PIL import Image
import csv, os, datetime
from tflite_runtime.interpreter import Interpreter   # use TensorFlow Lite runtime (tiny!)

MODEL_PATH = os.path.join(os.path.dirname(_file_), "..", "model", "best_float32.tflite")
LABELS_PATH = os.path.join(os.path.dirname(_file_), "..", "model", "labels.txt")
LOG_PATH    = os.path.join(os.path.dirname(_file_), "..", "..", "logs")
os.makedirs(LOG_PATH, exist_ok=True)
LOG_FILE    = os.path.join(LOG_PATH, "detections.csv")

# --- load model once ---------------------------------------------------------
interpreter = Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details  = interpreter.get_input_details()
output_details = interpreter.get_output_details()
input_height, input_width = input_details[0]["shape"][1:3]

# binary labels: idx 0 = Fake, idx 1 = Real
with open(LABELS_PATH, "r") as f:
    labels = [l.strip() for l in f.readlines()]

# -----------------------------------------------------------------------------    
def _preprocess(image_path: str) -> np.ndarray:
    img = Image.open(image_path).convert("RGB").resize((input_width, input_height))
    arr = np.asarray(img, dtype=np.float32) / 255.0          # normalize 0-1
    arr = np.expand_dims(arr, axis=0)                        # add batch dim
    return arr

def _log(brand: str, verdict: str, conf: float):
    is_new = not os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        w = csv.writer(f)
        if is_new:
            w.writerow(["timestamp", "brand", "verdict", "confidence"])
        w.writerow([datetime.datetime.now().isoformat(timespec="seconds"),
                    brand, verdict, f"{conf:.4f}"])

# -----------------------------------------------------------------------------    
def predict_logo(image_path: str, brand: str = "Unknown"):
    """Returns verdict ('Real'/'Fake') & confidence (0-1 float)."""
    inp = _preprocess(image_path)
    interpreter.set_tensor(input_details[0]["index"], inp)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]["index"])[0]  # shape (2,)
    
    conf_real = float(output[1])            # confidence for 'Real'
    verdict   = "Real" if conf_real >= 0.5 else "Fake"
    confidence = conf_real if verdict == "Real" else 1.0 - conf_real

    _log(brand, verdict, confidence)
    return verdict, confidences