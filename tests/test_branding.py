"""Validate shipped icon formats without creating a desktop window."""
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'soskuska'))
from branding import ASSETS, install_window_icon


class BrandingTests(unittest.TestCase):
    def test_png_sizes_and_transparent_corners(self):
        for size in (16, 24, 32, 48, 64, 128, 256, 512, 1024):
            with self.subTest(size=size), Image.open(ASSETS / f'logo-{size}.png') as icon:
                self.assertEqual(icon.size, (size, size))
                self.assertEqual(icon.mode, 'RGBA')
                self.assertLessEqual(icon.getpixel((0, 0))[3], 4)  # Resampling can leave <2% alpha.
                self.assertEqual(icon.getpixel((size//2, size//2))[3], 255)

    def test_native_containers_have_multiple_resolutions(self):
        with Image.open(ASSETS / 'soskuska.ico') as icon:
            self.assertTrue({(16, 16), (32, 32), (48, 48), (256, 256)} <= icon.ico.sizes())
            for size in icon.ico.sizes():
                self.assertEqual(icon.ico.getimage(size).size, size)
        with Image.open(ASSETS / 'soskuska.icns') as icon:
            icon.load()
            self.assertEqual(icon.size, (1024, 1024))

    def test_aqua_receives_large_first_icon(self):
        window = Mock()
        with patch('branding.sys.platform', 'darwin'), patch('branding.tk.PhotoImage') as image:
            install_window_icon(window)
        image.assert_called_once_with(master=window, file=str(ASSETS / 'logo-512.png'))
        window.iconphoto.assert_called_once_with(True, image.return_value)
        window.iconbitmap.assert_not_called()
