#!/usr/bin/env python3
"""
BAIM AI Challenge Solver
使用多种AI策略解决区块链上的挑战问题
"""

import hashlib
import json
import time
import random
import math
from typing import List, Tuple, Optional
import requests

# Challenge types and their solvers
class ChallengeSolver:
    def __init__(self):
        self.strategies = [
            self.solve_math,
            self.solve_hash,
            self.solve_pattern,
            self.solve_crypto,
        ]
    
    def generate_challenge(self, challenge_type: str) -> Tuple[str, str]:
        """生成挑战并返回(挑战描述, 答案)"""
        
        if challenge_type == "math_prime":
            # 找出一个数的质因数分解
            primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
            p = random.choice(primes)
            q = random.choice(primes)
            n = p * q
            challenge = f"Find the two prime factors of {n}"
            answer = f"{min(p,q)},{max(p,q)}"
            
        elif challenge_type == "math_fibonacci":
            # 斐波那契数列
            n = random.randint(5, 20)
            fib = [1, 1]
            for i in range(2, n+1):
                fib.append(fib[-1] + fib[-2])
            challenge = f"What is the {n}th number in the Fibonacci sequence? (1-indexed)"
            answer = str(fib[n-1])
            
        elif challenge_type == "math_square_root":
            # 平方根 (整数)
            n = random.randint(10, 100) ** 2
            challenge = f"What is the square root of {n}?"
            answer = str(int(math.sqrt(n)))
            
        elif challenge_type == "hash_reverse":
            # 反转哈希 (简化版: 找前缀)
            target = hashlib.sha256(str(random.randint(1, 10000)).encode()).hexdigest()[:8]
            challenge = f"Find a number whose SHA256 starts with '{target}'"
            # 简化: 答案就是找到的数字
            answer = "0"  # 简化版本
            
        elif challenge_type == "pattern_sequence":
            # 找序列规律
            seqs = [
                ([2, 4, 8, 16, 32], "What is the next number?"),
                ([1, 1, 2, 3, 5, 8], "What is the next number?"),
                ([1, 4, 9, 16, 25], "What is the next number?"),
                ([3, 6, 9, 12, 15], "What is the next number?"),
                ([1, 4, 1, 5, 9, 2, 6], "What is the next digit of Pi?"),
            ]
            seq, q = random.choice(seqs)
            next_num = seq[-1] * 2 if seq[1] == seq[0] * 2 else seq[-1] + seq[-2] if len(seq) > 2 and seq[-1] == seq[-2] + seq[-3] else seq[-1] + 1
            challenge = f"{', '.join(map(str, seq))}... {q}"
            answer = str(next_num)
            
        elif challenge_type == "crypto_caesar":
            # 凯撒密码
            alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            shift = random.randint(3, 10)
            plain = "HELLO"
            cipher = "".join(alphabet[(alphabet.index(c) + shift) % 26] for c in plain)
            challenge = f"Decrypt this Caesar cipher (shift {shift}): {cipher}"
            answer = plain
            
        else:
            # 默认数学题
            a = random.randint(10, 50)
            b = random.randint(10, 50)
            challenge = f"What is {a} + {b}?"
            answer = str(a + b)
        
        # 返回挑战和答案的hash
        challenge_hash = hashlib.sha256(answer.encode()).hexdigest()
        return challenge, challenge_hash
    
    def solve_math(self, challenge: str) -> Optional[str]:
        """数学问题求解"""
        try:
            if "prime factors" in challenge.lower():
                import re
                nums = re.findall(r'\d+', challenge)
                if nums:
                    n = int(nums[0])
                    # 简单质因数分解
                    factors = []
                    d = 2
                    temp = n
                    while d * d <= temp:
                        while temp % d == 0:
                            factors.append(d)
                            temp //= d
                        d += 1
                    if temp > 1:
                        factors.append(temp)
                    if factors:
                        factors.sort()
                        return ",".join(map(str, factors))
            
            if "fibonacci" in challenge.lower():
                import re
                nums = re.findall(r'\d+', challenge)
                if nums:
                    n = int(nums[0])
                    fib = [1, 1]
                    for i in range(2, n+1):
                        fib.append(fib[-1] + fib[-2])
                    return str(fib[n-1])
            
            if "square root" in challenge.lower():
                import re
                nums = re.findall(r'\d+', challenge)
                if nums:
                    n = int(nums[0])
                    return str(int(math.sqrt(n)))
            
            if "+" in challenge or "-" in challenge or "*" in challenge or "/" in challenge:
                import re
                expr = re.findall(r'[\d\+\-\*\/]+', challenge)
                if expr:
                    try:
                        return str(eval(expr[0]))
                    except:
                        pass
        except:
            pass
        return None
    
    def solve_hash(self, challenge: str) -> Optional[str]:
        """哈希问题求解"""
        return None
    
    def solve_pattern(self, challenge: str) -> Optional[str]:
        """序列问题求解"""
        try:
            numbers = [int(n) for n in challenge.split() if n.isdigit()]
            if len(numbers) >= 3:
                # 等差数列
                diffs = [numbers[i+1] - numbers[i] for i in range(len(numbers)-1)]
                if len(set(diffs)) == 1:
                    return str(numbers[-1] + diffs[0])
                
                # 等比数列
                if numbers[1] != 0:
                    ratios = [numbers[i+1] / numbers[i] for i in range(len(numbers)-1)]
                    if len(set(ratios)) == 1:
                        return str(int(numbers[-1] * ratios[0]))
                
                # 斐波那契风格
                if len(numbers) >= 3:
                    for i in range(len(numbers) - 2):
                        if numbers[i+2] == numbers[i+1] + numbers[i]:
                            return str(numbers[-1] + numbers[-2])
        except:
            pass
        return None
    
    def solve_crypto(self, challenge: str) -> Optional[str]:
        """密码学问题求解"""
        try:
            if "caesar" in challenge.lower():
                import re
                # 提取位移
                shift_match = re.search(r'shift\s+(\d+)', challenge, re.IGNORECASE)
                if shift_match:
                    shift = int(shift_match.group(1))
                    # 提取密文
                    cipher = re.findall(r'[A-Z]+', challenge)
                    if cipher:
                        cipher = cipher[-1]
                        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                        plain = "".join(alphabet[(alphabet.index(c) - shift) % 26] for c in cipher)
                        return plain
        except:
            pass
        return None
    
    def solve(self, challenge: str) -> Optional[str]:
        """使用所有策略尝试解决问题"""
        for strategy in self.strategies:
            result = strategy(challenge)
            if result:
                print(f"  ✓ Solved with {strategy.__name__}: {result}")
                return result
        return None


