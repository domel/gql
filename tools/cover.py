#!/usr/bin/env python3
"""Create responsive WebP copies of the cover for the HTML edition."""
from pathlib import Path
import re
from urllib.parse import quote

SITE = Path(__file__).resolve().parents[1]
WIDTHS = (230, 460, 690)


def cover_markup():
    # CSS hides the cover below 951px. A local data source also prevents the
    # browser's preload scanner from downloading a hidden cover on mobile.
    placeholder = 'data:image/svg+xml,' + quote(
        '<svg xmlns="http://www.w3.org/2000/svg" width="230" height="345"></svg>', safe=''
    )
    srcset = ', '.join(f'assets/cover-{width}.webp {width}w' for width in WIDTHS)
    return (
        '<picture class="cover-art">'
        f'<source media="(max-width:950px)" srcset="{placeholder}">'
        '<img src="assets/cover-230.webp" '
        f'srcset="{srcset}" sizes="(max-width:1250px) 190px, 230px" '
        'width="230" height="345" alt="GQL Essentials book cover" '
        'decoding="async" fetchpriority="high">'
        '</picture>'
    )


def update_home_cover(source):
    cover_class = r'(?=[^>]*\bclass=["\']cover-art["\'])'
    pattern = re.compile(
        r'<picture\b' + cover_class + r'[^>]*>.*?</picture>'
        r'|<img\b' + cover_class + r'[^>]*>', re.S
    )
    updated, count = pattern.subn(lambda match: cover_markup(), source, count=1)
    if count != 1:
        raise ValueError('Missing homepage cover')
    return updated


def prepare_cover_assets(site=SITE):
    from PIL import Image

    assets = site / 'assets'
    with Image.open(assets / 'cover.png') as original:
        cover = original.convert('RGB')
        resampling = getattr(Image, 'Resampling', Image)
        for width in WIDTHS:
            height = round(width * cover.height / cover.width)
            resized = cover.resize((width, height), resampling.LANCZOS)
            resized.save(assets / f'cover-{width}.webp', 'WEBP', quality=82, method=6)


if __name__ == '__main__':
    prepare_cover_assets()
    home = SITE / 'index.html'
    home.write_text(update_home_cover(home.read_text()))
