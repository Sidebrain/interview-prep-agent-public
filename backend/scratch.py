def fib(n: int) -> list[int]:
    if n == 2 or n == 1:
        return 1
    return n + n - 1


if __name__ == "__main__":
    print(fib(5))
