// EtherCrowd DAPP 客户端交互逻辑 (Dual-Mode: 真实 Web3 / 离线模拟器)

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
            { id: 1, desc: "采购第1批磷酸铁锂电池电芯", amount: 10.0, votes: 18.0, executed: true },
            { id: 2, desc: "并网智能逆变器硬件调试与部署", amount: 8.0, votes: 14.5, executed: false }
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
            { id: 1, desc: "开模打样与PCB第一版试产", amount: 5.0, votes: 4.2, executed: false }
        ]
    },
    {
        id: 3,
        title: "开源零知识证明 (ZKP) 教学引擎",
        description: "为高校学生与金融研究员打造交互式 zk-SNARKs 可视化模拟教学系统，零门槛学习密码学黑科技。",
        goal: 8.0,
        totalPledged: 8.0,
        creator: "0x98A...55B2",
        endAt: Date.now() - 86400000 * 2,
        status: "ended",
        milestones: [
            { id: 1, desc: "编写全部 12 讲交互式教程源码", amount: 4.0, votes: 8.0, executed: true },
            { id: 2, desc: "部署上线公共开放实验室", amount: 4.0, votes: 8.0, executed: true }
        ]
    }
];

let state = {
    account: "0x7856...A3F9",
    balance: 85.50,
    campaigns: JSON.parse(localStorage.getItem('ethercrowd_campaigns')) || INITIAL_CAMPAIGNS,
    filter: "all"
};

function saveState() {
    localStorage.setItem('ethercrowd_campaigns', JSON.stringify(state.campaigns));
}

function updateWalletUI() {
    document.getElementById('wallet-addr').innerText = state.account;
    document.getElementById('wallet-bal').innerText = `${state.balance.toFixed(2)} ETH`;
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

        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <div>
                <div class="card-header">
                    <h3 class="card-title">${c.title}</h3>
                    <span class="badge-status ${isEnded ? 'status-ended' : 'status-active'}">
                        ${isEnded ? (isSuccess ? '众筹达标' : '众筹结束') : '进行中'}
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
                </div>
            </div>
            <div class="card-actions">
                ${!isEnded ? `
                    <button class="btn btn-primary btn-sm" onclick="handlePledge(${c.id})"><i class="fas fa-hand-holding-usd"></i> 支持项目</button>
                ` : (
                    !isSuccess ? `<button class="btn btn-danger btn-sm" onclick="handleRefund(${c.id})"><i class="fas fa-undo"></i> 申请退款</button>` : ''
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
    const amtStr = prompt("请输入您希望支持的金额 (ETH):", "2.0");
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
        saveState();
        updateWalletUI();
        renderCampaigns();
        alert(`[交易成功已打包上链]\n成功向项目【${c.title}】出资 ${amt} ETH！\n获得相应智能合约里程碑投票权。`);
    }
};

window.handleRefund = function(id) {
    const c = state.campaigns.find(item => item.id === id);
    if (!c) return;
    alert(`[智能合约自动清算]\n该项目未能在截止日前达到预定筹资门槛 (${c.goal} ETH)。\n您的出资款项已原路退回您的钱包地址！`);
    state.balance += 2.0; // 模拟退款
    updateWalletUI();
};

window.openMilestones = function(id) {
    const c = state.campaigns.find(item => item.id === id);
    if (!c) return;
    const modal = document.getElementById('milestone-modal');
    const content = document.getElementById('milestone-content');

    let html = `
        <h4 style="margin-bottom: 0.8rem; color: #a5b4fc;">项目：${c.title}</h4>
        <p style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 1.2rem;">
            以太坊智能合约锁定资金池: <strong>${c.totalPledged.toFixed(1)} ETH</strong>。<br>
            项目方提取款项必须提交具体里程碑用途，并获得出资人投票超过 50% 赞成后方可拨付。
        </p>
    `;

    if (!c.milestones || c.milestones.length === 0) {
        html += `<p style="color: #64748b;">暂无里程碑申请记录</p>`;
    } else {
        c.milestones.forEach(m => {
            const pass = m.votes * 2 > c.totalPledged;
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
                        <button class="btn btn-primary btn-sm" onclick="voteMilestone(${c.id}, ${m.id})"><i class="fas fa-check"></i> 投赞成票</button>
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
    m.votes += 2.0; // 模拟投赞成票
    saveState();
    openMilestones(cid);
    renderCampaigns();
    alert(`[投票交易已上链] 您已对该里程碑投下赞成票！`);
};

// 交互绑定
document.addEventListener('DOMContentLoaded', () => {
    updateWalletUI();
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
        alert(`[合约创建成功]\n新众筹项目【${title}】已成功部署至区块链！`);
    };

    // 连接 MetaMask
    document.getElementById('btn-connect').onclick = async () => {
        if (window.ethereum) {
            try {
                const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
                state.account = accounts[0];
                updateWalletUI();
                alert(`MetaMask 钱包连接成功！\n地址: ${accounts[0]}`);
            } catch (err) {
                console.error(err);
            }
        } else {
            alert(`当前环境未检测到 MetaMask 插件，已为您自动启用沙盒模拟钱包进行全功能体验。`);
        }
    };
});

