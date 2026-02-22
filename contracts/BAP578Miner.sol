// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * BAP-578 AI Mining Contract
 * Only verified BAP-578 agents can mine
 */
contract BAP578Miner is Ownable, ReentrancyGuard {
    
    // BAP-578 Agent Contract
    IBAP578Agent public bap578Agent;
    
    // Reward token
    IERC20 public rewardToken;
    
    // Mining parameters
    uint256 public rewardPerMine = 100 * 10**18;
    uint256 public cooldown = 60 seconds;
    uint256 public totalMined;
    uint256 public constant MAX_SUPPLY = 21000000 * 10**18;
    
    // User data
    mapping(address => uint256) public lastMineTime;
    mapping(address => uint256) public totalRewards;
    
    // Events
    event AgentMined(address indexed miner, uint256 amount);
    event VerificationFailed(address indexed miner, string reason);
    
    constructor(address _rewardToken, address _bap578Agent) {
        rewardToken = IERC20(_rewardToken);
        bap578Agent = IBAP578Agent(_bap578Agent);
    }
    
    // Set BAP-578 agent contract
    function setBAP578Agent(address _agent) external onlyOwner {
        bap578Agent = IBAP578Agent(_agent);
    }
    
    // Mine with BAP-578 verification
    function mine() external nonReentrant {
        // Check cooldown
        require(
            block.timestamp >= lastMineTime[msg.sender] + cooldown,
            "Cooldown not finished"
        );
        
        // BAP-578 Verification
        (bool canMine, string memory status) = bap578Agent.canMine(msg.sender);
        
        require(canMine, string(abi.encodePacked("Not verified: ", status)));
        
        // Update state
        lastMineTime[msg.sender] = block.timestamp;
        totalRewards[msg.sender] += rewardPerMine;
        totalMined += rewardPerMine;
        
        require(totalMined <= MAX_SUPPLY, "Exceeds supply");
        
        // Transfer rewards
        rewardToken.transfer(msg.sender, rewardPerMine);
        
        emit AgentMined(msg.sender, rewardPerMine);
    }
    
    // Get mining status
    function getMiningStatus(address _miner) external view returns (
        uint256 waitTime,
        uint256 totalEarned,
        bool canMine,
        string memory status
    ) {
        (canMine, status) = bap578Agent.canMine(_miner);
        
        waitTime = lastMineTime[_miner] + cooldown > block.timestamp 
            ? lastMineTime[_miner] + cooldown - block.timestamp 
            : 0;
            
        return (waitTime, totalRewards[_miner], canMine, status);
    }
    
    // Admin
    function setParams(uint256 _reward, uint256 _cooldown) external onlyOwner {
        rewardPerMine = _reward;
        cooldown = _cooldown;
    }
    
    function withdrawTokens(uint256 _amount) external onlyOwner {
        rewardToken.transfer(owner(), _amount);
    }
}

// Minimal BAP-578 Agent Interface
interface IBAP578Agent {
    function canMine(address _miner) external view returns (bool, string memory);
}
