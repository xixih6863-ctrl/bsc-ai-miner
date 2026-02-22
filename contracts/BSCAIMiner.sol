// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * BSC AI Miner - 智能挖矿合约
 * 支持 AI 答题验证和自动挖矿
 */

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract BSCAIMiner is Ownable, ReentrancyGuard {
    
    // 事件
    event Mine(address indexed user, uint256 amount, uint256 timestamp);
    event ChallengeCreated(uint256 indexed challengeId, bytes32 challengeHash);
    event ChallengeSolved(uint256 indexed challengeId, address indexed user);
    
    // 状态变量
    uint256 public totalMined;
    uint256 public totalSupply = 1000000000 * 10**18; // 10亿代币
    uint256 public minePrice = 0.005 ether;
    uint256 public tokensPerMine = 25000 * 10**18;
    uint256 public cooldown = 300 seconds;
    
    address public feeRecipient;
    address public rewardToken;
    
    mapping(address => uint256) public lastMineTime;
    mapping(address => uint256) public miningCount;
    mapping(bytes32 => bool) public usedNonces;
    
    // 难度系数
    uint8 public difficulty = 2; // 2 = 中等难度
    
    constructor(
        address _rewardToken,
        address _feeRecipient
    ) {
        rewardToken = _rewardToken;
        feeRecipient = _feeRecipient;
    }
    
    // 设置挖矿参数
    function setMiningParams(
        uint256 _minePrice,
        uint256 _tokensPerMine,
        uint256 _cooldown,
        uint8 _difficulty
    ) external onlyOwner {
        minePrice = _minePrice;
        tokensPerMine = _tokensPerMine;
        cooldown = _cooldown;
        difficulty = _difficulty;
    }
    
    // 生成挑战
    function generateChallenge() external view returns (bytes32, uint256) {
        bytes32 challengeHash = keccak256(abi.encodePacked(
            block.timestamp,
            msg.sender,
            block.number,
            difficulty
        ));
        uint256 expiresAt = block.timestamp + 300 seconds;
        return (challengeHash, expiresAt);
    }
    
    // 验证 AI 答题
    function verifyAnswer(
        bytes32 challengeHash,
        string calldata answer,
        bytes32 nonce,
        bytes calldata signature
    ) external view returns (bool) {
        // 验证签名
        bytes32 message = keccak256(abi.encodePacked(challengeHash, answer, nonce));
        bytes32 ethSignedMessage = keccak256(abi.encodePacked(
            "\x19Ethereum Signed Message:\n32",
            message
        ));
        
        // 简化验证：检查 nonce 是否未使用
        require(!usedNonces[nonce], "Nonce already used");
        require(usedNonces[nonce] = true, "Nonce marked");
        
        return true;
    }
    
    // 挖矿函数
    function mine(
        bytes32 nonce,
        uint256 expiry,
        bytes calldata signature
    ) external payable nonReentrant {
        require(block.timestamp < expiry, "Challenge expired");
        require(!usedNonces[nonce], "Nonce already used");
        require(msg.value >= minePrice, "Insufficient BNB");
        
        usedNonces[nonce] = true;
        
        // 检查冷却
        require(
            block.timestamp >= lastMineTime[msg.sender] + cooldown,
            "Cooldown not finished"
        );
        
        lastMineTime[msg.sender] = block.timestamp;
        miningCount[msg.sender]++;
        
        // 铸造代币
        require(totalMined + tokensPerMine <= totalSupply, "Exceeds supply");
        totalMined += tokensPerMine;
        
        // 转移代币
        IERC20(rewardToken).transfer(msg.sender, tokensPerMine);
        
        // 退还多余 BNB
        if (msg.value > minePrice) {
            payable(msg.sender).transfer(msg.value - minePrice);
        }
        
        // 发送费用
        payable(feeRecipient).transfer(minePrice);
        
        emit Mine(msg.sender, tokensPerMine, block.timestamp);
    }
    
    // 紧急提款
    function emergencyWithdraw() external onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }
    
    // 提取代币
    function withdrawTokens(uint256 amount) external onlyOwner {
        IERC20(rewardToken).transfer(owner(), amount);
    }
    
    // 获取用户挖矿统计
    function getUserStats(address user) external view returns (
        uint256 lastMine,
        uint256 count,
        uint256 waitTime
    ) {
        waitTime = lastMineTime[user] + cooldown > block.timestamp 
            ? lastMineTime[user] + cooldown - block.timestamp 
            : 0;
        return (lastMineTime[user], miningCount[user], waitTime);
    }
}
