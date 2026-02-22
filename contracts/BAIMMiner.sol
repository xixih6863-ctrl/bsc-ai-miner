// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * BAIM AI Miner - AI 挑战挖矿合约
 * 解决复杂数学/密码学问题获得代币奖励
 */
contract BAIMMiner is Ownable, ReentrancyGuard {
    
    // 事件
    event ChallengePosted(uint256 indexed challengeId, string challengeType, uint256 reward);
    event SolutionSubmitted(uint256 indexed challengeId, address indexed solver);
    event ChallengeSolved(uint256 indexed challengeId, address indexed solver, string answer);
    event RewardClaimed(address indexed user, uint256 amount);
    
    // 状态变量
    uint256 public totalMined;
    uint256 public constant MAX_SUPPLY = 21000000 * 10**18;
    uint256 public tokensPerChallenge = 100 * 10**18;
    uint256 public cooldown = 30 seconds;
    uint256 public challengeCount;
    
    address public rewardToken;
    address public feeRecipient;
    
    // 挑战结构
    struct Challenge {
        string challengeType;
        string challengeHash;  // 答案的 hash
        uint256 reward;
        bool solved;
        address solver;
        uint256 timestamp;
    }
    
    mapping(uint256 => Challenge) public challenges;
    mapping(address => uint256) public lastSolveTime;
    mapping(address => uint256) public totalRewards;
    
    // 答案验证
    mapping(bytes32 => bool) public usedSolutions;
    
    constructor(address _rewardToken, address _feeRecipient) {
        rewardToken = _rewardToken;
        feeRecipient = _feeRecipient;
    }
    
    // 设置挖矿参数
    function setParams(uint256 _tokensPerChallenge, uint256 _cooldown) external onlyOwner {
        tokensPerChallenge = _tokensPerChallenge;
        cooldown = _cooldown;
    }
    
    // 发布新挑战
    function postChallenge(string calldata _type, string calldata _challengeHash) external onlyOwner returns (uint256) {
        challengeCount++;
        challenges[challengeCount] = Challenge({
            challengeType: _type,
            challengeHash: _challengeHash,
            reward: tokensPerChallenge,
            solved: false,
            solver: address(0),
            timestamp: block.timestamp
        });
        
        emit ChallengePosted(challengeCount, _type, tokensPerChallenge);
        return challengeCount;
    }
    
    // 提交答案
    function submitSolution(uint256 _challengeId, string calldata _answer) external nonReentrant {
        Challenge storage challenge = challenges[_challengeId];
        
        require(challenge.reward > 0, "Challenge not found");
        require(!challenge.solved, "Already solved");
        require(
            block.timestamp >= lastSolveTime[msg.sender] + cooldown,
            "Cooldown not finished"
        );
        
        // 验证答案
        bytes32 answerHash = keccak256(abi.encodePacked(_answer));
        require(keccak256(abi.encodePacked(challenge.challengeHash)) == keccak256(abi.encodePacked(answerHash)), "Wrong answer");
        require(!usedSolutions[answerHash], "Solution already used");
        
        // 标记为已使用
        usedSolutions[answerHash] = true;
        
        // 更新挑战状态
        challenge.solved = true;
        challenge.solver = msg.sender;
        
        // 更新用户状态
        lastSolveTime[msg.sender] = block.timestamp;
        totalRewards[msg.sender] += challenge.reward;
        totalMined += challenge.reward;
        
        // 转移代币
        require(totalMined <= MAX_SUPPLY, "Exceeds supply");
        IERC20(rewardToken).transfer(msg.sender, challenge.reward);
        
        emit ChallengeSolved(_challengeId, msg.sender, _answer);
        emit RewardClaimed(msg.sender, challenge.reward);
    }
    
    // 简单的挖矿 (用于测试)
    function simpleMine() external nonReentrant {
        require(
            block.timestamp >= lastSolveTime[msg.sender] + cooldown,
            "Cooldown not finished"
        );
        
        lastSolveTime[msg.sender] = block.timestamp;
        totalRewards[msg.sender] += tokensPerChallenge;
        totalMined += tokensPerChallenge;
        
        require(totalMined <= MAX_SUPPLY, "Exceeds supply");
        IERC20(rewardToken).transfer(msg.sender, tokensPerChallenge);
        
        emit RewardClaimed(msg.sender, tokensPerChallenge);
    }
    
    // 获取用户统计
    function getUserStats(address _user) external view returns (
        uint256 lastSolve,
        uint256 totalReward,
        uint256 waitTime
    ) {
        waitTime = lastSolveTime[_user] + cooldown > block.timestamp 
            ? lastSolveTime[_user] + cooldown - block.timestamp 
            : 0;
        return (lastSolveTime[_user], totalRewards[_user], waitTime);
    }
    
    // 紧急提款
    function emergencyWithdraw() external onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }
    
    // 提取代币
    function withdrawTokens(uint256 amount) external onlyOwner {
        IERC20(rewardToken).transfer(owner(), amount);
    }
}
