import os
import logging
import shutil
from PIL import Image
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Choose the output image format: "webp", "png", or None to keep original formats
TARGET_FORMAT = None  # e.g. "webp" or "png", or None to preserve originals
# Base quality setting for JPEG and WebP (1-100). Lower -> smaller files.
QUALITY = 85
# If a file is larger than this threshold (in bytes), apply more aggressive compression
THRESHOLD = 1.2 * 1024 * 1024  # 1.2 MB in bytes
# Additional drop in quality for large files
AGGRESSIVE_DROP = 20  # decrease quality by 20 points for files > THRESHOLD

# Source and output directories
SOURCE_DIR = "sourceImages"
OUTPUT_DIR = "compressedImages"

# Supported input image extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}

# Mapping from file extension to PIL save format
EXT_TO_FORMAT = {
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".png": "PNG",
    ".bmp": "BMP",
    ".gif": "GIF",
    ".tiff": "TIFF",
    ".webp": "WEBP",
}


def compress_image_file(input_path: str, output_path: str):
    """
    Opens an image from input_path, compresses it according to TARGET_FORMAT
    or keeps the original format if TARGET_FORMAT is None, and saves it to output_path.
    If the compressed file is larger than the original, the original is copied instead.
    """
    try:
        img = Image.open(input_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Determine save format and extension
        if TARGET_FORMAT:
            fmt = TARGET_FORMAT.upper()
            out_ext = f".{TARGET_FORMAT.lower()}"
        else:
            out_ext = os.path.splitext(input_path)[1].lower()
            fmt = EXT_TO_FORMAT.get(out_ext)
            if fmt is None:
                raise ValueError(f"Unsupported output format '{out_ext}'")

        # Prepare save parameters
        save_kwargs = {}
        orig_size = os.path.getsize(input_path)

        # Determine quality based on file size
        if fmt in ("WEBP", "JPEG"):
            # Use base QUALITY or more aggressive if above threshold
            if orig_size > THRESHOLD:
                q = max(1, QUALITY - AGGRESSIVE_DROP)
                logging.info(
                    f"Applying aggressive quality={q} for large file > {THRESHOLD//1024}KB")
            else:
                q = QUALITY
            save_kwargs["quality"] = q
        elif fmt == "PNG":
            save_kwargs["optimize"] = True

        # Save compressed image to a temporary path
        temp_path = output_path + ".tmp"
        img.save(temp_path, fmt, **save_kwargs)

        comp_size = os.path.getsize(temp_path)

        if comp_size < orig_size:
            os.replace(temp_path, output_path)
            logging.info(
                f"Compressed and saved: {output_path} ({orig_size//1024}KB → {comp_size//1024}KB)")
        else:
            # If compression bloat, keep original
            shutil.copy2(input_path, output_path)
            os.remove(temp_path)
            logging.warning(
                f"Skipped compression for '{input_path}'; compressed size {comp_size//1024}KB > original {orig_size//1024}KB."
            )
    except Exception as e:
        logging.error(f"Failed to process '{input_path}': {e}")


def gather_all_files(root_dir: str):
    """
    Walks through root_dir recursively and collects all file paths.
    """
    files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            files.append(os.path.join(dirpath, fname))
    return files


def main():
    if not os.path.isdir(SOURCE_DIR):
        logging.error(f"Source directory '{SOURCE_DIR}' not found!")
        return

    images = gather_all_files(SOURCE_DIR)
    if not images:
        logging.error(f"No images found in '{SOURCE_DIR}'.")
        return

    logging.info(f"Found {len(images)} files to process.")

    for src in tqdm(images, desc="Processing files", unit='file'):
        rel_dir = os.path.relpath(os.path.dirname(src), SOURCE_DIR)
        dest_dir = os.path.join(OUTPUT_DIR, rel_dir)
        os.makedirs(dest_dir, exist_ok=True)

        base, ext = os.path.splitext(os.path.basename(src))
        ext_lower = ext.lower()
        if ext_lower in IMAGE_EXTENSIONS:
            if TARGET_FORMAT:
                out_ext = f".{TARGET_FORMAT.lower()}"
            else:
                out_ext = ext_lower
            dest_path = os.path.join(dest_dir, base + out_ext)
            compress_image_file(src, dest_path)
        else:
            dest_path = os.path.join(dest_dir, base + ext)
            shutil.copy2(src, dest_path)
            logging.info(f"Copied file {src} to {dest_path}")

    logging.info("All files processed.")


if __name__ == "__main__":
    main()
