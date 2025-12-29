"""
Download exercise GIFs and store them locally.
"""
import os
import urllib.request
import ssl
import time

# Directory to save GIFs
GIF_DIR = os.path.join(os.path.dirname(__file__), "static", "images", "gifs")

# Updated GIF URLs from strengthlog.com (using their CDN)
GIFS = {
    "back-squat.gif": "https://i0.wp.com/www.strengthlog.com/wp-content/uploads/2021/11/squat.gif",
    "romanian-deadlift.gif": "https://i0.wp.com/www.strengthlog.com/wp-content/uploads/2022/01/Romanian-deadlift.gif",
    "leg-press.gif": "https://i0.wp.com/www.strengthlog.com/wp-content/uploads/2025/11/leg-press.gif",
    "lying-leg-curl.gif": "https://i0.wp.com/www.strengthlog.com/wp-content/uploads/2023/09/lying-leg-curl.gif",
    "standing-calf-raise.gif": "https://i0.wp.com/www.strengthlog.com/wp-content/uploads/2020/03/calf-raise-standing.gif",
    "plank.gif": "https://i0.wp.com/www.strengthlog.com/wp-content/uploads/2025/05/plank-with-shoulder-taps.gif",
    "bench-press.gif": "https://i0.wp.com/www.strengthlog.com/wp-content/uploads/2021/09/bench-press.gif",
    "overhead-press.gif": "https://i0.wp.com/www.strengthlog.com/wp-content/uploads/2020/12/Overhead-press-exercise.gif",
    "incline-dumbbell-press.gif": "https://i0.wp.com/www.strengthlog.com/wp-content/uploads/2020/03/Incline-Bench-Press.gif",
    "dips.gif": "https://i0.wp.com/www.strengthlog.com/wp-content/uploads/2020/02/Dips.gif",
    "lateral-raise.gif": "https://i0.wp.com/www.strengthlog.com/wp-content/uploads/2020/12/Dumbbell-Lateral-Raise.gif",
    "tricep-pushdown.gif": "https://i0.wp.com/www.strengthlog.com/wp-content/uploads/2020/03/triceps-pushdown-with-straight-handle.gif",
    "cable-crunch.gif": "https://i0.wp.com/www.strengthlog.com/wp-content/uploads/2020/03/cable-crunch.gif",
    "deadlift.gif": "https://i0.wp.com/www.strengthlog.com/wp-content/uploads/2020/11/Deadlift.gif",
    "pull-ups.gif": "https://i0.wp.com/www.strengthlog.com/wp-content/uploads/2025/12/pull-ups.gif",
    "barbell-row.gif": "https://i0.wp.com/www.strengthlog.com/wp-content/uploads/2022/03/Barbell-Row.gif",
    "lat-pulldown.gif": "https://i0.wp.com/www.strengthlog.com/wp-content/uploads/2020/03/lat-pulldown-with-pronated-grip.gif",
    "face-pull.gif": "https://i0.wp.com/www.strengthlog.com/wp-content/uploads/2020/05/face-pull.gif",
    "barbell-curl.gif": "https://i0.wp.com/www.strengthlog.com/wp-content/uploads/2020/12/Barbell-biceps-curl.gif",
    "hammer-curl.gif": "https://i0.wp.com/www.strengthlog.com/wp-content/uploads/2020/02/Hammer-curl.gif",
    "hanging-leg-raise.gif": "https://i0.wp.com/www.strengthlog.com/wp-content/uploads/2020/03/hanging-leg-raise.gif",
}


def download_gifs():
    """Download all GIFs to local storage."""
    # Create directory if it doesn't exist
    os.makedirs(GIF_DIR, exist_ok=True)

    # Create SSL context that doesn't verify (for sites with cert issues)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'image/gif,image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.strengthlog.com/',
    }

    downloaded = 0
    failed = []

    for filename, url in GIFS.items():
        filepath = os.path.join(GIF_DIR, filename)

        # Skip if already exists and is a valid size
        if os.path.exists(filepath) and os.path.getsize(filepath) > 10000:
            print(f"Already exists: {filename}")
            downloaded += 1
            continue

        try:
            print(f"Downloading: {filename}...")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=60) as response:
                data = response.read()

                # Check if we got actual image data
                if len(data) < 5000:
                    print(f"  Warning: File too small ({len(data)} bytes), might be blocked")
                    failed.append(filename)
                    continue

                with open(filepath, 'wb') as f:
                    f.write(data)
                print(f"  Saved: {filename} ({len(data):,} bytes)")
                downloaded += 1

            # Be nice to the server
            time.sleep(1)

        except Exception as e:
            print(f"  Failed: {e}")
            failed.append(filename)

    print(f"\nDownloaded: {downloaded}/{len(GIFS)}")
    if failed:
        print(f"Failed: {failed}")

    return downloaded, failed


if __name__ == "__main__":
    download_gifs()
