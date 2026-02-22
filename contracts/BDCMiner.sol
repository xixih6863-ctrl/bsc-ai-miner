// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * BDC Miner - AI Powered Mining Contract
 * Rewards: 25,000 BDC per mine
 * Cooldown: 5 minutes
 */
contract BDCMiner is Ownable, ReentrancyGuard {
    IERC20 public immutable rewardToken;
    uint256 public constant REWARD_AMOUNT = 25000 * 10 ** 18;
    uint256 public constant COOLDOWN = 5 minutes;
    uint256 public constant GAS_FEE = 0.005 ether;
    
    mapping(address => uint256) public lastMineTime;
    mapping(address => uint256) public miningCount;
    mapping(address => uint256) public totalMined;
    
    uint256 public totalRewardsDistributed;
    
    event Mine(address indexed user, uint256 amount, uint256 timestamp);
    event RewardsClaimed(address indexed user, uint256 amount);
    
    constructor(address _rewardToken) Ownable(msg.sender) {
        rewardToken = IERC20(_rewardToken);
    }
    
    /**
     * Mine BDC tokens
     * Requires: cooldown period passed, sufficient gas for fees
     */
    function mine() external payable nonReentrant {
        require(msg.value >= GAS_FEE, "Insufficient gas fee");
        
        address user = msg.sender;
        
        // Check cooldown
        if (lastMineTime[user] != 0) {
            require(
                block.timestamp >= lastMineTime[user] + COOLDOWN,
                "Cooldown not finished"
            );
        }
        
        // Update state
        lastMineTime[user] = block.timestamp;
        miningCount[user] += 1;
        
        // Transfer rewards
        rewardToken.transfer(user, REWARD_AMOUNT);
        totalMined[user] += REWARD_AMOUNT;
        totalRewardsDistributed += REWARD_AMOUNT;
        
        emit Mine(user, REWARD_AMOUNT, block.timestamp);
        
        // Refund excess gas
        if (msg.value > GAS_FEE) {
            payable(msg.sender).transfer(msg.value - GAS_FEE);
        }
    }
    
    /**
     * Get mining stats for a user
     */
    function getUserStats(address user) external view returns (
        uint256 count,
        uint256 total,
        uint256 lastTime,
        uint256 timeRemaining
    ) {
        count = miningCount[user];
        total = totalMined[user];
        lastTime = lastMineTime[user];
        
        if (lastTime == 0) {
            timeRemaining = 0;
        } else {
            uint256 available = lastTime + COOLDOWN;
            if (block.timestamp >= available) {
                timeRemaining = 0;
            } else {
                timeRemaining = available - block.timestamp;
            }
        }
    }
    
    /**
     * Withdraw collected fees (only owner)
     */
    function withdrawFees() external onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }
    
    /**
     * Emergency withdraw (only owner)
     */
    function emergencyWithdraw(IERC20 token) external onlyOwner {
        token.transfer(owner(), token.balanceOf(address(this)));
    }
}
