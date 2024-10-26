from dataclasses import dataclass


@dataclass
class A:
    x = 10

    def __post_init__(self):
        print("\n ------ Post init called ------ \n")

    def __repr__(self):
        return f"A.x = {self.x}"


if __name__ == "__main__":
    a = A()
    print(a)
