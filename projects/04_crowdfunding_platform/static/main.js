// 创益众筹平台前端交互逻辑 (CloudFund Client SPA)

const API_BASE = "/api";

let appState = {
    user: null,
    token: localStorage.getItem('cf_token') || null,
    campaigns: [],
    currentCategory: 'ALL',
    currentStatus: 'ACTIVE',
    authMode: 'LOGIN' // 'LOGIN' or 'REGISTER'
};

async function apiRequest(endpoint, method = 'GET', body = null) {
    const headers = { 'Content-Type': 'application/json' };
    if (appState.token) {
        headers['Authorization'] = `Bearer ${appState.token}`;
    }
    const options = { method, headers };
    if (body) {
        options.body = JSON.stringify(body);
    }
    try {
        const resp = await fetch(`${API_BASE}${endpoint}`, options);
        return await resp.json();
    } catch (err) {
        console.error("API Error:", err);
        return { success: false, error: "网络请求异常，请检查后端服务是否启动" };
    }
}

async function loadUserProfile() {
    if (!appState.token) {
        renderAuthUI();
        return;
    }
    const res = await apiRequest('/user/profile');
    if (res.success) {
        appState.user = res.user;
    } else {
        appState.token = null;
        localStorage.removeItem('cf_token');
        appState.user = null;
    }
    renderAuthUI();
}

function renderAuthUI() {
    const authBtn = document.getElementById('auth-buttons');
    const userBadge = document.getElementById('user-info-badge');

    if (appState.user) {
        authBtn.style.display = 'none';
        userBadge.style.display = 'flex';
        document.getElementById('user-display-name').innerText = appState.user.username;
        document.getElementById('avatar-initial').innerText = appState.user.username.charAt(0).toUpperCase();
        document.getElementById('user-balance-val').innerText = appState.user.balance.toFixed(2);
    } else {
        authBtn.style.display = 'block';
        userBadge.style.display = 'none';
    }
}

async function loadCampaigns() {
    const query = new URLSearchParams({
        category: appState.currentCategory,
        status: appState.currentStatus
    });
    const res = await apiRequest(`/campaigns?${query.toString()}`);
    if (res.success) {
        appState.campaigns = res.data;
        renderCampaigns();
    }
}

