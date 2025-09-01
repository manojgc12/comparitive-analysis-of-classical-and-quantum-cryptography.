def encrypt(text, shift):
    result = ""

    for char in text:
        if char.isalpha():
            # Handle uppercase and lowercase letters separately
            start = ord('A') if char.isupper() else ord('a')
            # Shift character and wrap around alphabet
            shifted = (ord(char) - start + shift) % 26 + start
            result += chr(shifted)
        else:
            # Non-alphabetic characters remain unchanged
            result += char

    return result

def decrypt(cipher_text, shift):
    # Decryption is just encryption with reversed shift
    return encrypt(cipher_text, -shift)

# Example usage
plain_text = "manoj has ideas"
shift_value = 3

encrypted_text = encrypt(plain_text, shift_value)
decrypted_text = decrypt(encrypted_text, shift_value)

print("Plain Text:", plain_text)
print("Encrypted Text:", encrypted_text)
print("Decrypted Text:", decrypted_text)
