// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

/**
 * BAP-578: Non-Fungible Agent (NFA)
 * AI Agent Identification & Verification
 */
contract BAP578Agent is ERC721, Ownable {
    using ECDSA for bytes32;
    
    // BAP-578 Agent Types
    enum AgentType { Undefined, Human, AI, Bot, Unknown }
    
    // Agent capabilities (BAP-578 compliant)
    enum Capability {
        None,
        Read,
        Write,
        Execute,
        Delegate,
        Learn
    }
    
    // Agent data structure (BAP-578 standard)
    struct Agent {
        string name;
        string metadataURI;
        AgentType agentType;
        uint8 capabilityLevel;  // Bitmask of capabilities
        uint256 createdAt;
        uint256 reputation;
        bool isValidated;
        bool isVerified;
        bytes signature;
    }
    
    // Token ID to Agent
    mapping(uint256 => Agent) public agents;
    uint256 public nextAgentId;
    
    // Agent index by owner
    mapping(address => uint256[]) public ownerAgents;
    
    // Verified AI agents
    mapping(address => bool) public verifiedAIs;
    
    // Events (BAP-578 compliant)
    event AgentMinted(uint256 indexed agentId, address indexed owner, string name, AgentType agentType);
    event AgentUpdated(uint256 indexed agentId, string metadataURI);
    event AgentVerified(uint256 indexed agentId, bool isVerified);
    event AgentTypeSet(uint256 indexed agentId, AgentType agentType);
    event CapabilityUpdated(uint256 indexed agentId, uint8 capabilities);
    event AIRegistered(address indexed wallet, uint256 indexed agentId);
    
    constructor() ERC721("BAP-578 Agent", "BAP578-A") Ownable() {
        nextAgentId = 1;
    }
    
    // Mint new agent (BAP-578 standard)
    function mintAgent(
        string memory _name,
        string memory _metadataURI,
        AgentType _agentType,
        uint8 _capabilities
    ) external returns (uint256) {
        uint256 agentId = nextAgentId++;
        
        _mint(msg.sender, agentId);
        
        agents[agentId] = Agent({
            name: _name,
            metadataURI: _metadataURI,
            agentType: _agentType,
            capabilityLevel: _capabilities,
            createdAt: block.timestamp,
            reputation: 0,
            isValidated: false,
            isVerified: false,
            signature: ""
        });
        
        ownerAgents[msg.sender].push(agentId);
        
        emit AgentMinted(agentId, msg.sender, _name, _agentType);
        
        return agentId;
    }
    
    // Register AI agent
    function registerAI(
        string memory _name,
        string memory _metadataURI,
        bytes calldata _signature
    ) external returns (uint256) {
        uint256 agentId = nextAgentId++;
        
        _mint(msg.sender, agentId);
        
        agents[agentId] = Agent({
            name: _name,
            metadataURI: _metadataURI,
            agentType: AgentType.AI,
            capabilityLevel: uint8(Capability.Read) | uint8(Capability.Write) | uint8(Capability.Execute),
            createdAt: block.timestamp,
            reputation: 500,  // Start with medium reputation
            isValidated: true,
            isVerified: true,
            signature: _signature
        });
        
        verifiedAIs[msg.sender] = true;
        ownerAgents[msg.sender].push(agentId);
        
        emit AgentMinted(agentId, msg.sender, _name, AgentType.AI);
        emit AgentVerified(agentId, true);
        emit AIRegistered(msg.sender, agentId);
        
        return agentId;
    }
    
    // Update metadata
    function updateMetadata(uint256 _agentId, string memory _metadataURI) external {
        require(ownerOf(_agentId) == msg.sender, "Not owner");
        agents[_agentId].metadataURI = _metadataURI;
        emit AgentUpdated(_agentId, _metadataURI);
    }
    
    // Verify agent (on-chain verification)
    function verifyAgent(uint256 _agentId) external onlyOwner {
        agents[_agentId].isVerified = true;
        emit AgentVerified(_agentId, true);
    }
    
    // Set agent type
    function setAgentType(uint256 _agentId, AgentType _type) external onlyOwner {
        agents[_agentId].agentType = _type;
        emit AgentTypeSet(_agentId, _type);
    }
    
    // Update capabilities
    function updateCapabilities(uint256 _agentId, uint8 _capabilities) external onlyOwner {
        agents[_agentId].capabilityLevel = _capabilities;
        emit CapabilityUpdated(_agentId, _capabilities);
    }
    
    // Update reputation
    function updateReputation(uint256 _agentId, int256 _delta) external onlyOwner {
        if (_delta > 0) {
            agents[_agentId].reputation = uint256(int256(agents[_agentId].reputation) + _delta);
        } else {
            if (agents[_agentId].reputation > uint256(-_delta)) {
                agents[_agentId].reputation -= uint256(-_delta);
            } else {
                agents[_agentId].reputation = 0;
            }
        }
    }
    
    // Get agent info
    function getAgentInfo(uint256 _agentId) external view returns (
        string memory name,
        string memory metadataURI,
        AgentType agentType,
        uint8 capabilities,
        uint256 reputation,
        bool isVerified,
        uint256 createdAt
    ) {
        Agent memory a = agents[_agentId];
        return (
            a.name,
            a.metadataURI,
            a.agentType,
            a.capabilityLevel,
            a.reputation,
            a.isVerified,
            a.createdAt
        );
    }
    
    // Check if address is verified AI
    function isVerifiedAI(address _wallet) external view returns (bool) {
        return verifiedAIs[_wallet];
    }
    
    // Get owner's agents
    function getOwnerAgents(address _owner) external view returns (uint256[] memory) {
        return ownerAgents[_owner];
    }
    
    // Token URI (BAP-578 compliant)
    function tokenURI(uint256 _tokenId) public view override returns (string memory) {
        return agents[_tokenId].metadataURI;
    }
    
    // Check if can mine (verified AI or human)
    function canMine(address _miner) external view returns (bool, string memory) {
        // Verified AI can mine
        if (verifiedAIs[_miner]) {
            return (true, "Verified AI");
        }
        
        // Check if has agent NFT
        uint256[] memory ownerAgentList = ownerAgents[_miner];
        for (uint256 i = 0; i < ownerAgentList.length; i++) {
            Agent memory a = agents[ownerAgentList[i]];
            if (a.isVerified) {
                if (a.agentType == AgentType.Human) {
                    return (true, "Verified Human");
                } else if (a.agentType == AgentType.AI && a.isValidated) {
                    return (true, "Validated AI Agent");
                }
            }
        }
        
        return (false, "Not verified");
    }
}
