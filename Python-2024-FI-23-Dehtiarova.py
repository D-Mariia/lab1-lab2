import time
from tabulate import tabulate


def hex_to_32(hex_num):
    n = int(hex_num, 16)
    array = []
    while n:
        array.append(n % 2**32)
        n //= 2**32
    return array


def from32_to2(blocks):
    binary_str = ''.join(f'{block:032b}' for block in reversed(blocks))
    return binary_str.lstrip('0') or '0'


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

        while len(result) > 1 and result[-1] == 0:
            result.pop()

        return result

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
    def shift_right(a):
        carry = 0
        for i in range(len(a) - 1, -1, -1):
            current = (carry << 32) | a[i]
            a[i] = current >> 1
            carry = current & 1
        while len(a) > 1 and a[-1] == 0:
            a.pop()
        return a

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
    def time(func, a, b, iterations=100):
        start_time = time.time()
        for _ in range(iterations):
            func(a, b)
        end_time = time.time()
        return (end_time - start_time) / iterations

    @staticmethod
    def gcd(a, b):
        a = a.copy()
        b = b.copy()
        d = [1]

        while (a[0] % 2 == 0) and (b[0] % 2 == 0):
            a = Long.shift_right(a)
            b = Long.shift_right(b)
            d = Long. mul_one(d, 2)

        while a[0] % 2 == 0:
            a = Long.shift_right(a)

        while b != [0]:
            while b[0] % 2 == 0:
                b = Long.shift_right(b)

            if Long.cmp(a, b) > 0:
                a = Long.sub(a, b)
            else:
                b = Long.sub(b, a)

        d = Long.mul(d, a)

        while len(d) > 1 and d[-1] == 0:
            d.pop()
        return d

    @staticmethod
    def lcm(a, b):
        if a == [0] or b == [0]:
            return [0]

        product = Long.mul(a.copy(), b.copy())
        gcd_ab = Long.gcd(a.copy(), b.copy())

        if Long.cmp(gcd_ab, [1]) == 0:
            return product

        q, _ = Long.div(product, gcd_ab)
        return q

    @staticmethod
    def u(n, k):
        b_2k = [0] * (2 * k) + [1]
        u, _ = Long.div(b_2k, n)
        return u

    @staticmethod
    def kill_last_digits(num, k):
        if k < len(num):
            num = num[k:]
        else:
            num = [0]
        return num

    @staticmethod
    def barrett(x, n, u):
        k = len(n)

        q = Long.kill_last_digits(x, k - 1)
        q = Long.mul(q, u)
        q = Long.kill_last_digits(q, k + 1)
        qn = Long.mul(q, n)

        if len(qn) > len(x):
            qn = qn[:len(x)]

        r = Long.sub(x, qn)

        while Long.cmp(r, n) >= 0:
            r = Long.sub(r, n)

        return r

    @staticmethod
    def add_mod(a, b, n):
        k = len(n)
        u = Long.u(n, k)

        a = Long.barrett(a, n, u)
        b = Long.barrett(b, n, u)
        s = Long.barrett(Long.add(a, b), n, u)
        return s

    @staticmethod
    def sub_mod(a, b, n):
        k = len(n)
        u = Long.u(n, k)

        a = Long.barrett(a, n, u)
        b = Long.barrett(b, n, u)

        if Long.cmp(a, b) >= 0:
            s = Long.sub(a, b)
        else:
            s = Long.add(Long.sub(a, b), n)

        s = Long.barrett(s, n, u)
        return s

    @staticmethod
    def mul_mod(a, b, n, u=None):
        k = len(n)

        if u is None:
            u = Long.u(n, k)

        a = Long.barrett(a, n, u)
        b = Long.barrett(b, n, u)

        result = Long.barrett(Long.mul(a, b), n, u)

        return result


    @staticmethod
    def power_mod(a, b, n):
        C = [1]
        k = len(n)
        u = Long.u(n, k)
        a = Long.barrett(a, n, u)
        b = from32_to2(b)
        for i in range(len(b) - 1, -1, -1):
            if b[i] == '1':
                C = Long.mul_mod(a, C, n, u)
            a = Long.mul_mod(a, a,  n, u)
        return C

    @staticmethod
    def time_mod(func, a, b, n, iterations=10):
        start_time = time.time()
        for _ in range(iterations):
            func(a, b, n)
        end_time = time.time()
        return (end_time - start_time) / iterations


