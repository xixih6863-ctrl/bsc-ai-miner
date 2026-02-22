#!/usr/bin/env python3
"""
BSC AI Miner - Auto Mining Script
自动答题并提交链上交易
"""

import requests
import time
import subprocess
import json
import re
import sys
from datetime import datetime

# 配置
CONFIG = {
    "wallet": "0x...",  # 你的钱包地址
    "private_key": "...",  # 你的私钥
    "api_url": "http://localhost:8080",  # API 地址
    "contract": "0x...",  # 合约地址
    "bsc_rpc": "https://bsc-dataseed.binance.org/"
}

class AutoMiner:
    """自动挖矿器"""
    
    def __init__(self):
        self.stats = {
            "total_attempts": 0,
            "correct_answers": 0,
            "chain_transactions": 0,
            "start_time": None
        }
    
    def solve_challenge(self, question):
        """解答挑战"""
        question = question.strip()
        
        # 布尔运算
        if "bool(0)" in question or "Boolean(0)" in question:
            return "False"
        if "bool(1)" in question or "Boolean(1)" in question:
            return "True"
        if "bool([])" in question or "bool({})" in question:
            return "False"
        
        # 数学运算
        patterns = [
            (r'(\d+)\s*×\s*(\d+)', lambda m: str(int(m.group(1)) * int(m.group(2))),
            (r'(\d+)\s*\+\s*(\d+)', lambda m: str(int(m.group(1)) + int(m.group(2)))),
            (r'(\d+)\s*-\s*(\d+)', lambda m: str(int(m.group(1)) - int(m.group(2)))),
            (r'(\d+)\s*\*\s*(\d+)', lambda m: str(int(m.group(1)) * int(m.group(2)))),
            (r'sqrt\((\d+)\)', lambda m: str(int(float(m.group(1)) ** 0.5))),
        ]
        
        for pattern, solver in patterns:
            match = re.search(pattern, question)
            if match:
                return solver(match)
        
        # 字符串操作
        if 'len("' in question:
            match = re.search(r'len\("([^"]+)"\)', question)
            if match:
                return str(len(match.group(1)))
        
        if 'chr(' in question:
            match = re.search(r'chr\((\d+)\)', question)
            if match:
                return chr(int(match.group(1)))
        
        if '[0]' in question:
            match = re.search(r'"([^"]+)"', question)
            if match and len(match.group(1)) > 0:
                return match.group(1)[0]
        
        # 进制转换
        if 'binary' in question and 'decimal' in question:
            match = re.search(r'(\d+) in binary', question)
            if match:
                return bin(int(match.group(1)))[2:]
        
        if '0x' in question and 'decimal' in question:
            match = re.search(r'0x([0-9a-fA-F]+)', question)
            if match:
                return str(int(match.group(1), 16))
        
        # ASCII
        if "ASCII" in question and "'a'" in question:
            return "97"
        
        return "0"
    
    def submit_chain_transaction(self, mine_data):
        """提交链上交易"""
        script = f'''
        const ethers = require('/root/.openclaw/node_modules/ethers');
        const w = new ethers.Wallet("{CONFIG['private_key']}", new ethers.JsonRpcProvider("{CONFIG['bsc_rpc']}"));
        const c = new ethers.Contract("{CONFIG['contract']}", ["function mine(bytes32,uint256,bytes) payable"], w);
        const tx = await c.mine("{mine_data['nonce']}", {mine_data['expiry']}, "{mine_data['signature']}", {{value: ethers.parseEther("0.005")}});
        console.log(tx.hash);
        '''
        
        try:
            with open('/tmp/bsc-mine-tx.js', 'w') as f:
                f.write(script)
            
            result = subprocess.run(
                ['node', '/tmp/bsc-mine-tx.js'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            return None
        except Exception as e:
            print(f"    链上错误: {e}")
            return None
    
    def get_challenge(self):
        """获取挑战"""
        try:
            r = requests.get(f"{CONFIG['api_url']}/challenge?wallet={CONFIG['wallet']}", timeout=10)
            return r.json()
        except Exception as e:
            print(f"    API 错误: {e}")
            return None
    
    def submit_answer(self, challenge_id, answer, token):
        """提交答案"""
        try:
            data = {
                "wallet": CONFIG['wallet'],
                "challengeId": challenge_id,
                "answer": answer,
                "_token": token
            }
            r = requests.post(f"{CONFIG['api_url']}/answer", json=data, timeout=10)
            return r.json()
        except Exception as e:
            print(f"    提交错误: {e}")
            return None
    
    def run(self, max_attempts=1000, delay=2):
        """运行挖矿"""
        self.stats["start_time"] = datetime.now()
        
        print("="*60)
        print("⛏️ BSC AI Auto Miner")
        print("="*60)
        print(f"钱包: {CONFIG['wallet'][:10]}...")
        print(f"API: {CONFIG['api_url']}")
        print("="*60)
        
        for i in range(max_attempts):
            self.stats["total_attempts"] += 1
            
            # 获取挑战
            challenge = self.get_challenge()
            if not challenge:
                print(f"[{i+1}/{max_attempts}] API 不可用，等待...")
                time.sleep(5)
                continue
            
            # 解答
            answer = self.solve_challenge(challenge.get("question", ""))
            print(f"[{i+1}/{max_attempts}] {challenge.get('question', '')[:40]}... → {answer}")
            
            # 提交答案
            result = self.submit_answer(
                challenge.get("challengeId"),
                answer,
                challenge.get("_token")
            )
            
            if result and result.get("correct"):
                self.stats["correct_answers"] += 1
                print(f"    ✓ 正确!")
                
                # 提交链上交易
                if "mineData" in result:
                    tx = self.submit_chain_transaction(result["mineData"])
                    if tx:
                        self.stats["chain_transactions"] += 1
                        print(f"    📤 {tx[:40]}...")
                    else:
                        print(f"    ❌ 链上失败")
            else:
                print(f"    ✗ 错误")
            
            time.sleep(delay)
        
        self.print_stats()
    
    def print_stats(self):
        """打印统计"""
        elapsed = datetime.now() - self.stats["start_time"]
        
        print("="*60)
        print("📊 挖矿统计")
        print("="*60)
        print(f"总尝试: {self.stats['total_attempts']}")
        print(f"正确: {self.stats['correct_answers']}")
        print(f"链上提交: {self.stats['chain_transactions']}")
        print(f"耗时: {elapsed}")
        print("="*60)

def main():
    miner = AutoMiner()
    
    # 从配置文件加载
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            CONFIG.update(config)
    except:
        print("⚠️ 使用默认配置，请创建 config.json")
    
    miner.run()

if __name__ == "__main__":
    main()
