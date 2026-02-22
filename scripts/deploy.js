import hre from "hardhat";

async function main() {
    console.log("========================================");
    console.log("  BAIM AI Miner - Deploy Script");
    console.log("========================================\n");
    
    const [deployer] = await hre.ethers.getSigners();
    console.log("Deployer:", deployer.address);
    
    const balance = await hre.ethers.provider.getBalance(deployer.address);
    console.log("Balance:", hre.ethers.utils.formatEther(balance), "BNB\n");
    
    // 1. Deploy BAIM Token
    console.log("1. Deploying BAIM Token...");
    const BAIMToken = await hre.ethers.getContractFactory("BAIMToken");
    const token = await BAIMToken.deploy();
    await token.deployed();
    console.log("   BAIM Token:", token.address);
    
    // 2. Deploy Miner Contract
    console.log("\n2. Deploying BAIM Miner...");
    const BAIMMiner = await hre.ethers.getContractFactory("BAIMMiner");
    const miner = await BAIMMiner.deploy(token.address, deployer.address);
    await miner.deployed();
    console.log("   BAIM Miner:", miner.address);
    
    // 3. Configure
    console.log("\n3. Configuring...");
    
    // Mint tokens to miner
    const mintAmount = hre.ethers.utils.parseEther("10000000"); // 10M tokens
    await token.mint(miner.address, mintAmount);
    console.log("   Minted 10M BAIM to miner");
    
    // Add miner as minter
    await token.addMinter(miner.address);
    console.log("   Added miner as minter");
    
    // Set mining params
    await miner.setParams(hre.ethers.utils.parseEther("100"), 60); // 100 BAIM, 60s cooldown
    console.log("   Set mining params: 100 BAIM/task, 60s cooldown");
    
    // Verify
    console.log("\n========================================");
    console.log("  Deployment Complete!");
    console.log("========================================\n");
    console.log("BAIM Token:", token.address);
    console.log("BAIM Miner:", miner.address);
    console.log("\nNetwork:", hre.network.name);
    console.log("Explorer: https://testnet.bscscan.com/");
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
