import base64
import nacl.encoding
import nacl.public

public_key = "YOUR_PUBLIC_KEY"
secret_value = "YOUR_SECRET"

public_key_bytes = base64.b64decode(public_key)
sealed_box = nacl.public.SealedBox(nacl.public.PublicKey(public_key_bytes))
encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
encrypted_secret = base64.b64encode(encrypted).decode("utf-8")
