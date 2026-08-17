import os
import io
from PIL import Image

test_sets = [
    {"name": "test-small-800x600.jpg", "w": 800, "h": 600},
    {"name": "test-medium-1920x1080.jpg", "w": 1920, "h": 1080},
    {"name": "test-large-2560x1440.jpg", "w": 2560, "h": 1440},
    {"name": "test-xlarge-3840x2160.jpg", "w": 3840, "h": 2160},
]

output_dir = "benchmark_samples"
os.makedirs(output_dir, exist_ok=True)

print("Inizio generazione immagini di benchmark in Python...")

for conf in test_sets:
    w, h, name = conf["w"], conf["h"], conf["name"]
    print(f"Generazione {name} ({w}x{h})...")
    
    # Creazione immagine con pattern complesso per testare la compressione
    img = Image.new("RGB", (w, h))
    pixel_data = []
    
    for y in range(h):
        for x in range(w):
            r = (x * y) % 255
            g = (x ^ y) % 255
            b = (x + y) % 255
            pixel_data.append((r, g, b))
            
    img.putdata(pixel_data)
    
    file_path = os.path.join(output_dir, name)
    img.save(file_path, "JPEG", quality=95)
    size_kb = round(os.path.getsize(file_path) / 1024, 2)
    print(f"Creata: {name} | Dimensione: {size_kb} KB")

print("\nTutte le immagini sono pronte nella cartella: /benchmark_samples")