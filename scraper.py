from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests
import os

from config import URL, DOWNLOAD_FOLDER


def open_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL)
        page.wait_for_timeout(5000)  # tunggu halaman load
        html = page.content()
        browser.close()
        return html


def download_image(img_url, folder):
    try:
        if not img_url.startswith(('http://', 'https://')):
            return  # skip relative url yang tidak lengkap

        filename = os.path.basename(img_url.split('?')[0])  # ambil nama file
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            filename += '.jpg'  # fallback

        filepath = os.path.join(folder, filename)

        response = requests.get(img_url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"✅ Downloaded: {filename}")
        else:
            print(f"❌ Gagal download: {img_url} (status {response.status_code})")
    except Exception as e:
        print(f"❌ Error download {img_url}: {e}")


# ============== MAIN ==============
if __name__ == "__main__":
    # Buat folder download jika belum ada
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    print("Mengambil halaman...")
    html = open_page()

    print("Parsing gambar...")
    soup = BeautifulSoup(html, "lxml")
    images = soup.find_all("img")

    print(f"Ditemukan {len(images)} tag gambar")

    for img in images:
        src = img.get("src") or img.get("data-src") or img.get("data-original")
        if src:
            # Ubah relative URL menjadi absolute
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                src = URL.rstrip('/') + src
            download_image(src, DOWNLOAD_FOLDER)

    print("Proses selesai!")