function renderCampaigns() {
    const container = document.getElementById('campaigns-container');
    container.innerHTML = '';

    let totalFunded = 0;
    appState.campaigns.forEach(c => {
        totalFunded += c.current_amount;
        const percent = Math.min(100, Math.round((c.current_amount / c.goal_amount) * 100));

        let tagClass = "tag-tech";
        let tagText = "科技";
        if (c.category === "PUBLISHING") { tagClass = "tag-publishing"; tagText = "出版"; }
        if (c.category === "CREATIVE") { tagClass = "tag-creative"; tagText = "创意"; }

        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <div>
                <div class="card-top">
                    <span class="card-tag ${tagClass}">${tagText}</span>
                    <span style="font-size: 0.8rem; font-weight: 600; color: ${c.status === 'ACTIVE' ? '#2563eb' : (c.status === 'SUCCEEDED' ? '#10b981' : '#ef4444')}">
                        ${c.status === 'ACTIVE' ? '筹集中' : (c.status === 'SUCCEEDED' ? '已达成' : '已流标')}
                    </span>
                </div>
                <h3 class="card-title">${c.title}</h3>
                <p class="card-desc">${c.description}</p>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: ${percent}%;"></div>
                </div>
                <div class="progress-numbers">
                    <span>已筹: <strong>¥${c.current_amount.toFixed(0)}</strong> (${percent}%)</span>
                    <span>目标: ¥${c.goal_amount.toFixed(0)}</span>
                </div>
            </div>
            <div class="card-footer">
                <div class="creator-info">
                    <i class="fas fa-user-circle"></i> ${c.creator_name}
                </div>
                <button class="btn btn-outline btn-sm" onclick="openCampaignDetail(${c.id})">查看详情 / 支持</button>
            </div>
        `;
        container.appendChild(card);
    });

    document.getElementById('stat-total-campaigns').innerText = appState.campaigns.length;
    document.getElementById('stat-total-funded').innerText = totalFunded.toLocaleString();
}

window.openCampaignDetail = async function(id) {
    const res = await apiRequest(`/campaigns/${id}`);
    if (!res.success) {
        alert("获取项目详情失败");
        return;
    }
    const c = res.data;
    const modal = document.getElementById('detail-modal');
    document.getElementById('detail-title').innerText = c.title;

    const percent = Math.min(100, Math.round((c.current_amount / c.goal_amount) * 100));
    let tiersHtml = '';
    if (c.tiers && c.tiers.length > 0) {
        c.tiers.forEach(t => {
            tiersHtml += `
                <div style="border: 1px solid #e2e8f0; padding: 1rem; border-radius: 8px; margin-bottom: 0.8rem; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 700; color: #0f172a;">${t.title} - <span style="color: #2563eb;">¥${t.price}</span></div>
                        <div style="font-size: 0.85rem; color: #64748b; margin-top: 0.2rem;">${t.description}</div>
                        <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.3rem;">已有 ${t.current_backers} 位支持者</div>
                    </div>
                    <button class="btn btn-primary" onclick="handlePledgeTier(${c.id}, ${t.id}, ${t.price})">立即支持</button>
                </div>
            `;
        });
    }

    document.getElementById('detail-body').innerHTML = `
        <div style="margin-bottom: 1.2rem;">
            <p style="color: #475569; line-height: 1.6; margin-bottom: 1rem;">${c.description}</p>
            <div style="display: flex; gap: 2rem; background: #f8fafc; padding: 1rem; border-radius: 8px;">
                <div><strong>目标金额:</strong> ¥${c.goal_amount}</div>
                <div><strong>已筹集:</strong> ¥${c.current_amount} (${percent}%)</div>
                <div><strong>支持人数:</strong> ${c.backer_count} 人</div>
                <div><strong>截止日期:</strong> ${c.end_time}</div>
            </div>
        </div>
        <h4 style="margin-bottom: 0.8rem;">选择支持档位</h4>
        ${tiersHtml || '<p style="color: #94a3b8;">暂未配置标准档位</p>'}
        <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center;">
            <div style="font-size: 0.85rem; color: #94a3b8;">众筹到期后，系统将按 All-or-Nothing 规则自动执行清算或原路全额退款。</div>
            ${c.status === 'ACTIVE' ? `
                <button class="btn btn-secondary btn-sm" onclick="handleManualSettle(${c.id})"><i class="fas fa-balance-scale"></i> 触发到期清算</button>
            ` : ''}
        </div>
    `;

    modal.classList.add('active');
};

window.handlePledgeTier = async function(campaignId, tierId, price) {
    if (!appState.user) {
        alert("请先登录创益众筹账户");
        document.getElementById('auth-modal').classList.add('active');
        return;
    }
    if (confirm(`确认出资 ¥${price} 支持该项目？资金将通过平台账户安全托管。`)) {
        const res = await apiRequest(`/campaigns/${campaignId}/pledge`, 'POST', {
            amount: price,
            tier_id: tierId
        });
        if (res.success) {
            alert("出资成功！您的支持已记录上链并进入履约监管流程。");
            document.getElementById('detail-modal').classList.remove('active');
            await loadUserProfile();
            await loadCampaigns();
        } else {
            alert(`出资失败: ${res.error}`);
        }
    }
};

window.handleManualSettle = async function(campaignId) {
    if (confirm("是否立即结算该项目？\n达标将向发起人放款并扣除 5% 服务费；未达标将对所有出资人原路批量退款。")) {
        const res = await apiRequest(`/campaigns/${campaignId}/settle`, 'POST', {});
        if (res.success) {
            if (res.status === 'SUCCEEDED') {
                alert(`[清算完成: 众筹成功]\n已筹金额 ¥${res.current_amount}，平台扣除 5% 佣金 (¥${res.fee})，已将净款 ¥${res.payout} 汇入发起人账户！`);
            } else {
                alert(`[清算完成: 众筹未达标]\n已自动为全部 ${res.refunded_count} 笔订单办理原路全额退款，总退款金额 ¥${res.total_refunded}！`);
            }
            document.getElementById('detail-modal').classList.remove('active');
            await loadUserProfile();
            await loadCampaigns();
        } else {
            alert(`清算失败: ${res.error}`);
        }
    }
};

// 事件绑定
document.addEventListener('DOMContentLoaded', () => {
    loadUserProfile();
    loadCampaigns();

    // 模态弹窗开关
    document.getElementById('btn-open-login').onclick = () => {
        appState.authMode = 'LOGIN';
        document.getElementById('auth-title').innerText = "登录创益账户";
        document.getElementById('btn-auth-submit').innerText = "确认登录";
        document.getElementById('btn-toggle-auth-mode').innerText = "切换到快速注册";
        document.getElementById('auth-modal').classList.add('active');
    };
    document.getElementById('btn-close-auth').onclick = () => document.getElementById('auth-modal').classList.remove('active');
    document.getElementById('btn-toggle-auth-mode').onclick = () => {
        if (appState.authMode === 'LOGIN') {
            appState.authMode = 'REGISTER';
            document.getElementById('auth-title').innerText = "注册新账户";
            document.getElementById('btn-auth-submit').innerText = "立即注册";
            document.getElementById('btn-toggle-auth-mode').innerText = "返回已有账号登录";
        } else {
            appState.authMode = 'LOGIN';
            document.getElementById('auth-title').innerText = "登录创益账户";
            document.getElementById('btn-auth-submit').innerText = "确认登录";
            document.getElementById('btn-toggle-auth-mode').innerText = "切换到快速注册";
        }
    };

    document.getElementById('btn-logout').onclick = () => {
        appState.token = null;
        appState.user = null;
        localStorage.removeItem('cf_token');
        renderAuthUI();
        alert("已成功退出登录");
    };

    document.getElementById('btn-open-create').onclick = () => {
        if (!appState.user) {
            alert("发起众筹前请先登录账户");
            document.getElementById('auth-modal').classList.add('active');
            return;
        }
        document.getElementById('create-modal').classList.add('active');
    };
    document.getElementById('btn-close-create').onclick = () => document.getElementById('create-modal').classList.remove('active');
    document.getElementById('btn-cancel-create').onclick = () => document.getElementById('create-modal').classList.remove('active');
    document.getElementById('btn-close-detail').onclick = () => document.getElementById('detail-modal').classList.remove('active');

    // 登录/注册表单
    document.getElementById('form-auth').onsubmit = async (e) => {
        e.preventDefault();
        const u = document.getElementById('auth-username').value.trim();
        const p = document.getElementById('auth-password').value.trim();
        if (appState.authMode === 'LOGIN') {
            const res = await apiRequest('/auth/login', 'POST', { username: u, password: p });
            if (res.success) {
                appState.token = res.token;
                appState.user = res.user;
                localStorage.setItem('cf_token', res.token);
                document.getElementById('auth-modal').classList.remove('active');
                renderAuthUI();
                alert(`欢迎回来，${res.user.username}！`);
            } else {
                alert(res.error);
            }
        } else {
            const res = await apiRequest('/auth/register', 'POST', { username: u, password: p, role: 'USER' });
            if (res.success) {
                alert("注册成功！已为您自动登录。");
                const loginRes = await apiRequest('/auth/login', 'POST', { username: u, password: p });
                appState.token = loginRes.token;
                appState.user = loginRes.user;
                localStorage.setItem('cf_token', loginRes.token);
                document.getElementById('auth-modal').classList.remove('active');
                renderAuthUI();
            } else {
                alert(res.error);
            }
        }
    };

    // 发起众筹表单
    document.getElementById('form-create').onsubmit = async (e) => {
        e.preventDefault();
        const title = document.getElementById('create-title').value.trim();
        const category = document.getElementById('create-category').value;
        const goal = parseFloat(document.getElementById('create-goal').value);
        const days = parseInt(document.getElementById('create-days').value);
        const desc = document.getElementById('create-desc').value.trim();

        const res = await apiRequest('/campaigns', 'POST', {
            title,
            category,
            goal_amount: goal,
            duration_days: days,
            description: desc,
            tiers: [
                { title: "早期支持礼包", description: "项目专属限量定制版", price: Math.round(goal * 0.05), backer_limit: 100 },
                { title: "标准全套回报", description: "全套量产成品顺丰包邮", price: Math.round(goal * 0.1), backer_limit: 50 }
            ]
        });

        if (res.success) {
            alert(`众筹项目【${title}】发布成功！已正式上线接受全国公众出资。`);
            document.getElementById('create-modal').classList.remove('active');
            await loadCampaigns();
        } else {
            alert(`发起失败: ${res.error}`);
        }
    };

    // 分类筛选
    document.querySelectorAll('.cat-btn').forEach(btn => {
        btn.onclick = () => {
            document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            appState.currentCategory = btn.dataset.cat;
            loadCampaigns();
        };
    });

    document.getElementById('select-status').onchange = (e) => {
        appState.currentStatus = e.target.value;
        loadCampaigns();
    };
});

