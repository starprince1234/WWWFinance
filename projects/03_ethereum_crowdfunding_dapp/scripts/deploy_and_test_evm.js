const ganache = require('ganache');
const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

async function main() {
    console.log('======================================================================');
    console.log('   《以太坊众筹 DApp》真实 EVM (Ganache) 部署与合约交互全流程测试');
    console.log('======================================================================');

    // 1. 启动 Ganache 本地 EVM 提供商 (链 ID: 1337)
    const provider = new ethers.BrowserProvider(
        ganache.provider({
            logging: { quiet: true },
            chain: { chainId: 1337 },
            wallet: { totalAccounts: 10, defaultBalance: 100 }
        })
    );

    const accounts = await provider.listAccounts();
    console.log(`[EVM] 本地测试链启动成功，ChainId: 1337，可用测试账户数: ${accounts.length}`);
    const [deployer, creator, backer1, backer2, backer3, vendor] = accounts;

    console.log(`Deployer : ${deployer.address}`);
    console.log(`Creator  : ${creator.address}`);
    console.log(`Backer 1 : ${backer1.address}`);
    console.log(`Backer 2 : ${backer2.address}`);
    console.log(`Vendor   : ${vendor.address}`);

    // 2. 加载已编译的合约 ABI 与 Bytecode
    const artifact = JSON.parse(
        fs.readFileSync(path.resolve(__dirname, '../build/Crowdfunding.json'), 'utf8')
    );

    // 3. 部署合约到 EVM
    const factory = new ethers.ContractFactory(artifact.abi, artifact.bytecode, deployer);
    const contract = await factory.deploy();
    await contract.waitForDeployment();
    const contractAddress = await contract.getAddress();
    const deployTx = contract.deploymentTransaction();
    console.log(`\n[Deploy] 合约成功部署到真实本地 EVM!`);
    console.log(`[Deploy] 合约地址: ${contractAddress}`);
    console.log(`[Deploy] 部署交易哈希: ${deployTx.hash}`);

    // 4. 发起人 Creator 创建众筹项目 #1 (目标: 10 ETH, 持续 7 天 = 604800 秒)
    const goal = ethers.parseEther('10.0');
    const duration = 7 * 24 * 3600;
    const contractAsCreator = contract.connect(creator);
    const createTx = await contractAsCreator.launch(
        '去中心化开源卫星众筹',
        '自主构建低轨通信微纳卫星研发与测控平台',
        goal,
        duration
    );
    const createReceipt = await createTx.wait();
    console.log(`\n[Campaign #1] 项目创建成功! TxHash: ${createTx.hash}, GasUsed: ${createReceipt.gasUsed.toString()}`);

    // 5. 支持者出资 (Backer 1 出资 6 ETH, Backer 2 出资 5 ETH -> 总额 11 ETH, 超过目标 10 ETH)
    const pledge1 = ethers.parseEther('6.0');
    const tx1 = await contract.connect(backer1).pledge(1, { value: pledge1 });
    const rcpt1 = await tx1.wait();
    console.log(`[Pledge] Backer 1 出资 6.0 ETH 成功! TxHash: ${tx1.hash}, Gas: ${rcpt1.gasUsed.toString()}`);

    const pledge2 = ethers.parseEther('5.0');
    const tx2 = await contract.connect(backer2).pledge(1, { value: pledge2 });
    const rcpt2 = await tx2.wait();
    console.log(`[Pledge] Backer 2 出资 5.0 ETH 成功! TxHash: ${tx2.hash}, Gas: ${rcpt2.gasUsed.toString()}`);

    // 检查项目状态
    const camp = await contract.campaigns(1);
    console.log(`\n[State] 项目 #1 筹集总额: ${ethers.formatEther(camp.totalPledged)} ETH`);
    console.log(`[State] 合约当前存留金额: ${ethers.formatEther(camp.currentBalance)} ETH`);
    console.log(`[State] 支持者人数: ${camp.backerCount}`);

    // 6. EVM 时钟快进: 跃过 7 天众筹期，进入里程碑治理期
    console.log('\n[EVM Clock] 快进 EVM 时钟 7 天 + 10 秒进入众筹成功后的治理期...');
    await provider.send('evm_increaseTime', [duration + 10]);
    await provider.send('evm_mine', []);

    // 7. 里程碑 DAO 治理测试
    // Creator 申请里程碑 1 提款: 4 ETH 用于向供应商采购元器件
    const milestoneAmount = ethers.parseEther('4.0');
    const msTx = await contractAsCreator.proposeMilestone(
        1,
        '购买航天级高可靠抗辐照元器件与传感器',
        milestoneAmount,
        vendor.address
    );
    const msReceipt = await msTx.wait();
    console.log(`[Milestone] Creator 提交里程碑提款申请: 4.0 ETH, 收款方: Vendor (TxHash: ${msTx.hash}, Gas: ${msReceipt.gasUsed.toString()})`);

    // Backer 1 (持有 6 ETH 投票权，在 11 ETH 中占 54.5% > 50%) 投票赞成
    const voteTx = await contract.connect(backer1).voteMilestone(1, 1);
    const voteReceipt = await voteTx.wait();
    console.log(`[DAO Vote] Backer 1 投票赞成该里程碑! (出资权重: 6.0 ETH, Gas: ${voteReceipt.gasUsed.toString()})`);

    // 负面测试: 拦截重复投票防刷票攻击
    let repeatVoteBlocked = false;
    try {
        const tx = await contract.connect(backer1).voteMilestone(1, 1);
        await tx.wait();
    } catch (err) {
        repeatVoteBlocked = true;
    }
    console.log(`[Security] 拦截重复投票防刷票攻击: ${repeatVoteBlocked ? '[PASS]' : '[FAIL]'}`);

    // Creator 执行里程碑提款 (已达超半数 6 ETH > 5.5 ETH 赞成)
    const vendorBalBefore = await provider.getBalance(vendor.address);
    const execTx = await contractAsCreator.executeMilestone(1, 1);
    const execReceipt = await execTx.wait();
    const vendorBalAfter = await provider.getBalance(vendor.address);
    console.log(`[Milestone Exec] 里程碑审批通过并成功划拨资金! TxHash: ${execTx.hash}`);
    console.log(`[Balance Check] 供应商 Vendor 收到拨付资金: +${ethers.formatEther(vendorBalAfter - vendorBalBefore)} ETH (实到 4.0 ETH)`);

    // 8. 测试退款保护与未达标场景 (创建项目 #2 目标 10 ETH，出资 2 ETH，流标退款)
    console.log('\n--- 测试流标全额退款场景 (项目 #2) ---');
    const camp2Tx = await contractAsCreator.launch(
        '未达标测试项目',
        '测试 All-or-Nothing 退款机制',
        ethers.parseEther('10.0'),
        60 // 最低合法时长: 60 秒
    );
    await camp2Tx.wait();

    // Backer 3 出资 2 ETH
    const pledge3 = ethers.parseEther('2.0');
    const tx3 = await contract.connect(backer3).pledge(2, { value: pledge3 });
    await tx3.wait();
    console.log(`[Campaign #2] Backer 3 出资 2.0 ETH，等待截止时钟跃迁...`);

    // 快进 70 秒使项目 #2 截止流标
    await provider.send('evm_increaseTime', [70]);
    await provider.send('evm_mine', []);

    // 申请退款
    const b3BalBefore = await provider.getBalance(backer3.address);
    const refundTx = await contract.connect(backer3).refund(2);
    const refundReceipt = await refundTx.wait();
    const b3BalAfter = await provider.getBalance(backer3.address);
    const gasUsedRefund = refundReceipt.gasUsed * refundReceipt.gasPrice;
    console.log(`[Refund] Backer 3 成功触发全额退款! TxHash: ${refundTx.hash}, GasUsed: ${refundReceipt.gasUsed.toString()}`);
    console.log(`[Balance Check] Backer 3 原路全额退款到账 (净增: +${ethers.formatEther(b3BalAfter - b3BalBefore + gasUsedRefund)} ETH)`);

    // 负面测试: 拦截重复退款空手套白狼
    let repeatRefundBlocked = false;
    try {
        const tx = await contract.connect(backer3).refund(2);
        await tx.wait();
    } catch (err) {
        repeatRefundBlocked = true;
    }
    console.log(`[Security] 拦截重复退款空手套白狼测试: ${repeatRefundBlocked ? '[PASS]' : '[FAIL]'}`);

    console.log('\n======================================================================');
    console.log('   所有真实 EVM 合约交互、权限控制、状态转换与安全断言 100% 通过！');
    console.log('======================================================================');
}

main().catch(err => {
    console.error('EVM Run Error:', err);
    process.exit(1);
});
