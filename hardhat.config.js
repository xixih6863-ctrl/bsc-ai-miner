import "@nomicfoundation/hardhat-toolbox";
import "dotenv/config";

/** @type import('hardhat/config').HardhatUserConfig */
export default {
  solidity: "0.8.20",
  networks: {
    bscTestnet: {
      url: "https://data-seed-prebsc-1-s1.bnbchain.org:8545",
      chainId: 97,
      accounts: [process.env.PRIVATE_KEY ? "0x" + process.env.PRIVATE_KEY : []].filter(Boolean),
    },
    bsc: {
      url: "https://bsc-dataseed.binance.org/",
      chainId: 56,
      accounts: [process.env.PRIVATE_KEY ? "0x" + process.env.PRIVATE_KEY : []].filter(Boolean),
    },
  },
};
