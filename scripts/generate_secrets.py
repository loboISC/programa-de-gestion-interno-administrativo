from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.auth import hash_master_password
from core.crypto import generate_encryption_key


def main():
    sample_password = "Cambia_Esta_Clave_123!"
    print("APP_ENCRYPTION_KEY=", generate_encryption_key(), sep="")
    print("MASTER_PASSWORD_HASH=", hash_master_password(sample_password), sep="")
    print("SAMPLE_PASSWORD=", sample_password, sep="")


if __name__ == "__main__":
    main()
