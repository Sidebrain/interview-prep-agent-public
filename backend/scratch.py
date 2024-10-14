from functools import lru_cache


@lru_cache()
def factorial(n: int) -> int:
    if n == 0 | n == 1:
        return 1
    return n * factorial(n - 1)


if __name__ == "__main__":
    print(factorial(925))  # 120
