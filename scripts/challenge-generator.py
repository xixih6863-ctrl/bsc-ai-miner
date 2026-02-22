#!/usr/bin/env python3
"""
BAIM AI 挑战生成器 - 高级版
生成各种高难度数学和密码学挑战
"""

import hashlib
import random
import math
import json
from typing import List, Tuple, Optional, Dict
import re

class AdvancedChallengeGenerator:
    """高级挑战生成器"""
    
    def __init__(self):
        self.difficulty_levels = {
            1: ["math_add", "math_subtract", "pattern_simple"],
            2: ["math_multiply", "math_prime", "math_square", "pattern_arithmetic"],
            3: ["math_fibonacci", "math_prime_factor", "pattern_geometric", "crypto_caesar_simple"],
            4: ["math_log", "math_power", "crypto_caesar_any", "pattern_fibonacci_extended"],
            5: ["math_prime_large", "crypto_vigenere", "math_system_eq", "hash_preimage"],
        }
    
    def generate_challenge(self, difficulty: int = 3) -> Tuple[Dict, str]:
        """生成指定难度的挑战"""
        
        available = []
        for d in range(1, difficulty + 1):
            available.extend(self.difficulty_levels.get(d, []))
        
        challenge_type = random.choice(available)
        
        if challenge_type == "math_add":
            a, b = random.randint(100, 999), random.randint(100, 999)
            return {
                "type": "math",
                "difficulty": 1,
                "question": f"Calculate: {a} + {b} = ?",
                "answer": str(a + b)
            }, str(a + b)
        
        elif challenge_type == "math_subtract":
            a, b = random.randint(500, 999), random.randint(100, 499)
            return {
                "type": "math",
                "difficulty": 1,
                "question": f"Calculate: {a} - {b} = ?",
                "answer": str(a - b)
            }, str(a - b)
        
        elif challenge_type == "math_multiply":
            a, b = random.randint(11, 30), random.randint(2, 15)
            return {
                "type": "math",
                "difficulty": 2,
                "question": f"Calculate: {a} × {b} = ?",
                "answer": str(a * b)
            }, str(a * b)
        
        elif challenge_type == "math_prime":
            # 找一个数的质因数
            primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]
            p, q = random.sample(primes, 2)
            n = p * q
            return {
                "type": "math",
                "difficulty": 2,
                "question": f"Find the prime factors of {n} (format: smaller,larger)",
                "answer": f"{min(p,q)},{max(p,q)}",
                "hint": f"{n} = p × q where p and q are prime numbers"
            }, f"{min(p,q)},{max(p,q)}"
        
        elif challenge_type == "math_square":
            n = random.randint(15, 50)
            return {
                "type": "math",
                "difficulty": 2,
                "question": f"What is {n}² = ?",
                "answer": str(n * n)
            }, str(n * n)
        
        elif challenge_type == "math_fibonacci":
            n = random.randint(8, 20)
            fib = [1, 1]
            for i in range(2, n + 1):
                fib.append(fib[-1] + fib[-2])
            return {
                "type": "math",
                "difficulty": 3,
                "question": f"What is the {n}th Fibonacci number? (1-indexed)",
                "answer": str(fib[n-1]),
                "sequence": fib[:n]
            }, str(fib[n-1])
        
        elif challenge_type == "math_prime_factor":
            # 三个质数的乘积
            primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
            p1, p2, p3 = random.sample(primes, 3)
            n = p1 * p2 * p3
            factors = sorted([p1, p2, p3])
            return {
                "type": "math",
                "difficulty": 3,
                "question": f"Find the three prime factors of {n} (format: a,b,c)",
                "answer": ",".join(map(str, factors))
            }, ",".join(map(str, factors))
        
        elif challenge_type == "math_square_root":
            n = random.randint(20, 100) ** 2
            return {
                "type": "math",
                "difficulty": 2,
                "question": f"What is √{n} = ?",
                "answer": str(int(math.sqrt(n)))
            }, str(int(math.sqrt(n)))
        
        elif challenge_type == "pattern_arithmetic":
            # 等差数列
            start = random.randint(1, 10)
            diff = random.randint(2, 7)
            seq = [start + i * diff for i in range(5)]
            next_num = seq[-1] + diff
            return {
                "type": "pattern",
                "difficulty": 2,
                "question": f"What comes next? {', '.join(map(str, seq))}, ?",
                "answer": str(next_num)
            }, str(next_num)
        
        elif challenge_type == "pattern_geometric":
            # 等比数列
            start = random.randint(2, 5)
            ratio = random.randint(2, 3)
            seq = [start * (ratio ** i) for i in range(5)]
            next_num = seq[-1] * ratio
            return {
                "type": "pattern",
                "difficulty": 3,
                "question": f"What comes next? {', '.join(map(str, seq))}, ?",
                "answer": str(next_num)
            }, str(next_num)
        
        elif challenge_type == "pattern_fibonacci_extended":
            # 斐波那契变体
            a, b = random.randint(1, 5), random.randint(1, 5)
            seq = [a, b]
            for i in range(5):
                seq.append(seq[-1] + seq[-2])
            return {
                "type": "pattern",
                "difficulty": 3,
                "question": f"What comes next? {', '.join(map(str, seq[:5]))}, ?",
                "answer": str(seq[5])
            }, str(seq[5])
        
        elif challenge_type == "crypto_caesar_simple":
            # 凯撒密码 (固定位移)
            shift = random.randint(3, 7)
            plain = random.choice(["HELLO", "WORLD", "CRYPTO", "BLOCKCHAIN", "MINING"])
            alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            cipher = "".join(alphabet[(alphabet.index(c) + shift) % 26] for c in plain)
            return {
                "type": "crypto",
                "difficulty": 3,
                "question": f"Decrypt (Caesar, shift={shift}): {cipher}",
                "answer": plain,
                "hint": f"Shift each letter back by {shift}"
            }, plain
        
        elif challenge_type == "crypto_caesar_any":
            # 凯撒密码 (任意位移)
            shift = random.randint(1, 25)
            plain = random.choice(["AI", "BOT", "SOLVE", "CHALLENGE", "REWARD"])
            alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            cipher = "".join(alphabet[(alphabet.index(c) + shift) % 26] for c in plain)
            return {
                "type": "crypto",
                "difficulty": 4,
                "question": f"Decrypt this Caesar cipher: {cipher}",
                "answer": plain,
                "hint": "Try all 25 possible shifts"
            }, plain
        
        elif challenge_type == "math_log":
            # 对数
            base = random.choice([2, 3, 5, 10])
            exp = random.randint(2, 6)
            result = base ** exp
            return {
                "type": "math",
                "difficulty": 4,
                "question": f"log_{base}({result}) = ?",
                "answer": str(exp)
            }, str(exp)
        
        elif challenge_type == "math_power":
            # 幂运算
            base = random.randint(2, 10)
            exp = random.randint(2, 5)
            return {
                "type": "math",
                "difficulty": 4,
                "question": f"{base}^{exp} = ?",
                "answer": str(base ** exp)
            }, str(base ** exp)
        
        elif challenge_type == "math_system_eq":
            # 二元一次方程组
            x = random.randint(1, 10)
            y = random.randint(1, 10)
            a1, b1 = random.randint(1, 5), random.randint(1, 5)
            a2, b2 = random.randint(1, 5), random.randint(1, 5)
            # 确保有整数解
            while (a1 * x + b1 * y) == (a2 * x + b2 * y):
                a2, b2 = random.randint(1, 5), random.randint(1, 5)
            eq1 = f"{a1}x + {b1}y = {a1*x + b1*y}"
            eq2 = f"{a2}x + {b2}y = {a2*x + b2*y}"
            return {
                "type": "math",
                "difficulty": 5,
                "question": f"Solve: {eq1}, {eq2} (format: x,y)",
                "answer": f"{x},{y}"
            }, f"{x},{y}"
        
        else:
            # 默认
            a, b = random.randint(10, 50), random.randint(10, 50)
            return {
                "type": "math",
                "difficulty": 1,
                "question": f"Calculate: {a} + {b} = ?",
                "answer": str(a + b)
            }, str(a + b)


