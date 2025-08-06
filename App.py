from flask import Flask, request, send_file
from Crypto.Cipher import AES
import os

app = Flask(_name_)

# ✅ Absolute uploads path
BASE_DIR = os.path.dirname(os.path.abspath(_file_))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

KEY = b'ThisIsASecretKey'  # ✅ Exactly 16 bytes for AES-128

# Make sure uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ✅ Encrypt function
def encrypt_file(data):
    cipher = AES.new(KEY, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return cipher.nonce + tag + ciphertext

# ✅ Decrypt function
def decrypt_file(data):
    nonce = data[:16]
    tag = data[16:32]
    ciphertext = data[32:]
    cipher = AES.new(KEY, AES.MODE_EAX, nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext

# ✅ Upload route
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    data = file.read()
    encrypted = encrypt_file(data)
    filename = file.filename + '.enc'
    enc_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(enc_path, 'wb') as f:
        f.write(encrypted)
    print(f"Encrypted file saved to: {enc_path}")
    return f"Uploaded & Encrypted: {filename}"

# ✅ Download & decrypt route with newline fix
@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    print(f"RAW filename BEFORE strip: '{filename}'")
    filename = filename.strip()
    print(f"RAW filename AFTER strip: '{filename}'")

    enc_path = os.path.join(UPLOAD_FOLDER, filename + '.enc')
    print(f"Looking for: {enc_path}")

    if not os.path.exists(enc_path):
        return "File not found.", 404

    with open(enc_path, 'rb') as f:
        enc_data = f.read()

    decrypted = decrypt_file(enc_data)
    dec_path = os.path.join(UPLOAD_FOLDER, 'decrypted_' + filename)
    with open(dec_path, 'wb') as f:
        f.write(decrypted)

    print(f"Decrypted file saved to: {dec_path}")
    return send_file(dec_path, as_attachment=True)

if _name_ == '_main_':
    app.run(debug=True)
