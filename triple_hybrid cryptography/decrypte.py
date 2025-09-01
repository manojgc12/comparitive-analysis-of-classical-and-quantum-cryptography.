def decrypt(cipher_text, shift):
    result = ""

    for char in cipher_text:
        if char.isalpha():
            # Encrypt uppercase and lowercase letters separately
            start = ord('A') if char.isupper() else ord('a')
            # Shift characters backward by 'shift' and wrap around alphabet
            shifted = (ord(char) - start - shift) % 26 + start
            result += chr(shifted)
        else:
            # Non-alphabet characters are unchanged
            result += char

    return result


# Example usage:
encrypted = "pdqrm kdv lghdv"
shift_value = 3

decrypted_text = decrypt(encrypted, shift_value)
print("Decrypted Text:", decrypted_text)
