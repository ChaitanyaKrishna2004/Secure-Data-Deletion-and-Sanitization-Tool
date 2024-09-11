import os
import random
import string
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
import shutil

def overwrite_file(filename, passes=3):
    """Overwrite the file with random data."""
    try:
        with open(filename, "r+b") as f:
            length = os.path.getsize(filename)
            for i in range(passes):
                f.seek(0)
                f.write(os.urandom(length))
                f.flush()
                os.fsync(f.fileno())
        print(f"File '{filename}' was overwritten {passes} times.")
    except PermissionError as e:
        print(f"PermissionError: {e}. Ensure that the file is not in use and that you have sufficient permissions.")
    except Exception as e:
        print(f"An error occurred: {e}")

def secure_delete_file(filename, passes=3):
    """Securely delete a single file by overwriting and then removing it."""
    if os.path.exists(filename):
        print(f"File '{filename}' is stored at: {os.path.abspath(filename)}")
        overwrite_file(filename, passes)
        try:
            os.remove(filename)
            print(f"File '{filename}' securely deleted from: {os.path.abspath(filename)}")
        except PermissionError as e:
            print(f"PermissionError: {e}. Ensure that the file is not in use and that you have sufficient permissions.")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print(f"File '{filename}' does not exist.")

def secure_delete_directory(directory, passes=3):
    """Securely delete a directory and all of its contents."""
    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist.")
        return
    
    print(f"Directory '{directory}' is stored at: {os.path.abspath(directory)}")
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            secure_delete_file(file_path, passes)
        for name in dirs:
            dir_path = os.path.join(root, name)
            try:
                os.rmdir(dir_path)
                print(f"Directory '{dir_path}' deleted.")
            except Exception as e:
                print(f"An error occurred while deleting directory '{dir_path}': {e}")

    try:
        os.rmdir(directory)
        print(f"Directory '{directory}' securely deleted from: {os.path.abspath(directory)}")
    except Exception as e:
        print(f"An error occurred while deleting directory '{directory}': {e}")

def cryptographic_erase(filename):
    """Encrypt the file and delete the encryption key."""
    if os.path.isdir(filename):
        print(f"Error: '{filename}' is a directory. Cryptographic erase is not supported for directories.")
        return

    if os.path.exists(filename):
        key = get_random_bytes(32)  # AES-256
        cipher = AES.new(key, AES.MODE_CFB)
        with open(filename, "rb") as f:
            plaintext = f.read()
        ciphertext = cipher.encrypt(plaintext)

        with open(filename, "wb") as f:
            f.write(cipher.iv)  # Write the IV
            f.write(ciphertext)  # Write the ciphertext

        print(f"File '{filename}' cryptographically erased and was stored at: {os.path.abspath(filename)}")
        os.remove(filename)  # Delete the file after encrypting
    else:
        print(f"File '{filename}' does not exist.")

def wipe_free_space(drive_path, passes=1, chunk_size=1024*1024*10):
    """Wipe the free space on a given drive in chunks to avoid memory errors."""
    free_space_file = os.path.join(drive_path, ''.join(random.choices(string.ascii_letters + string.digits, k=12)))

    try:
        total, used, free = shutil.disk_usage(drive_path)
        
        with open(free_space_file, "wb") as f:
            for _ in range(passes):
                print(f"Wiping free space on {drive_path} with {passes} pass(es)...")
                bytes_written = 0
                while bytes_written < free:
                    chunk = os.urandom(min(chunk_size, free - bytes_written))
                    f.write(chunk)
                    bytes_written += len(chunk)
                    f.flush()
                    os.fsync(f.fileno())
            print(f"Free space on '{drive_path}' wiped with {passes} pass(es).")
    finally:
        if os.path.exists(free_space_file):
            os.remove(free_space_file)
            print(f"Temporary file used for wiping free space deleted from '{free_space_file}'.")

def main():
    filename = None

    while True:
        print("\nSecure Data Deletion Tool")
        print("1. Provide input file, folder, or video file")
        print("2. Securely delete the file or directory")
        print("3. Cryptographically erase the file")
        print("4. Wipe free space on a drive")
        print("5. Exit")

        choice = input("Please choose an option: ")

        if choice == '1':
            filename = input("Enter the file, folder, or video file path: ")
            if not os.path.exists(filename):
                print(f"'{filename}' does not exist.")
                filename = None
            else:
                print(f"'{filename}' loaded.")
        
        elif choice == '2':
            if filename:
                passes = int(input("Enter the number of overwrite passes (default is 3): ") or "3")
                if os.path.isdir(filename):
                    secure_delete_directory(filename, passes)
                else:
                    secure_delete_file(filename, passes)
            else:
                print("No file or directory provided. Please select option 1 to provide an input file or directory first.")
        
        elif choice == '3':
            if filename:
                if os.path.isdir(filename):
                    print("Cryptographic erase is not supported for directories.")
                else:
                    cryptographic_erase(filename)
            else:
                print("No file provided. Please select option 1 to provide an input file first.")
        
        elif choice == '4':
            drive_path = input("Enter the drive path to wipe free space: ")
            if os.path.exists(drive_path):
                passes = int(input("Enter the number of passes (default is 1): ") or "1")
                wipe_free_space(drive_path, passes)
            else:
                print(f"Drive path '{drive_path}' does not exist.")
        
        elif choice == '5':
            print("Exiting the program.")
            break
        
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()

