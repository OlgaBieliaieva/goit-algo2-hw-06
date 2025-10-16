import re
import time
from datasketch import HyperLogLog

# -----------------------------
# 1. Завантаження та обробка лог-файлу
# -----------------------------
def load_ip_addresses(file_path: str) -> list[str]:
    """
    Завантажує IP-адреси з лог-файлу.
    Ігнорує некоректні або порожні рядки.
    :param file_path: шлях до файлу з логами
    :return: список IP-адрес
    """
    ip_pattern = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
    ip_addresses = []

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                match = ip_pattern.search(line)
                if match:
                    ip_addresses.append(match.group(0))
    except FileNotFoundError:
        print(f"Файл {file_path} не знайдено.")
        return []

    return ip_addresses


# -----------------------------
# 2. Точний підрахунок унікальних IP-адрес
# -----------------------------
def count_unique_exact(ip_addresses: list[str]) -> int:
    """
    Підрахунок точної кількості унікальних IP-адрес.
    Використовує структуру set.
    """
    return len(set(ip_addresses))


# -----------------------------
# 3. Наближений підрахунок HyperLogLog
# -----------------------------
def count_unique_hll(ip_addresses: list[str], p: int = 14) -> float:
    """
    Підрахунок кількості унікальних IP-адрес за допомогою HyperLogLog.
    :param p: параметр точності HLL (чим більший p, тим менша похибка)
    """
    hll = HyperLogLog(p=p)
    for ip in ip_addresses:
        hll.update(ip.encode('utf-8'))
    return hll.count()


# -----------------------------
# 4. Порівняння продуктивності
# -----------------------------
def compare_methods(file_path: str):
    """
    Порівнює швидкість і точність підрахунку між set та HyperLogLog.
    Виводить результати у вигляді таблиці.
    """
    print("Завантаження даних...")
    ip_addresses = load_ip_addresses(file_path)

    if not ip_addresses:
        print("Дані для обробки відсутні.")
        return

    print(f"Завантажено {len(ip_addresses)} рядків із логів.\n")

    # Точний підрахунок
    start_time = time.perf_counter()
    exact_count = count_unique_exact(ip_addresses)
    exact_time = time.perf_counter() - start_time

    # HyperLogLog підрахунок
    start_time = time.perf_counter()
    hll_count = count_unique_hll(ip_addresses)
    hll_time = time.perf_counter() - start_time

    # Формування таблиці результатів
    print("Результати порівняння:")
    print(f"{'Метод':<30}{'Унікальні елементи':<25}{'Час виконання (сек.)'}")
    print("-" * 70)
    print(f"{'Точний підрахунок (set)':<30}{exact_count:<25}{exact_time:.4f}")
    print(f"{'HyperLogLog':<30}{int(hll_count):<25}{hll_time:.4f}")


# -----------------------------
# 5. Приклад запуску
# -----------------------------
if __name__ == "__main__":
    # Приклад використання
    log_file = "lms-stage-access.log"  
    compare_methods(log_file)