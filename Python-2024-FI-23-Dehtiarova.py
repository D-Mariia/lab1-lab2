import timeit
import matplotlib.pyplot as plt
import random

class Operations:

    def __init__(self, value="0", bit_length=2048, base=16):
        self.bit_length = bit_length

        if isinstance(value, str):
            if base == 16:
                if not all(c in '0123456789ABCDEF' for c in value.upper()):
                    raise ValueError(f"Некоректно: {value}")
                self.value = int(value, 16)
            else:
                raise ValueError(f"Невідома система числення: {base}")
        else:
            self.value = value

        if self.value >= (1 << bit_length):
            raise OverflowError(f"Число перевищує {bit_length} бітів!")

    def from_constant(value):
        if value not in [0, 1]:
            raise ValueError("Допустимі лише константи 0 і 1.")
        return Operations(hex(value)[2:], base=16)

    def add(self, other):
        result = self.value + other.value
        carry = result >> self.bit_length
        result &= (1 << self.bit_length) - 1

        return Operations(hex(result)[2:], self.bit_length, base=16), carry

    def sub(self, other):
        if self.value < other.value:
            raise ValueError("Результат віднімання негативний")

        result = self.value - other.value
        borrow = 1 if result < 0 else 0
        result &= (1 << self.bit_length) - 1

        return Operations(hex(result)[2:], self.bit_length, base=16), borrow

    def mul(self, other):
        if self.value == 0 or other.value == 0:
            return Operations(0)

        result = self.value * other.value
        result &= (1 << self.bit_length) - 1

        return Operations(hex(result)[2:], self.bit_length, base=16)

    def div(self, other):
        if other.value == 0:
            raise ZeroDivisionError("Ділення на нуль неможливе.")

        q = self.value // other.value
        r = self.value % other.value

        return Operations(hex(q)[2:], self.bit_length, base=16), Operations(hex(r)[2:], self.bit_length, base=16)

    def sq(self):
        return self.mul(self)

    def __str__(self):
        return self.to_base(16)

    def to_base(self, base):
        if base == 2:
            return bin(self.value)[2:] or '0'
        elif base == 10:
            return str(self.value)
        elif base == 16:
            return hex(self.value)[2:].upper() or '0'
        else:
            raise ValueError(f"Невідома система числення: {base}")

    def input_number(bit_length=2048):
        value = input("Введіть число у шістнадцятковій системі числення: ")
        return Operations(value, bit_length, base=16)

    def time_operations(a, b):
        operations = {
            "Addition": 'a.add(b)',
            "Subtraction": 'a.sub(b)',
            "Multiplication": 'a.mul(b)',
        }

        if b.value != 0:
            operations["Division"] = 'a.div(b)'
        operations["Square"] = 'a.sq()'

        times = {}
        for op, expr in operations.items():
            timer = timeit.Timer(lambda: eval(expr))
            execution_time = timer.timeit(number=1000)
            times[op] = execution_time / 1000

        return times

    def test_identities():
        a = Operations(hex(random.randint(1, 2 ** 2048 - 1))[2:])
        b = Operations(hex(random.randint(1, 2 ** 2048 - 1))[2:])
        c = Operations(hex(random.randint(1, 2 ** 2048 - 1))[2:])

        # Перевірка тотожності 1: (a + b) * c = c * (a + b) = a * c + b * c
        sum_ab, _ = a.add(b)
        left_side = sum_ab.mul(c)
        right_side_1 = c.mul(sum_ab)
        right_side_2, _ = a.mul(c).add(b.mul(c))

        print("1:")
        print(
            f"Left side: {left_side.to_base(16)},\n Right side 1: {right_side_1.to_base(16)}, \n Right side 2: {right_side_2.to_base(16)}")
        print("1:", left_side.value == right_side_1.value == right_side_2.value)

        n = random.randint(100, 200)

        # Перевірка тотожності 2: n * a = (a + a + ... + a) / n
        sum_a = Operations(0)
        for _ in range(n):
            sum_a, _ = sum_a.add(a)

        left_side_2 = sum_a
        right_side_2 = a.mul(Operations(n))

        print("\n 2:")
        print(f"Left side: {left_side_2.to_base(16)}, \n  Right side: {right_side_2.to_base(16)}")
        print("2:", left_side_2.value == right_side_2.value)


if __name__ == "__main__":
    Operations.test_identities()

    a = Operations.input_number()
    b = Operations.input_number()

    sum_result, carry = a.add(b)
    print(f"Сума: {sum_result.to_base(16)}")
    print(f"Перенос (carry): {carry}")

    try:
        diff_result, borrow = a.sub(b)
        print(f"Різниця: {diff_result.to_base(16)}")
        print(f"Запозичення (borrow): {borrow}")
    except ValueError as e:
        print(e)

    product_result = a.mul(b)
    print(f"Добуток: {product_result.to_base(16)}")

    sq_result = a.sq()
    print(f"Квадрат числа A: {sq_result.to_base(16)}")

    try:
        q_result, r_result = a.div(b)
        print(f"Частка від ділення: {q_result.to_base(16)}")
        print(f"Остача від ділення: {r_result.to_base(16)}")
    except ZeroDivisionError as e:
        print(e)

    execution_times = Operations.time_operations(a, b)

    for op, time in execution_times.items():
        print(f"{op}: {time:.10f} seconds")

    operations = list(execution_times.keys())
    times = list(execution_times.values())

    plt.bar(operations, times)
    plt.ylabel('Time (seconds)')
    plt.title('')
    plt.xticks(rotation=45)
    plt.show()
