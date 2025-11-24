"""Barcode scanner for reading ISBN barcodes from camera."""

from typing import Optional

import cv2
from pyzbar.pyzbar import decode


class BarcodeScanner:
    """Scanner for reading ISBN barcodes from camera."""

    def __init__(self):
        """Initialize the barcode scanner."""
        self.camera = None
        self.is_running = False

    def start_camera(self) -> bool:
        """Start the camera for barcode scanning.

        Returns:
            True if camera started successfully, False otherwise
        """
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                return False
            self.is_running = True
            return True
        except Exception:
            return False

    def scan_barcode(self) -> Optional[str]:
        """Scan a barcode from the camera.

        Returns:
            ISBN string if barcode is detected, None otherwise
        """
        if not self.is_running or self.camera is None:
            return None

        try:
            ret, frame = self.camera.read()
            if not ret:
                return None

            # Decode barcodes in the frame
            barcodes = decode(frame)

            for barcode in barcodes:
                # Extract ISBN from barcode data
                isbn = barcode.data.decode("utf-8")
                # Validate ISBN format (13 digits)
                if isbn.isdigit() and len(isbn) in [10, 13]:
                    return isbn

            return None
        except Exception:
            return None

    def stop_camera(self) -> None:
        """Stop the camera."""
        if self.camera is not None:
            self.camera.release()
            self.is_running = False

    def __del__(self):
        """Cleanup when scanner is destroyed."""
        self.stop_camera()
