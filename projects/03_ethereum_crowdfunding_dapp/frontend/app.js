// EtherCrowd DAPP 客户端交互逻辑 (明确标注: 沙盒演示模式 vs 真实 Web3 模式)

const INITIAL_CAMPAIGNS = [
    {
        id: 1,
        title: "去中心化绿色能源微电网",
        description: "基于以太坊智能合约调度社区分布式光伏与储能电池，实现点对点清洁能源众筹与绿电消纳结算。",
        goal: 20.0,
        totalPledged: 24.5,
        creator: "0x71C...9382",
        endAt: Date.now() + 86400000 * 5,
        status: "active",
        milestones: [
            { id: 1, desc: "采购第1批磷酸铁锂电池电芯", amount: 10.0, votes: 18.0, executed: true, voters: [] },
            { id: 2, desc: "并网智能逆变器硬件调试与部署", amount: 8.0, votes: 14.5, executed: false, voters: [] }
        ]
    },
    {
        id: 2,
        title: "Web3 隐私硬件冷钱包",
        description: "开源硬件架构，支持 EAL6+ 安全芯片与离线二维码空气隔离 (Air-gapped) 签名，抵抗物理探测攻击。",
        goal: 15.0,
        totalPledged: 9.8,
        creator: "0x4Fa...11D3",
        endAt: Date.now() + 86400000 * 12,
        status: "active",
        milestones: [
            { id: 1, desc: "开模打样与PCB第一版试产", amount: 5.0, votes: 4.2, executed: false, voters: [] }
        ]
    },
    {
        id: 3,
        title: "开源零知识证明 (ZKP) 教学引擎",
        description: "为高校学生与金融研究员打造交互式 zk-SNARKs 可视化模拟教学系统，零门槛学习密码学黑科技。",
        goal: 8.0,
        totalPledged: 4.0, // 未达标项目
        creator: "0x98A...55B2",
        endAt: Date.now() - 86400000 * 2, // 已到期流标
        status: "ended",
        milestones: [
            { id: 1, desc: "编写全部 12 讲交互式教程源码", amount: 4.0, votes: 4.0, executed: false, voters: [] }
        ]
    }
];

let state = {
    account: "0x7856...A3F9 (本地测试地址)",
    balance: 50.00,
    isWeb3Connected: false,
    userContributions: JSON.parse(localStorage.getItem('ethercrowd_user_pledges')) || { 3: 2.0 }, // 默认记录在项目3出资过2 ETH
    campaigns: JSON.parse(localStorage.getItem('ethercrowd_campaigns')) || INITIAL_CAMPAIGNS,
    filter: "all"
};

function saveState() {
    localStorage.setItem('ethercrowd_campaigns', JSON.stringify(state.campaigns));
    localStorage.setItem('ethercrowd_user_pledges', JSON.stringify(state.userContributions));
}

function updateWalletUI() {
    document.getElementById('wallet-addr').innerText = state.account;
    document.getElementById('wallet-bal').innerText = `${state.balance.toFixed(2)} ETH`;
}

function updateModeBanner() {
    const banner = document.getElementById('mode-text');
    if (banner) {
        if (state.isWeb3Connected) {
            banner.innerHTML = `<span style="color: #10b981;">● 真实 Web3 模式 (已连接 MetaMask: ${state.account})</span>`;
        } else {
            banner.innerHTML = `<span style="color: #f59e0b;">● 离线沙盒演示模式 (未连接真实 EVM 节点，状态变更仅保存在浏览器本地)</span>`;
        }
    }
}