a = ''
b = ''
n = ''


a = hex_to_32(a)
b = hex_to_32(b)
n = hex_to_32(n)

#"""

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

result_gcd = Long.gcd(a, b)
result_gcd = ''.join(f'{x:08x}' for x in reversed(result_gcd)).lstrip('0') or '0'
print("НСД  :", result_gcd)

result_lcm = Long.lcm(a, b)
result_lcm = ''.join(f'{x:08x}' for x in reversed(result_lcm)).lstrip('0') or '0'
print("НСК :", result_lcm)

result_add_mod = Long.add_mod(a, b, n)
result_add_mod = ''.join(f'{x:08x}' for x in reversed(result_add_mod)).lstrip('0') or '0'
print("A+B mod N:", result_add_mod)

result_sub_mod = Long.sub_mod(a, b, n)
result_sub_mod = ''.join(f'{x:08x}' for x in reversed(result_sub_mod)).lstrip('0') or '0'
print("A-B mod N:", result_sub_mod)

result_mul_mod = Long.mul_mod(a, b, n)
result_mul_mod = ''.join(f'{x:08x}' for x in reversed(result_mul_mod)).lstrip('0') or '0'
print("A*B mod N:", result_mul_mod)

result_mul_mod_2 = Long.mul_mod(a, a, n)
result_mul_mod_2 = ''.join(f'{x:08x}' for x in reversed(result_mul_mod_2)).lstrip('0') or '0'
print("A^2 mod N:", result_mul_mod_2)

result_power_mod = Long.power_mod(a, b, n)
result_power_mod = ''.join(f'{x:08x}' for x in reversed(result_power_mod)).lstrip('0') or '0'
print("A^B mod N:", result_power_mod)

add_time = Long.time(Long.add, a, b)
sub_time = Long.time(Long.sub, a, b)
mul_time = Long.time(Long.mul, a, b)
sq_time = Long.time(Long.mul, a, a)
div_time = Long.time(Long.div, a, b)

gcd_time = Long.time(Long.gcd, a, a)
lcm_time = Long.time(Long.lcm, a, b)

add_mod_time = Long.time_mod(Long.add_mod, a, b, n)
sub_mod_time = Long.time_mod(Long.sub_mod, a, b, n)
mul_mod_time = Long.time_mod(Long.mul_mod, a, b, n)
sq_mod_time = Long.time_mod(Long.mul_mod, a, a, n)
pow_mod_time = Long.time_mod(Long.power_mod, a, b, n)

table = [
    ["Додавання", f"{add_time:.8f} сек"],
    ["Віднімання", f"{sub_time:.8f} сек"],
    ["Множення", f"{mul_time:.8f} сек"],
    ["Квадрат", f"{sq_time:.8f} сек"],
    ["Ділення", f"{div_time:.8f} сек"],
    ["НСД", f"{gcd_time:.8f} сек"],
    ["НСК", f"{lcm_time:.8f} сек"],
    ["Додавання(mod)", f"{add_mod_time:.8f} сек"],
    ["Віднімання(mod)", f"{sub_mod_time:.8f} сек"],
    ["Множення(mod)", f"{mul_mod_time:.8f} сек"],
    ["Квадрат(mod)", f"{sq_mod_time:.8f} сек"],
    ["Степінь(mod)", f"{pow_mod_time:.8f} сек"],
]

print(tabulate(table, headers=["Операція ", "Середній час"], tablefmt="simple"))
