#!/usr/bin/env node

import { ethers } from "ethers";
import fs from "fs";

// Configuration
const TESTNET_RPC = "https://data-seed-prebsc-1-s1.bnbchain.org:8545";
const PRIVATE_KEY = "0462b093216213ab41e9dc099663f4f4192ed1bf03ac1aae1a2ffd08ef734b1f";

function loadArtifact(name) {
    const abi = JSON.parse(fs.readFileSync(`artifacts/${name}.abi`, "utf8"));
    const bin = fs.readFileSync(`artifacts/${name}.bin`, "utf8");
    return { abi, bin };
}

async function main() {
    console.log("========================================");
    console.log("  BAIM AI Miner - Deploy Script");
    console.log("========================================\n");
    
    // Connect to BSC Testnet
    const provider = new ethers.providers.JsonRpcProvider(TESTNET_RPC);
    const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
    
    console.log("Deployer:", wallet.address);
    
    const balance = await provider.getBalance(wallet.address);
    console.log("Balance:", ethers.utils.formatEther(balance), "BNB\n");
    
    if (balance.lt(ethers.utils.parseEther("0.01"))) {
        console.log("❌ Insufficient BNB! Please get testnet BNB from:");
        console.log("   https://www.bnbchain.org/en/testnet-faucet");
        console.log("\n   Or use MetaMask to switch to BSC Testnet and claim from faucet.");
        process.exit(1);
    }
    
    // Load artifacts
    const tokenArtifact = loadArtifact("contracts_BAIMToken_sol_BAIMToken");
    const minerArtifact = loadArtifact("contracts_BAIMMiner_sol_BAIMMiner");
    
    // 1. Deploy BAIM Token
    console.log("1. Deploying BAIM Token...");
    const tokenFactory = new ethers.ContractFactory(tokenArtifact.abi, tokenArtifact.bin, wallet);
    const token = await tokenFactory.deploy();
    await token.deployed();
    console.log("   BAIM Token:", token.address);
    
    // 2. Deploy Miner Contract
    console.log("\n2. Deploying BAIM Miner...");
    const minerFactory = new ethers.ContractFactory(minerArtifact.abi, minerArtifact.bin, wallet);
    const miner = await minerFactory.deploy(token.address, wallet.address);
    await miner.deployed();
    console.log("   BAIM Miner:", miner.address);
    
    // 3. Configure
    console.log("\n3. Configuring...");
    
    // Mint tokens to miner
    const mintAmount = ethers.utils.parseEther("10000000"); // 10M tokens
    await token.mint(miner.address, mintAmount);
    console.log("   ✓ Minted 10M BAIM to miner");
    
    // Add miner as minter
    await token.addMinter(miner.address);
    console.log("   ✓ Added miner as minter");
    
    // Set mining params
    await miner.setParams(ethers.utils.parseEther("100"), 60);
    console.log("   ✓ Set mining params: 100 BAIM/task, 60s cooldown");
    
    // Save addresses
    const config = {
        network: "bsc-testnet",
        timestamp: new Date().toISOString(),
        deployer: wallet.address,
        contracts: {
            BAIMToken: token.address,
            BAIMMiner: miner.address
        }
    };
    fs.writeFileSync("deploy-config.json", JSON.stringify(config, null, 2));
    
    // Summary
    console.log("\n========================================");
    console.log("  ✅ Deployment Complete!");
    console.log("========================================\n");
    console.log("📋 Contract Addresses:");
    console.log("   BAIM Token:", token.address);
    console.log("   BAIM Miner:", miner.address);
    console.log("\n🔗 BSCScan Testnet:");
    console.log("   Token: https://testnet.bscscan.com/address/" + token.address);
    console.log("   Miner: https://testnet.bscscan.com/address/" + miner.address);
    
    console.log("\n💾 Config saved to: deploy-config.json");
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error("❌ Error:", error.message);
        process.exit(1);
    });