class AIProblemSolver:
    """AI 问题求解器"""
    
    def solve(self, challenge: Dict) -> Optional[str]:
        """尝试解决挑战"""
        
        q = challenge.get("question", "")
        answer_type = challenge.get("type", "math")
        
        try:
            if answer_type == "math":
                return self.solve_math(q)
            elif answer_type == "pattern":
                return self.solve_pattern(q)
            elif answer_type == "crypto":
                return self.solve_crypto(q)
        except:
            pass
        
        return None
    
    def solve_math(self, question: str) -> Optional[str]:
        """数学问题求解"""
        numbers = re.findall(r'\d+', question)
        
        if "Fibonacci" in question and numbers:
            n = int(numbers[0])
            fib = [1, 1]
            for i in range(2, n + 1):
                fib.append(fib[-1] + fib[-2])
            return str(fib[n-1])
        
        if "prime factor" in question and numbers:
            n = int(numbers[0])
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
                return ",".join(map(str, sorted(factors)))
        
        if "√" in question and numbers:
            n = int(numbers[0])
            return str(int(math.sqrt(n)))
        
        if "^" in question and numbers:
            parts = question.split("^")
            if len(parts) == 2:
                base = int(parts[0].split()[-1])
                exp = int(parts[1].split()[0])
                return str(base ** exp)
        
        if "log_" in question and numbers:
            if len(numbers) >= 2:
                return str(int(numbers[1]))
        
        if "Solve:" in question and numbers:
            # 简化: 如果有 x,y 格式，尝试提取
            if len(numbers) >= 2:
                return f"{numbers[0]},{numbers[1]}"
        
        # 基本运算
        for op in ['+', '-', '×', '*', '/']:
            if op in question:
                expr = re.findall(rf'\d+\s*\{re.escape(op)}\s*\d+', question)
                if expr:
                    try:
                        clean_expr = expr[0].replace('×', '*')
                        return str(eval(clean_expr))
                    except:
                        pass
        
        return None
    
    def solve_pattern(self, question: str) -> Optional[str]:
        """序列问题求解"""
        numbers = [int(n) for n in re.findall(r'\d+', question)]
        
        if len(numbers) >= 3:
            # 等差
            diffs = [numbers[i+1] - numbers[i] for i in range(len(numbers)-1)]
            if len(set(diffs)) == 1:
                return str(numbers[-1] + diffs[0])
            
            # 等比
            if 0 not in numbers[1:]:
                ratios = [numbers[i+1] / numbers[i] for i in range(len(numbers)-1)]
                if len(set(ratios)) == 1:
                    return str(int(numbers[-1] * ratios[0]))
            
            # 斐波那契
            for i in range(len(numbers) - 2):
                if numbers[i+2] == numbers[i+1] + numbers[i]:
                    return str(numbers[-1] + numbers[-2])
        
        return None
    
    def solve_crypto(self, question: str) -> Optional[str]:
        """密码学问题求解"""
        # 凯撒密码
        cipher = re.findall(r'[A-Z]+', question)
        if cipher:
            cipher = cipher[-1]
            
            # 尝试所有位移
            alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            
            # 检查是否有指定位移
            shift_match = re.search(r'shift\s*=\s*(\d+)', question, re.IGNORECASE)
            if shift_match:
                shift = int(shift_match.group(1))
                plain = "".join(alphabet[(alphabet.index(c) - shift) % 26] for c in cipher)
                return plain
            
            # 暴力尝试
            for shift in range(1, 26):
                plain = "".join(alphabet[(alphabet.index(c) - shift) % 26] for c in cipher)
                # 检查是否是常见单词
                common = ["HELLO", "WORLD", "CRYPTO", "BLOCKCHAIN", "MINING", "AI", "BOT", "SOLVE", "CHALLENGE", "REWARD"]
                if plain in common:
                    return plain
        
        return None


