import time
import matplotlib.pyplot as plt


def mtime (func, *args, repeats=10):
    start = time.time()
    for _ in range(repeats):
        result = func(*args)
    end = time.time()
    avg_time = (end - start) / repeats
    return avg_time, result


class Operations:
    def __init__(self, hex_value):
        self.bin_value = self.hex_to_bin(hex_value)

    @staticmethod
    def hex_to_bin(hex_str):
        return bin(int(hex_str, 16))[2:].zfill(2048)

    @staticmethod
    def bin_to_hex(bin_str):
        return hex(int(bin_str, 2))[2:].lstrip('0').upper() or '0'

    @staticmethod
    def small_constant_to_bin(value):
        if value not in (0, 1):
            raise ValueError("Можливі тільки константи 0 або 1")
        return str(value).zfill(2048)

    def add(self, other):
        return self.bin_to_hex(self.add_binary(self.bin_value, other.bin_value))

    @staticmethod
    def add_binary(a, b):
        max_len = max(len(a), len(b))
        a = a.zfill(max_len)
        b = b.zfill(max_len)

        result = ''
        carry = 0

        for i in range(max_len - 1, -1, -1):
            r = carry
            r += 1 if a[i] == '1' else 0
            r += 1 if b[i] == '1' else 0

            result = ('1' if r % 2 == 1 else '0') + result
            carry = 0 if r < 2 else 1

        if carry != 0:
            result = '1' + result

        return result.zfill(2048)

    @staticmethod
    def subtract(a, b):
        comparison = Operations.long_cmp(a, b)
        if comparison == -1:
            return "Помилка: неможливо відняти більше число від меншого."
        return Operations.bin_to_hex(Operations.subtract_binary(a, b))

    @staticmethod
    def subtract_binary(a, b):
        max_len = max(len(a), len(b))
        a = a.zfill(max_len)
        b = b.zfill(max_len)

        result = ''
        borrow = 0

        for i in range(max_len - 1, -1, -1):
            r = int(a[i]) - borrow
            r -= int(b[i])

            if r < 0:
                r += 2
                borrow = 1
            else:
                borrow = 0

            result = str(r) + result

        return result.lstrip('0').zfill(2048)

    @staticmethod
    def long_mul_one_digit(a, b_digit):
        carry = 0
        result = ['0'] * (len(a) + 1)

        for i in range(len(a) - 1, -1, -1):
            temp = int(a[i]) * b_digit + carry
            result[i + 1] = str(temp % 2)
            carry = temp // 2

        result[0] = str(carry)
        return ''.join(result).lstrip('0').zfill(2048)

    @staticmethod
    def long_mul(a, b):
        result = '0' * (len(a) + len(b))

        for i in range(len(b) - 1, -1, -1):
            temp = Operations.long_mul_one_digit(a, int(b[i]))
            temp = Operations.long_shift_digits_to_high(temp, len(b) - 1 - i)
            result = Operations.add_binary(result, temp)

        return Operations.bin_to_hex(result)

    @staticmethod
    def long_shift_digits_to_high(b, n):
        return b + '0' * n

    @staticmethod
    def long_cmp(a, b):
        a = a.lstrip('0')
        b = b.lstrip('0')

        if len(a) > len(b):
            return 1
        elif len(a) < len(b):
            return -1

        for i in range(len(a)):
            if a[i] > b[i]:
                return 1
            elif a[i] < b[i]:
                return -1

        return 0

    @staticmethod
    def long_div_mod(a, b):
        if b == '0':
            return "Помилка: ділення на нуль."
        if a == '0':
            return ('0', '0')

        R = a
        Q = '0'
        C = b
        shift = 0

        while Operations.long_cmp(R, C) >= 0:
            C = Operations.long_shift_digits_to_high(b, shift)
            shift += 1

        while shift > 0:
            shift -= 1
            C = Operations.long_shift_digits_to_high(b, shift)

            if Operations.long_cmp(R, C) >= 0:
                R = Operations.subtract_binary(R, C)
                Q = Operations.add_binary(Q, '1' + '0' * shift)

        return (Operations.bin_to_hex(Q), Operations.bin_to_hex(R))  # Повертаємо частку і залишок

    @staticmethod
    def input_number(prompt):
        while True:
            hex_value = input(prompt)
            try:
                int(hex_value, 16)
                return hex_value
            except ValueError:
                print("Невірний формат. Будь ласка, введіть 16-кове число.")

    def square(self):
        return Operations.long_mul(self.bin_value, self.bin_value)



if __name__ == "__main__":
    num1_hex = Operations.input_number("Введіть перше число (16-кове): ")
    num2_hex = Operations.input_number("Введіть друге число (16-кове): ")

    a = Operations(num1_hex)
    b = Operations(num2_hex)

    add_time, add_result = mtime(a.add, b)
    sub_time, sub_result = mtime(Operations.subtract, a.bin_value, b.bin_value)
    mul_time, mul_result = mtime(Operations.long_mul, a.bin_value, b.bin_value)
    div_time, (div_quotient, div_remainder) = mtime(Operations.long_div_mod, a.bin_value, b.bin_value)
    square_time, square_result = mtime(a.square)

    print(f"Результат додавання: {add_result}")
    print(f"Середній час виконання додавання: {add_time:.10f} сек")

    print(f"Результат віднімання: {sub_result}")
    print(f"Середній час виконання віднімання: {sub_time:.10f} сек")

    print(f"Результат множення: {mul_result}")
    print(f"Середній час виконання множення: {mul_time:.10f} сек")

    print(f"Частка при діленні: {div_quotient}")
    print(f"Залишок при діленні: {div_remainder}")
    print(f"Середній час виконання ділення: {div_time:.10f} сек")

    print(f"Результат піднесення до квадрату: {square_result}")
    print(f"Середній час виконання піднесення до квадрату: {square_time:.10f} сек")

    operations = ['Додавання', 'Віднімання', 'Множення', 'Ділення', 'Квадрат']
    times = [add_time, sub_time, mul_time, div_time, square_time]

    plt.barh(operations, times, color='green')
    plt.xlabel('Час виконання (сек)')
    plt.title('Час виконання арифметичних операцій')
    plt.show()
