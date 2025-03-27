import time
from tabulate import tabulate

def hex_to_32(hex_num):
    n = int(hex_num, 16)
    array = []
    while n:
        array.append(n % 2**32)
        n //= 2**32
    return array


class Long():
    @staticmethod
    def add(a,b):
        size = max(len(a),len(b))

        a = a + [0] * (size - len(a))
        b = b + [0] * (size - len(b))

        result = [0] * (size + 1)
        carry = 0

        for i in range(size):
            temp = a[i] + b[i] + carry
            result [i] = temp & (2**32 - 1)
            carry = temp >> 32

        return result if result[-1] else result[:-1]

    @staticmethod
    def sub(a,b):
        size = max (len(a),len(b))

        a = a + [0] * (size - len(a))
        b = b + [0] * (size - len(b))

        result = [0] * size
        borrow = 0

        for i in range(size):
            temp = a[i] - b[i] - borrow
            if temp >= 0:
                result[i] = temp
                borrow = 0
            else:
                result[i] = temp + 2**32
                borrow = 1

        return result if result[-1] != 0 else result[:-1]

    @staticmethod
    def cmp(a, b):
        len_a = len(a)
        len_b = len(b)

        if len_a > len_b:
            return 1
        elif len_a < len_b:
            return -1

        for i in range(len_a - 1, -1, -1):
            if a[i] > b[i]:
                return 1
            elif a[i] < b[i]:
                return -1
        return 0

    @staticmethod
    def mul_one(a, digit):
        n = len(a)
        C = [0] * (n + 1)

        carry = 0
        for i in range(n):
            temp = a[i] * digit + carry
            C[i] = temp & (2 ** 32 - 1)
            carry = temp >> 32

        C[n] = carry
        return C

    @staticmethod
    def mul(a, b):
        n = min(len(a), len(b))
        C = [0]

        for i in range(n):
            temp = Long.mul_one(a, b[i])
            temp = [0] * i + temp
            C = Long.add(C, temp)
        return C

    @staticmethod
    def bit(a):
        n = 32 * (len(a) - 1) + a[-1].bit_length()
        return n

    @staticmethod
    def shift(a, shift):
        if shift == 0:
            return a
        num_blocks = shift // 32
        bit_shift = shift % 32
        shifted_num = [0] * num_blocks
        carry = 0

        for i in range(len(a)):
            block = a[i]
            shifted_block = (block << bit_shift) | carry
            shifted_num.append(shifted_block & (2 ** 32 - 1))
            carry = block >> (32 - bit_shift)
        if carry:
            shifted_num.append(carry)
        return shifted_num


    @staticmethod
    def div(a,b):
        k = Long.bit(b)
        R = a
        Q = [0] * len(a)

        while Long.cmp(R,b) != -1 :
            t = Long.bit(R)
            C = Long.shift(b, t - k)

            if Long.cmp(R,C) == -1:
                t -= 1
                C = Long.shift(b, t - k)

            R = Long.sub(R, C)
            Q[(t - k) // 32] = Q[(t - k) // 32] | 1 << ((t - k) % 32)

        return Q, R

    @staticmethod
    def time(func, a, b, iterations=1000):
        start_time = time.time()
        for _ in range(iterations):
            func(a, b)
        end_time = time.time()
        return (end_time - start_time) / iterations

a = '6f18df13a563d96b3abdd33abaf605b0c41c9fa9ef9859ea87e6fc6e61e8687f906363a5b3c11933822abb67ea9e86f8f53aee31044fd11ccb0441184911ecd5928eb1c6a0911962fcc69498c4a16a65c5c51e8d464dc69144b76afbb7ef97911b1ac6c1a3eae29ede0df9d7c125cfc49597e80a41aaa92adf0d0de4929ad52'
b = '6f2a4782244c271647890169026fcf4d14e5e17d97edb7ff034544b584464879c977aa43b058a97546cf299a110101ec26c7e641dfaa88a3b9bdc1'

a = hex_to_32(a)
b = hex_to_32(b)

result_add = Long.add(a, b)
result_add = ''.join(f'{x:08x}' for x in reversed(result_add)).lstrip('0') or '0'
print("A+B:", result_add)

result_sub = Long.sub(a, b)
result_sub = ''.join(f'{x:08x}' for x in reversed(result_sub)).lstrip('0') or '0'
print("A-B:", result_sub)

result_mul = Long.mul(a, b)
result_mul = ''.join(f'{x:08x}' for x in reversed(result_mul)).lstrip('0') or '0'
print("A*B:", result_mul)

result_sq = Long.mul(a, a)
result_sq = ''.join(f'{x:08x}' for x in reversed(result_sq)).lstrip('0') or '0'
print("A^2:", result_sq)

result_div = Long.div(a, b)

q_result = ''.join(f'{x:08x}' for x in reversed(result_div[0])).lstrip('0') or '0'
r_result = ''.join(f'{x:08x}' for x in reversed(result_div[1])).lstrip('0') or '0'

print("Q:", q_result)
print("R:", r_result)

add_time = Long.time(Long.add, a, b)
sub_time = Long.time(Long.sub, a, b)
mul_time = Long.time(Long.mul, a, b)
sq_time = Long.time(Long.mul, a, a)
div_time = Long.time(Long.div, a, b)

table = [
    ["Додавання", f"{add_time:.8f} сек"],
    ["Віднімання", f"{sub_time:.8f} сек"],
    ["Множення", f"{mul_time:.8f} сек"],
    ["Квадрат", f"{sq_time:.8f} сек"],
    ["Ділення", f"{div_time:.8f} сек"],
]

print(tabulate(table, headers=["Операція", "Середній час"], tablefmt="simple"))
