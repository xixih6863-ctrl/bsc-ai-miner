// BAP-578 AI Mining Script
// No mint needed - just mine!

const { ethers } = require('ethers');

// Configuration
const PRIVATE_KEY = process.env.MINER_PRIVATE_KEY || 'your_private_key_here';

// Contract Addresses
const CONTRACTS = {
    token: '0xDC7Cb643ECEB34F721A712863D1B3a79B3852aa8',
    agent: '0x9c60F91FceF96771B5b1fC33bef6c95c45977633',
    miner: '0x2e49FEbf9bac290f19313c32dAC1D9F06Cc8FEB1'
};

// RPC
const RPC = 'https://bsc-dataseed.binance.org/';

async function mine() {
    console.log('='.repeat(40));
    console.log('  BAIM BAP-578 AI Mining');
    console.log('='.repeat(40));
    
    // Connect
    const provider = new ethers.providers.JsonRpcProvider(RPC);
    const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
    console.log('\nWallet:', wallet.address);
    
    // Check balance
    const bal = await provider.getBalance(wallet.address);
    console.log('BNB:', ethers.utils.formatEther(bal));
    
    if (bal.lt(ethers.utils.parseEther('0.005'))) {
        console.log('\n❌ Need BNB for gas!');
        return;
    }
    
    // Check if verified AI
    const agentABI = ['function isVerifiedAI(address) view returns (bool)'];
    const agent = new ethers.Contract(CONTRACTS.agent, agentABI, provider);
    const isAI = await agent.isVerifiedAI(wallet.address);
    
    if (!isAI) {
        console.log('\n📝 Registering AI Agent...');
        const regABI = ['function registerAI(string,string,bytes) returns (uint256)'];
        const reg = new ethers.Contract(CONTRACTS.agent, regABI, wallet);
        const tx = await reg.registerAI('BAIM-Miner-AI', 'ipfs://baim', '0x00');
        await tx.wait();
        console.log('✅ AI Registered!');
    } else {
        console.log('\n✅ Already verified AI');
    }
    
    // Mine
    console.log('\n⛏️ Mining...');
    const minerABI = ['function mine()'];
    const miner = new ethers.Contract(CONTRACTS.miner, minerABI, wallet);
    
    try {
        const tx = await miner.mine({ gasLimit: 200000 });
        console.log('Tx:', tx.hash);
        await tx.wait();
        
        // Check balance
        const tokenABI = ['function balanceOf(address) view returns (uint256)'];
        const token = new ethers.Contract(CONTRACTS.token, tokenABI, provider);
        const newBal = await token.balanceOf(wallet.address);
        
        console.log('\n✅ SUCCESS!');
        console.log('💰 Balance:', ethers.utils.formatEther(newBal), 'BAIM');
    } catch (e) {
        console.log('\n❌ Error:', e.message.substring(0, 100));
    }
}

// Auto mine loop
async function autoMine(intervalMs = 60000) {
    console.log('🔄 Auto-mining every', intervalMs/1000, 'seconds');
    
    while (true) {
        try {
            await mine();
        } catch (e) {
            console.log('Error:', e.message.substring(0, 50));
        }
        await new Promise(r => setTimeout(r, intervalMs));
    }
}

// Run
const args = process.argv.slice(2);
if (args[0] === '--auto') {
    autoMine();
} else {
    mine();
}