class AIMiner:
    def __init__(self, wallet_address: str, private_key: str, contract_addr: str, token_addr: str, rpc_url: str):
        self.wallet_address = wallet_address
        self.private_key = private_key
        self.contract_addr = contract_addr
        self.token_addr = token_addr
        self.rpc_url = rpc_url
        self.solver = ChallengeSolver()
        
    def generate_and_solve(self):
        """生成挑战并解决"""
        challenge_types = ["math_prime", "math_fibonacci", "math_square_root", "pattern_sequence"]
        challenge_type = random.choice(challenge_types)
        
        print(f"\n🤖 Generating {challenge_type} challenge...")
        challenge, answer_hash = self.solver.generate_challenge(challenge_type)
        print(f"   Challenge: {challenge}")
        
        print(f"🤔 AI Solving...")
        solution = self.solver.solve(challenge)
        
        if solution:
            print(f"   ✅ Solution found: {solution}")
            return challenge, solution
        else:
            print(f"   ❌ Could not solve")
            return challenge, None


def main():
    print("=" * 50)
    print("  BAIM AI Challenge Miner")
    print("=" * 50)
    
    miner = AIMiner(
        wallet_address="0x7657bfd010f75dDB6B1EbED104fb4B11E17c8f6A",
        private_key="0462b093216213ab41e9dc099663f4f4192ed1bf03ac1aae1a2ffd08ef734b1f",
        contract_addr="",
        token_addr="",
        rpc_url="https://data-seed-prebsc-1-s1.bnbchain.org:8545"
    )
    
    # Test challenge generation and solving
    for i in range(5):
        print(f"\n{'='*50}")
        print(f"  Round {i+1}")
        print("="*50)
        
        challenge, solution = miner.generate_and_solve()
        
        if solution:
            print(f"\n🎉 Ready to submit!")
            print(f"   Challenge: {challenge}")
            print(f"   Solution: {solution}")
        else:
            print(f"\n⚠️ Need help with this one")
        
        time.sleep(1)


if __name__ == "__main__":
    main()
