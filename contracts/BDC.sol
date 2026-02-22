// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * BDC (Botcoin) - AI Agent Token
 * Total Supply: 1,000,000,000 BDC
 */
contract BDC is ERC20, Ownable {
    uint256 public constant INITIAL_SUPPLY = 1000000000 * 10 ** 18;
    
    constructor() ERC20("Botcoin", "BDC") Ownable(msg.sender) {
        _mint(msg.sender, INITIAL_SUPPLY);
    }
    
    /**
     * Mint additional tokens (only owner)
     */
    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }
    
    /**
     * Burn tokens
     */
    function burn(uint256 amount) external {
        _burn(msg.sender, amount);
    }
}
