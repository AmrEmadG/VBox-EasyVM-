import unittest
from unittest.mock import patch, MagicMock
import os

from Virtual_Disk import create_disk, create_vbox_disk, create_vhd

class TestDiskCreation(unittest.TestCase):

    @patch("Virtual_Disk.subprocess.run")
    @patch("Virtual_Disk.os.makedirs")
    def test_create_vbox_disk(self, mock_makedirs, mock_run):
        path = "C:/temp/test.vdi"
        size_mb = 1024
        create_vbox_disk(path, size_mb, "VDI", "Fixed-Size")

        mock_makedirs.assert_called_once_with(os.path.dirname(path), exist_ok=True)
        mock_run.assert_called_once()

    @patch("Virtual_Disk.subprocess.run")
    @patch("Virtual_Disk.os.remove")
    @patch("Virtual_Disk.open", create=True)
    @patch("Virtual_Disk.os.makedirs")
    def test_create_vhd(self, mock_makedirs, mock_open, mock_remove, mock_run):
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        create_vhd("C:/temp/test.vhd", 512, "Dynamic-Size")
        mock_makedirs.assert_called_once()
        mock_open.assert_called_once()
        mock_run.assert_called_once()
        mock_remove.assert_called_once()

    @patch("Virtual_Disk.create_vhd")
    def test_create_disk_vhd(self, mock_create_vhd):
        create_disk("C:/temp/test.vhd", 1.0, "VHD", "Fixed-Size")
        mock_create_vhd.assert_called_once()

    @patch("Virtual_Disk.create_vbox_disk")
    def test_create_disk_vdi(self, mock_create_vbox_disk):
        create_disk("C:/temp/test.vdi", 2.0, "VDI", "Dynamic-Size")
        mock_create_vbox_disk.assert_called_once()

if __name__ == '__main__':
    unittest.main()