function renderCampaigns() {
    const listEl = document.getElementById('campaign-list');
    listEl.innerHTML = '';

    const filtered = state.campaigns.filter(c => {
        if (state.filter === "active") return c.status === "active";
        if (state.filter === "ended") return c.status === "ended";
        return true;
    });

    filtered.forEach(c => {
        const percent = Math.min(100, Math.round((c.totalPledged / c.goal) * 100));
        const isEnded = c.status === "ended" || Date.now() > c.endAt;
        const isSuccess = c.totalPledged >= c.goal;
        const myPledged = state.userContributions[c.id] || 0;

        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <div>
                <div class="card-header">
                    <h3 class="card-title">${c.title}</h3>
                    <span class="badge-status ${isEnded ? (isSuccess ? 'status-active' : 'status-ended') : 'status-active'}">
                        ${isEnded ? (isSuccess ? '众筹达标' : '众筹流标') : '进行中'}
                    </span>
                </div>
                <p class="card-desc">${c.description}</p>
                <div class="progress-box">
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width: ${percent}%;"></div>
                    </div>
                    <div class="progress-info">
                        <span>已筹集: <strong>${c.totalPledged.toFixed(1)} ETH</strong> (${percent}%)</span>
                        <span>目标: ${c.goal.toFixed(1)} ETH</span>
                    </div>
                    ${myPledged > 0 ? `<div style="font-size:0.8rem; color:#38bdf8; margin-top:0.3rem;">我的出资: ${myPledged.toFixed(1)} ETH</div>` : ''}
                </div>
            </div>
            <div class="card-actions">
                ${!isEnded ? `
                    <button class="btn btn-primary btn-sm" onclick="handlePledge(${c.id})"><i class="fas fa-hand-holding-usd"></i> 支持项目</button>
                ` : (
                    !isSuccess ? `<button class="btn btn-danger btn-sm" onclick="handleRefund(${c.id})"><i class="fas fa-undo"></i> 申请全额退款</button>` : ''
                )}
                <button class="btn btn-outline btn-sm" onclick="openMilestones(${c.id})"><i class="fas fa-list-check"></i> 里程碑治理 (${c.milestones ? c.milestones.length : 0})</button>
            </div>
        `;
        listEl.appendChild(card);
    });

    // 更新全局统计
    document.getElementById('stat-total-campaigns').innerText = state.campaigns.length;
    const totalEth = state.campaigns.reduce((acc, cur) => acc + cur.totalPledged, 0);
    document.getElementById('stat-total-eth').innerText = `${totalEth.toFixed(1)} ETH`;
}

window.handlePledge = function(id) {
    const amtStr = prompt("请输入您希望出资的金额 (ETH):", "2.0");
    if (!amtStr) return;
    const amt = parseFloat(amtStr);
    if (isNaN(amt) || amt <= 0) {
        alert("请输入合法的金额");
        return;
    }
    if (amt > state.balance) {
        alert("钱包余额不足！");
        return;
    }

    state.balance -= amt;
    const c = state.campaigns.find(item => item.id === id);
    if (c) {
        c.totalPledged += amt;
        state.userContributions[id] = (state.userContributions[id] || 0) + amt;
        saveState();
        updateWalletUI();
        renderCampaigns();
        alert(`[离线沙盒演示]\n成功向项目【${c.title}】出资 ${amt} ETH！\n（注意：当前为前端离线沙盒模式，变更已写入浏览器本地存储，未发起真实区块链交易）`);
    }
};

window.handleRefund = function(id) {
    const c = state.campaigns.find(item => item.id === id);
    if (!c) return;

    const myPledged = state.userContributions[id] || 0;
    if (myPledged <= 0) {
        alert(`[退款拦截] 您在项目【${c.title}】中当前出资记录为 0 ETH，无款项可退。`);
        return;
    }

    state.balance += myPledged;
    state.userContributions[id] = 0;
    saveState();
    updateWalletUI();
    renderCampaigns();
    alert(`[离线沙盒退款成功]\n项目【${c.title}】流标触发 All-or-Nothing 退款！\n您此前实际出资的 ${myPledged.toFixed(1)} ETH 已原路全额返还至您的沙盒钱包余额。`);
};

window.openMilestones = function(id) {
    const c = state.campaigns.find(item => item.id === id);
    if (!c) return;
    const modal = document.getElementById('milestone-modal');
    const content = document.getElementById('milestone-content');

    let html = `
        <h4 style="margin-bottom: 0.8rem; color: #a5b4fc;">项目：${c.title}</h4>
        <p style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 1.2rem;">
            锁定资金池: <strong>${c.totalPledged.toFixed(1)} ETH</strong>。<br>
            规则：项目方提款必须提交里程碑用途，并获得出资人投票超过 50% 赞成后方可拨付。
        </p>
    `;

    if (!c.milestones || c.milestones.length === 0) {
        html += `<p style="color: #64748b;">暂无里程碑申请记录</p>`;
    } else {
        c.milestones.forEach(m => {
            const pass = m.votes * 2 > c.totalPledged;
            const hasVoted = m.voters && m.voters.includes(state.account);
            html += `
                <div style="background: rgba(0,0,0,0.25); border: 1px solid rgba(255,255,255,0.08); padding: 1rem; border-radius: 8px; margin-bottom: 0.8rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.4rem;">
                        <strong>阶段 #${m.id}：${m.desc}</strong>
                        <span style="color: #38bdf8; font-weight: 600;">申请金额: ${m.amount} ETH</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 0.6rem;">
                        当前赞成权重: ${m.votes} ETH / ${c.totalPledged} ETH (${Math.round(m.votes/c.totalPledged*100)}%)
                        · 状态: <span style="color: ${m.executed ? '#10b981' : (pass ? '#f59e0b' : '#94a3b8')}">${m.executed ? '已执行拨款' : (pass ? '票数达标待拨' : '投票进行中')}</span>
                    </div>
                    ${!m.executed ? `
                        <button class="btn ${hasVoted ? 'btn-outline' : 'btn-primary'} btn-sm" onclick="voteMilestone(${c.id}, ${m.id})">
                            <i class="fas fa-check"></i> ${hasVoted ? '已投赞成票' : '投赞成票'}
                        </button>
                    ` : ''}
                </div>
            `;
        });
    }

    content.innerHTML = html;
    modal.classList.add('active');
};

window.voteMilestone = function(cid, mid) {
    const c = state.campaigns.find(item => item.id === cid);
    if (!c) return;
    const m = c.milestones.find(item => item.id === mid);
    if (!m) return;

    m.voters = m.voters || [];
    if (m.voters.includes(state.account)) {
        alert(`[安全拦截] 您（${state.account}）已对该里程碑投过票，智能合约已拦截重复投票！`);
        return;
    }

    const voteWeight = state.userContributions[cid] || 2.0;
    m.votes += voteWeight;
    m.voters.push(state.account);
    saveState();
    openMilestones(cid);
    renderCampaigns();
    alert(`[离线沙盒投票成功]\n已按您的出资权重 (${voteWeight.toFixed(1)} ETH) 计入赞成票！\n（注意：当前为前端离线演示）`);
};

// 交互绑定
document.addEventListener('DOMContentLoaded', () => {
    updateWalletUI();
    updateModeBanner();
    renderCampaigns();

    // 筛选标签切换
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            state.filter = tab.dataset.filter;
            renderCampaigns();
        });
    });

    // 模态弹窗控制
    const launchModal = document.getElementById('launch-modal');
    document.getElementById('btn-launch-modal').onclick = () => launchModal.classList.add('active');
    document.getElementById('btn-close-modal').onclick = () => launchModal.classList.remove('active');
    document.getElementById('btn-cancel-launch').onclick = () => launchModal.classList.remove('active');

    document.getElementById('btn-close-milestone').onclick = () => {
        document.getElementById('milestone-modal').classList.remove('active');
    };

    // 表单提交发起众筹
    document.getElementById('form-launch').onsubmit = (e) => {
        e.preventDefault();
        const title = document.getElementById('input-title').value;
        const goal = parseFloat(document.getElementById('input-goal').value);
        const days = parseInt(document.getElementById('input-days').value);
        const desc = document.getElementById('input-desc').value;

        const newCamp = {
            id: Date.now(),
            title,
            description: desc,
            goal,
            totalPledged: 0,
            creator: state.account,
            endAt: Date.now() + days * 86400000,
            status: "active",
            milestones: []
        };

        state.campaigns.unshift(newCamp);
        saveState();
        renderCampaigns();
        launchModal.classList.remove('active');
        alert(`[离线沙盒项目已创建]\n新众筹项目【${title}】已加入列表。\n（注意：当前为前端离线沙盒模式，未发起真实区块链交易）`);
    };

    // 连接 MetaMask
    document.getElementById('btn-connect').onclick = async () => {
        if (window.ethereum) {
            try {
                const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
                state.account = accounts[0];
                state.isWeb3Connected = true;
                updateWalletUI();
                updateModeBanner();
                alert(`MetaMask 钱包连接成功！\n当前连接地址: ${accounts[0]}\n提示: 真实链交易需要本地运行 Ganache 节点 (ChainId 1337) 并部署合约。`);
            } catch (err) {
                console.error(err);
                alert(`MetaMask 连接取消或发生错误: ${err.message}`);
            }
        } else {
            alert(`未检测到 MetaMask 插件。当前保持【离线沙盒演示模式】，所有功能可在前端沙盒中安全体验。`);
        }
    };
});
