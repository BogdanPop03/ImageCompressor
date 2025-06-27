# ImageCompressor

Batch-compress images from either cloud URLs or local files using simple Python scripts.

---

## ✨ Features

• **Dual Workflow** – Compress images that are already online _or_ ones stored on your local drive.
• **Lossy / Loss-less formats** – Output as **WebP**, **PNG**, or keep originals.
• **Automatic directory mirroring** – Preserves nested folder structure when processing local files.
• **Size-aware quality** – Lowers quality more aggressively for very large images to save space (local workflow).
• **Progress bars & logging** – Clear, real-time feedback in the terminal.

---

## 📂 Repository layout
```
ImageCompressor/
├── withLinks/          # Script that downloads & compresses images from URLs
│   └── main.py
├── withSource/         # Script that compresses images that already exist locally
│   ├── main.py
│   ├── sourceImages/   # (you create / drop files here)
│   └── compressedImages/  # (created automatically)
└── README.md
```

> The folders listed in `.gitignore` (`images/`, `compressedImages/`, `sourceImages/`) are kept out of version-control to avoid bloating the repo with binary assets.

---

## 🚀 Getting started

1. **Clone the repository**
   ```bash
git clone https://github.com/<you>/ImageCompressor.git
cd ImageCompressor
```
2. **Create a virtual environment (optional but recommended)**
   ```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```
3. **Install Python dependencies**
   ```bash
pip install pillow tqdm python-docx requests
```
   (Feel free to generate a `requirements.txt` and pin versions for production usage.)

---

## 🖇️ Workflow 1 – withLinks (images hosted online)

### 1. Prepare `images.docx`
Create a Word document **inside `withLinks/`** using the following repeatable pattern:
```
Category name
["https://example.com/image1.jpg", "https://example.com/image2.png"]

Another category
["https://...", "https://..."]
```
Each heading line becomes the folder name; the JSON-like array underneath is parsed for URLs.

### 2. Run the script
```bash
cd withLinks
python main.py
```
The script will:
1. Parse `images.docx`.
2. Download every image to a temporary buffer.
3. Convert/compress it to the chosen `TARGET_FORMAT` (default **WebP**).
4. Save results inside `images4/<Category name>/image_X.webp`.

You can change the output format by editing the constant near the top of `withLinks/main.py`:
```python
TARGET_FORMAT = "webp"  # or "png"
```

---

## 🗂️ Workflow 2 – withSource (images on disk)

1. Place any files or sub-folders you want compressed under:
```
withSource/sourceImages/
```
2. Tweak settings in `withSource/main.py` if desired:
   * `TARGET_FORMAT` – `None` (keep original) / `"webp"` / `"png"`
   * `QUALITY` – Base quality for JPEG/WebP (1–100).
   * `THRESHOLD` & `AGGRESSIVE_DROP` – control extra compression for very large files.
3. Run the script:
```bash
cd withSource
python main.py
```
Images will be written to `withSource/compressedImages/`, mirroring the original directory structure. If the compressed file ends up larger than the original, the script keeps the original to avoid bloat.

---

## ⚙️ Configuration reference
| Constant | Location | Description |
|----------|----------|-------------|
| `TARGET_FORMAT` | both scripts | Desired output extension. `None` (local-only) keeps original format. |
| `QUALITY` | `withSource/main.py` | Base quality for lossy formats. |
| `THRESHOLD` | `withSource/main.py` | File-size (bytes) above which extra compression is applied. |
| `AGGRESSIVE_DROP` | `withSource/main.py` | How many quality points to subtract above the threshold. |

---

## ❓ FAQ / Troubleshooting

• **I get `File 'images.docx' not found'** – Make sure the document sits in the same folder you launch `withLinks/main.py` from (usually `withLinks/`).

• **PIL complains about an unsupported image mode** – Some exotic formats might not be supported by Pillow. Convert these images manually before running the script or skip them.

• **The compressed file is larger than the original** – The local workflow automatically reverts to the original in this case; nothing to worry about.

---

## 🤝 Contributing
Pull requests are welcome! Feel free to open an issue if you spot a bug or have a feature request.

---

## 📝 License
This project is released under the MIT License. See `LICENSE` for details.
