import unittest
import subprocess
from unittest.mock import patch, MagicMock
from tkinter import messagebox
from Virtual_Machine import create_vm, browse_disk, adjust_var  # Replace 'Virtual_Machine' with your actual module name

class TestVMCreation(unittest.TestCase):

    @patch("Virtual_Machine.subprocess.run")
    @patch("Virtual_Machine.messagebox.showerror")
    @patch("Virtual_Machine.messagebox.showinfo")
    def test_create_vm(self, mock_showinfo, mock_showerror, mock_run):
        # Setup mocks
        mock_run.return_value = None  # Mock subprocess to do nothing

        # Test successful VM creation
        create_vm("TestVM", "Linux_64", "2048", "2", "C:/path/to/disk.vdi")
        
        mock_run.assert_called()  # Check subprocess.run was called
        mock_showinfo.assert_called_once_with(
            "Success", "VM 'TestVM' created and disk attached:\nC:/path/to/disk.vdi"
        )
        mock_showerror.assert_not_called()

    @patch("Virtual_Machine.subprocess.run")
    @patch("Virtual_Machine.messagebox.showerror")
    def test_create_vm_error(self, mock_showerror, mock_run):
        # Simulate an error
        mock_run.side_effect = subprocess.CalledProcessError(1, 'command')  # Mock subprocess error

        # Test error handling
        create_vm("TestVM", "Linux_64", "2048", "2", "C:/path/to/disk.vdi")

        mock_showerror.assert_called_once_with(
            "Error", "Failed to create VM:\nCommand 'command' returned non-zero exit status 1."
        )

    @patch("Virtual_Machine.filedialog.askopenfilename")
    def test_browse_disk(self, mock_askopenfilename):
        # Mock file dialog to return a specific file path
        mock_askopenfilename.return_value = "C:/path/to/disk.vdi"

        var = MagicMock()
        browse_disk(var)

        var.set.assert_called_once_with("C:/path/to/disk.vdi")

    def test_adjust_var_increment(self):
        # Test increment of memory/cpu variables
        var = MagicMock()
        var.get.return_value = "2048"
        adjust_var(var, 256)
        
        var.set.assert_called_once_with("2304")

    def test_adjust_var_decrement(self):
        # Test decrement of memory/cpu variables
        var = MagicMock()
        var.get.return_value = "2048"
        adjust_var(var, -256)
        
        var.set.assert_called_once_with("1792")

    def test_adjust_var_no_value(self):
        # Test with no value set (default to 1)
        var = MagicMock()
        var.get.return_value = ""
        adjust_var(var, -256)
        
        var.set.assert_called_once_with("1")


if __name__ == '__main__':
    unittest.main()
