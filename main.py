#!/usr/bin/env python3
"""Entry for make.fun news-image-20261122: write the news image to /output/entry.png.

The image (entry.png, drawn by draw_news.py) sums up the world news of
Sunday 22 November 2026 in a single 1024x1024 infographic. This program
only copies it to the output path, so two runs always write the same bytes
and no network is needed.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    os.makedirs("/output", exist_ok=True)
    shutil.copyfile(os.path.join(HERE, "entry.png"), "/output/entry.png")


if __name__ == "__main__":
    main()