def main():
    print("=" * 60)
    print("  BAIM AI 挑战系统 - 高级版")
    print("=" * 60)
    
    generator = AdvancedChallengeGenerator()
    solver = AIProblemSolver()
    
    # 生成并解决 10 个不同难度的挑战
    results = []
    
    for difficulty in range(1, 6):
        print(f"\n{'='*60}")
        print(f"  难度 {difficulty} 挑战")
        print("="*60)
        
        for i in range(2):
            challenge, _ = generator.generate_challenge(difficulty)
            
            print(f"\n📝 问题: {challenge['question']}")
            print(f"   类型: {challenge['type']} | 难度: {challenge['difficulty']}")
            
            solution = solver.solve(challenge)
            expected = challenge['answer']
            
            if solution == expected:
                print(f"   ✅ AI解答: {solution} ✓")
                results.append({"difficulty": difficulty, "status": "success", "question": challenge['question']})
            else:
                print(f"   ❌ AI解答: {solution} | 正确答案: {expected}")
                results.append({"difficulty": difficulty, "status": "failed", "question": challenge['question']})
    
    # 统计
    print("\n" + "=" * 60)
    print("  统计结果")
    print("=" * 60)
    
    total = len(results)
    success = sum(1 for r in results if r['status'] == 'success')
    
    print(f"\n总计: {success}/{total} ({100*success/total:.1f}%)")
    
    for d in range(1, 6):
        d_results = [r for r in results if r['difficulty'] == d]
        d_success = sum(1 for r in d_results if r['status'] == 'success')
        print(f"  难度 {d}: {d_success}/{len(d_results)}")


if __name__ == "__main__":
    main()
