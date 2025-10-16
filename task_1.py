from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mmh3

# -----------------------------
# Клас реалізації фільтра Блума
# -----------------------------
class BloomFilter:
    def __init__(self, size: int, num_hashes: int):
        """
        Ініціалізує фільтр Блума.
        :param size: розмір бітового масиву
        :param num_hashes: кількість хеш-функцій
        """
        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = [0] * size

    def _hashes(self, item: str):
        """Генерує набір індексів для елемента."""
        return [mmh3.hash(item, i) % self.size for i in range(self.num_hashes)]

    def add(self, item: str):
        """Додає елемент до фільтра."""
        if not isinstance(item, str) or not item:
            return
        for index in self._hashes(item):
            self.bit_array[index] = 1

    def contains(self, item: str) -> bool:
        """Перевіряє, чи можливо, що елемент є у фільтрі."""
        if not isinstance(item, str) or not item:
            return False
        return all(self.bit_array[i] == 1 for i in self._hashes(item))


# -------------------------------------------------
# Функція перевірки унікальності списку паролів
# -------------------------------------------------
def check_password_uniqueness(bloom: BloomFilter, new_passwords: list[str]) -> dict[str, str]:
    """
    Перевіряє, які паролі вже використовувались, а які унікальні.
    :param bloom: екземпляр фільтра Блума
    :param new_passwords: список паролів для перевірки
    :return: словник {пароль: статус}
    """
    results = {}
    for password in new_passwords:
        if not isinstance(password, str) or not password:
            results[password] = "некоректне значення"
        elif bloom.contains(password):
            results[password] = "вже використаний"
        else:
            results[password] = "унікальний"
            bloom.add(password)
    return results


# -----------------------------
# Частина для FastAPI
# -----------------------------
app = FastAPI(title="Password Bloom Filter API")

# Ініціалізація фільтра
bloom = BloomFilter(size=1000, num_hashes=3)

# Модель запиту
class PasswordCheckRequest(BaseModel):
    passwords: list[str]

@app.post("/check_passwords")
def check_passwords(request: PasswordCheckRequest):
    """API-ендпоінт для перевірки паролів"""
    if not request.passwords:
        raise HTTPException(status_code=400, detail="Список паролів порожній")
    results = check_password_uniqueness(bloom, request.passwords)
    return results


# -----------------------------
# Приклад локального використання
# -----------------------------
if __name__ == "__main__":
    # Ініціалізація фільтра Блума
    bloom = BloomFilter(size=1000, num_hashes=3)

    # Додавання існуючих паролів
    existing_passwords = ["password123", "admin123", "qwerty123"]
    for password in existing_passwords:
        bloom.add(password)

    # Перевірка нових паролів
    new_passwords_to_check = ["password123", "newpassword", "admin123", "guest"]
    results = check_password_uniqueness(bloom, new_passwords_to_check)

    # Виведення результатів
    for password, status in results.items():
        print(f"Пароль '{password}' - {status}.")