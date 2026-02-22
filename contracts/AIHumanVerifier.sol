// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * AI vs Human Verifier
 * Distinguishes between AI agents and humans using various verification methods
 */
contract AIHumanVerifier is Ownable {
    
    // Verification methods
    enum VerificationMethod {
        None,           // Unverified
        WalletAge,      // Based on wallet age
        Challenge,      // AI can't solve certain challenges
        Signature,      // Cryptographic signature verification
        Behavioral,     // Behavioral analysis
        Staking,        // Stake-based verification
        TimeResponse,   // Human-like response time
        Captcha,        // CAPTCHA verification
        SocialVerify    // Social media verification
    }
    
    // Entity data
    struct Entity {
        bool isVerified;
        bool isAI;
        VerificationMethod method;
        uint256 verifiedAt;
        uint256 trustScore;      // 0-1000
        uint256 totalVerifications;
        address validator;
    }
    
    // Mapping
    mapping(address => Entity) public entities;
    mapping(address => bool) public whitelist;  // Known AI agents
    mapping(address => bool) public blacklist; // Known bots
    
    // Parameters
    uint256 public walletAgeThreshold = 365 days;  // 1 year
    uint256 public minTrustScore = 500;  // Minimum for AI verification
    uint256 public challengeDifficulty = 5;  // 1-10
    
    // Events
    event EntityVerified(address indexed entity, bool isAI, VerificationMethod method);
    event VerificationChallengePosted(address indexed entity, string challenge);
    event TrustScoreUpdated(address indexed entity, uint256 newScore);
    
    constructor() Ownable() {}
    
    // Set verification parameters
    function setParameters(
        uint256 _walletAgeThreshold,
        uint256 _minTrustScore,
        uint256 _difficulty
    ) external onlyOwner {
        walletAgeThreshold = _walletAgeThreshold;
        minTrustScore = _minTrustScore;
        challengeDifficulty = _difficulty;
    }
    
    // Add to AI whitelist
    function addAI(address _ai) external onlyOwner {
        whitelist[_ai] = true;
        entities[_ai].isVerified = true;
        entities[_ai].isAI = true;
        entities[_ai].method = VerificationMethod.Staking;
        entities[_ai].trustScore = 1000;
        emit EntityVerified(_ai, true, VerificationMethod.Staking);
    }
    
    // Add to blacklist
    function addToBlacklist(address _bot) external onlyOwner {
        blacklist[_bot] = true;
        entities[_bot].isVerified = true;
        entities[_bot].isAI = true;
    }
    
    // Verify by wallet age (older = more likely human)
    function verifyByWalletAge(address _entity, uint256 _deployTime) external onlyOwner {
        if (block.timestamp - _deployTime >= walletAgeThreshold) {
            Entity storage e = entities[_entity];
            e.isVerified = true;
            e.isAI = false;
            e.method = VerificationMethod.WalletAge;
            e.verifiedAt = block.timestamp;
            e.trustScore = Math.min(e.trustScore + 300, 1000);
            e.totalVerifications++;
            
            emit EntityVerified(_entity, false, VerificationMethod.WalletAge);
        }
    }
    
    // Verify by challenge (AI struggles with these)
    function verifyByChallenge(
        address _entity,
        string calldata _challenge,
        bool _passed
    ) external onlyOwner {
        Entity storage e = entities[_entity];
        e.totalVerifications++;
        
        if (_passed) {
            // Human passed - give points
            e.trustScore = Math.min(e.trustScore + 100, 1000);
        } else {
            // AI failed - suspicious
            if (e.trustScore > 0) {
                e.trustScore -= 50;
            }
        }
        
        emit TrustScoreUpdated(_entity, e.trustScore);
    }
    
    // Verify by response time (too fast = AI)
    function verifyByResponseTime(
        address _entity,
        uint256 _responseTimeMs,
        uint256 _thresholdMs
    ) external onlyOwner {
        Entity storage e = entities[_entity];
        
        if (_responseTimeMs < _thresholdMs) {
            // Too fast - likely AI
            e.isAI = true;
            e.trustScore = Math.min(e.trustScore, 200);
            e.isVerified = true;
            e.method = VerificationMethod.TimeResponse;
            
            emit EntityVerified(_entity, true, VerificationMethod.TimeResponse);
        }
    }
    
    // Get verification status
    function getStatus(address _entity) external view returns (
        bool isVerified,
        bool isAI,
        uint256 trustScore,
        VerificationMethod method
    ) {
        Entity memory e = entities[_entity];
        return (e.isVerified, e.isAI, e.trustScore, e.method);
    }
    
    // Check if can mine (human only)
    function canMine(address _entity) external view returns (bool) {
        Entity memory e = entities[_entity];
        
        // Whitelisted AI can mine
        if (whitelist[_entity]) return true;
        
        // Blacklisted can't mine
        if (blacklist[_entity]) return false;
        
        // Unverified can mine with low trust
        return e.trustScore >= 100;
    }
}

// Math library
library Math {
    function min(uint256 a, uint256 b) internal pure returns (uint256) {
        return a < b ? a : b;
    }
}
