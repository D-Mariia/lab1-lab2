import time
import numpy as np
import matplotlib.pyplot as plt

class Operations:
    def __init__(self, words):
        self.words = words

    @staticmethod
    def hex_to_words(hex_string):
        num = int(hex_string, 16)
        words = []
        while num:
            words.append(num & 0xFFFFFFFF)
            num >>= 32
        return words

    def to_hex(self):
        hex_string = ""
        for word in reversed(self.words):
            hex_string += f"{word:08x}"
        return hex_string.lstrip("0") or "0"

    def add(self, other):
        max_len = max(len(self.words), len(other.words))
        result = [0] * (max_len + 1)
        carry = 0

        for i in range(max_len):
            a = self.words[i] if i < len(self.words) else 0
            b = other.words[i] if i < len(other.words) else 0
            total = a + b + carry
            result[i] = total & 0xFFFFFFFF
            carry = total >> 32

        result[max_len] = carry
        return Operations(words=result)

    def subtract(self, other):
        result = [0] * len(self.words)
        borrow = 0

        for i in range(len(self.words)):
            total = self.words[i] - (other.words[i] if i < len(other.words) else 0) - borrow
            if total < 0:
                borrow = 1
                total += 1 << 32
            else:
                borrow = 0
            result[i] = total & 0xFFFFFFFF
        return Operations(words=result)

    def multiply(self, other):
        result = [0] * (len(self.words) + len(other.words))

        for i in range(len(self.words)):
            carry = 0
            for j in range(len(other.words)):
                total = result[i + j] + self.words[i] * other.words[j] + carry
                result[i + j] = total & 0xFFFFFFFF
                carry = total >> 32

            result[i + len(other.words)] += carry

        while len(result) > 1 and result[-1] == 0:
            result.pop()

        return Operations(words=result)

    def divide(self, other):
        if len(other.words) == 1 and other.words[0] == 0:
            raise ZeroDivisionError("Ділення на нуль")

        dividend = self.words[:]
        divisor = other.words[:]
        quotient = [0] * (len(dividend) + 1)
        remainder = [0] * len(dividend)

        shift = 0
        while len(divisor) > 1 and (divisor[-1] & (1 << 31)) == 0:
            divisor = self.left_shift(divisor, 1)
            shift += 1

        for i in range(len(dividend) * 32 - 1, -1, -1):
            remainder = self.left_shift(remainder, 1)
            remainder[0] |= (dividend[i // 32] >> (i % 32)) & 1

            if self.compare_words(remainder, divisor) >= 0:
                remainder = self.subtract_words(remainder, divisor)
                quotient[i // 32] |= 1 << (i % 32)

        quotient_result = Operations(words=self.right_shift(quotient, shift))
        remainder_result = Operations(words=remainder)

        while len(quotient_result.words) > 1 and quotient_result.words[-1] == 0:
            quotient_result.words.pop()

        return quotient_result, remainder_result

    @staticmethod
    def left_shift(words, shift):
        shifted = [0] * len(words)
        for i in range(len(words)):
            shifted[i] = (words[i] << shift) & 0xFFFFFFFF
            if i > 0:
                shifted[i] |= words[i - 1] >> (32 - shift)
        return shifted

    @staticmethod
    def right_shift(words, shift):
        shifted = [0] * len(words)
        for i in range(len(words) - 1, -1, -1):
            shifted[i] = (words[i] >> shift) & 0xFFFFFFFF
            if i < len(words) - 1:
                shifted[i] |= (words[i + 1] << (32 - shift)) & 0xFFFFFFFF
        return shifted

    @staticmethod
    def compare_words(a, b):
        len_a, len_b = len(a), len(b)
        if len_a < len_b:
            a.extend([0] * (len_b - len_a))
        elif len_b < len_a:
            b.extend([0] * (len_a - len_b))

        for i in range(len(a) - 1, -1, -1):
            if a[i] > b[i]:
                return 1
            elif a[i] < b[i]:
                return -1
        return 0

    @staticmethod
    def subtract_words(a, b):
        result = [0] * len(a)
        borrow = 0
        for i in range(len(a)):
            total = a[i] - (b[i] if i < len(b) else 0) - borrow
            if total < 0:
                borrow = 1
                total += 1 << 32
            else:
                borrow = 0
            result[i] = total & 0xFFFFFFFF
        return result

    def mtime(self, operation, other, iterations=100):
        times = []
        for _ in range(iterations):
            start_time = time.time()
            operation(other)
            end_time = time.time()
            times.append(end_time - start_time)
        return np.mean(times)

if __name__ == "__main__":
    hex_input1 = input("Введіть перше велике число у шістнадцятковому форматі: ")
    hex_input2 = input("Введіть друге велике число у шістнадцятковому форматі: ")

    num1 = Operations(Operations.hex_to_words(hex_input1))
    num2 = Operations(Operations.hex_to_words(hex_input2))

    operations = {
        "Додавання": num1.add,
        "Віднімання": num1.subtract,
        "Множення": num1.multiply,
        "Ділення": num1.divide,
    }

    results = {}
    for name, func in operations.items():
        mean_time = num1.mtime(func, num2)
        if name == "Ділення":
            quotient, remainder = func(num2)
            results[name] = (mean_time, quotient.to_hex(), remainder.to_hex())
        else:
            result = func(num2)
            results[name] = (mean_time, result.to_hex())

    print("\nРезультати арифметичних операцій:")
    for operation, (mean_time, *result) in results.items():
        if len(result) > 1:
            print(f"{operation}: {result[0]} (ціле)")
            print(f"Час: {mean_time:.10f} секунд")
            print(f"Залишок: {result[1]}\n")
        else:
            print(f"{operation}: {result[0]}")
            print(f"Час: {mean_time:.10f} секунд\n")

    labels = list(results.keys())
    mean_times = [r[0] for r in results.values()]

    x = np.arange(len(labels))

    fig, ax = plt.subplots()
    ax.bar(x, mean_times, 0.4, label='Середній час')
    ax.set_ylabel('Час (с)')
    ax.set_title('Час виконання арифметичних операцій')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    plt.tight_layout()
    plt.show()