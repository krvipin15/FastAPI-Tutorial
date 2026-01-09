from pwdlib import PasswordHash

# Initialize a password hashing configuration
password_hash: PasswordHash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using a secure, one-way hashing algorithm.

    This function should be used when storing a user's password
    (e.g., during registration or password reset).

    Args:
        password (str): The plain-text password provided by the user.

    Returns:
        str: A securely hashed password string suitable for database storage.
    """
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a previously hashed password.

    This function safely compares the provided password with the stored
    hash and returns whether they match.

    Args:
        plain_password (str): The plain-text password to verify.
        hashed_password (str): The stored hashed password.

    Returns:
        bool: True if the password is valid, False otherwise.
    """
    return password_hash.verify(plain_password, hashed_password)
