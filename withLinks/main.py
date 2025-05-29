import os
import re
import logging
import requests
from tqdm import tqdm
from PIL import Image
from io import BytesIO
import docx

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Choose the output image format: "webp" or "png"
TARGET_FORMAT = "webp"  # change to "png" if needed


def read_docx_data(filename):
    """
    Reads a DOCX file and extracts categories and their corresponding
    list of image URLs.

    Expected format:

    CategoryName
    [ "url1", "url2", ... ]

    This function processes the whole document text using regex.
    """
    document = docx.Document(filename)
    full_text = "\n".join(para.text for para in document.paragraphs)

    # This regex looks for a line (the category) followed by an array block in square brackets.
    # The DOTALL flag allows the square bracket block to span multiple lines.
    pattern = re.compile(
        r'^(?P<category>[^\n]+)\s*\n\s*(?P<array>\[.*?\])', re.DOTALL | re.MULTILINE)

    data = {}
    for match in pattern.finditer(full_text):
        category = match.group("category").strip()
        array_text = match.group("array")
        # Extract URLs enclosed in any type of quotes: " or “ or ”
        urls = re.findall(r'[“"](\bhttps?://[^"”]+)[”"]', array_text)
        if urls:
            data[category] = urls
            logging.info(
                f"Extracted {len(urls)} URLs for category '{category}'.")
        else:
            logging.warning(f"No URLs found for category '{category}'.")
    return data


def download_and_compress_image(url, save_path):
    """
    Downloads an image from the given URL with a progress bar,
    then compresses and saves it in the specified TARGET_FORMAT.
    """
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        buffer = BytesIO()

        with tqdm(total=total_size, unit='B', unit_scale=True,
                  desc="Downloading", leave=False) as pbar:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    buffer.write(chunk)
                    pbar.update(len(chunk))
        buffer.seek(0)

        img = Image.open(buffer)
        if TARGET_FORMAT.lower() == "webp":
            img.save(save_path, "WEBP", quality=95)
        elif TARGET_FORMAT.lower() == "png":
            img.save(save_path, "PNG", optimize=True)
        else:
            raise ValueError(
                "Unsupported TARGET_FORMAT. Choose 'webp' or 'png'.")

        logging.info(f"Saved image to {save_path}")
    except Exception as e:
        logging.error(f"Failed to process image from {url}. Error: {e}")


def main():
    docx_filename = "images.docx"
    if not os.path.exists(docx_filename):
        logging.error(f"File '{docx_filename}' not found!")
        return

    data = read_docx_data(docx_filename)
    if not data:
        logging.error("No image data was extracted from the DOCX file.")
        return

    base_dir = "images4"
    os.makedirs(base_dir, exist_ok=True)

    for category, urls in data.items():
        category_folder = os.path.join(base_dir, category)
        os.makedirs(category_folder, exist_ok=True)
        logging.info(
            f"Processing category '{category}' with {len(urls)} images.")

        for idx, url in enumerate(urls, start=1):
            logging.info(f"Processing image {idx}/{len(urls)} in '{category}'")
            filename = f"image_{idx}.{TARGET_FORMAT.lower()}"
            save_path = os.path.join(category_folder, filename)
            download_and_compress_image(url, save_path)


if __name__ == "__main__":
    main()
