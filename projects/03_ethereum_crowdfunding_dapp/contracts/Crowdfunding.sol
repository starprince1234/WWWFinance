// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title DecentralizedCrowdfund
 * @dev 去中心化众筹智能合约 (Decentralized Crowdfunding with Milestone Governance)
 * 支持基于目标的众筹、未达标全额退款、以及防卷款跑路的“里程碑 DAO 投票拨款”机制
 */
contract DecentralizedCrowdfund {
    
    // --- 自定义错误 (Gas 优化) ---
    error InvalidGoal();
    error InvalidDuration();
    error CampaignNotActive();
    error CampaignEnded();
    error GoalNotReached();
    error GoalAlreadyReached();
    error AlreadyClaimed();
    error NothingToRefund();
    error TransferFailed();
    error NotCreator();
    error NotBacker();
    error AlreadyVoted();
    error MilestoneAlreadyExecuted();
    error InsufficientMilestoneVotes();
    error ExceedsAvailableBalance();

    // --- 数据结构 ---
    struct Milestone {
        string description;      // 里程碑资金用途描述
        uint256 amount;          // 申请提取的金额 (Wei)
        address payable recipient; // 接收资金的供应商/开发团队地址
        uint256 votesInFavor;    // 赞成票权重 (以出资 Wei 数为权重)
        bool executed;           // 是否已执行拨款
        mapping(address => bool) hasVoted; // 支持者投票记录
    }

    struct Campaign {
        address payable creator; // 项目发起人
        string title;            // 项目标题
        string description;      // 项目描述
        uint256 goal;            // 目标筹资金额 (Wei)
        uint256 totalPledged;    // 已筹集总金额 (Wei)
        uint256 currentBalance;  // 智能合约中当前存留金额
        uint32 startAt;          // 开始时间戳
        uint32 endAt;            // 截止时间戳
        bool claimed;            // 是否已完成全部筹资结算
        uint256 backerCount;     // 出资人数
        uint256 milestoneCount;  // 里程碑数量
    }

    // --- 状态变量 ---
    uint256 public campaignCount;
    mapping(uint256 => Campaign) public campaigns;
    mapping(uint256 => mapping(address => uint256)) public pledgedAmount;
    mapping(uint256 => mapping(uint256 => Milestone)) public campaignMilestones;

    // --- 事件定义 (前端监听与链上审计) ---
    event CampaignLaunched(uint256 indexed id, address indexed creator, uint256 goal, uint32 startAt, uint32 endAt, string title);
    event Pledged(uint256 indexed id, address indexed backer, uint256 amount);
    event Unpledged(uint256 indexed id, address indexed backer, uint256 amount);
    event Refunded(uint256 indexed id, address indexed backer, uint256 amount);
    event MilestoneProposed(uint256 indexed campaignId, uint256 indexed milestoneId, uint256 amount, string desc);
    event MilestoneVoted(uint256 indexed campaignId, uint256 indexed milestoneId, address indexed backer, uint256 weight);
    event MilestoneExecuted(uint256 indexed campaignId, uint256 indexed milestoneId, uint256 amount, address recipient);

    // --- 防重入锁 ---
    uint256 private _status;
    modifier nonReentrant() {
        require(_status != 2, "REENTRANCY_GUARD");
        _status = 2;
        _;
        _status = 1;
    }

    constructor() {
        _status = 1;
    }

    /**
     * @notice 发起新的众筹项目
     * @param _title 项目标题
     * @param _description 项目详细介绍
     * @param _goal 目标金额 (Wei)
     * @param _durationSeconds 众筹持续时长 (秒)
     */
    function launch(
        string calldata _title,
        string calldata _description,
        uint256 _goal,
        uint32 _durationSeconds
    ) external returns (uint256 campaignId) {
        if (_goal == 0) revert InvalidGoal();
        if (_durationSeconds < 60 || _durationSeconds > 90 days) revert InvalidDuration();

        campaignId = ++campaignCount;
        Campaign storage c = campaigns[campaignId];
        c.creator = payable(msg.sender);
        c.title = _title;
        c.description = _description;
        c.goal = _goal;
        c.startAt = uint32(block.timestamp);
        c.endAt = uint32(block.timestamp + _durationSeconds);
        c.currentBalance = 0;
        c.claimed = false;

        emit CampaignLaunched(campaignId, msg.sender, _goal, c.startAt, c.endAt, _title);
    }

    /**
     * @notice 支持者向指定项目出资 (Pledge ETH)
     */
    function pledge(uint256 _id) external payable nonReentrant {
        Campaign storage c = campaigns[_id];
        if (block.timestamp < c.startAt || block.timestamp > c.endAt) revert CampaignNotActive();
        if (msg.value == 0) revert InvalidGoal();

        if (pledgedAmount[_id][msg.sender] == 0) {
            c.backerCount++;
        }

        c.totalPledged += msg.value;
        c.currentBalance += msg.value;
        pledgedAmount[_id][msg.sender] += msg.value;

        emit Pledged(_id, msg.sender, msg.value);
    }

    /**
     * @notice 在众筹进行期间，支持者可撤回出资
     */
    function unpledge(uint256 _id, uint256 _amount) external nonReentrant {
        Campaign storage c = campaigns[_id];
        if (block.timestamp > c.endAt) revert CampaignEnded();
        if (pledgedAmount[_id][msg.sender] < _amount) revert ExceedsAvailableBalance();

        pledgedAmount[_id][msg.sender] -= _amount;
        c.totalPledged -= _amount;
        c.currentBalance -= _amount;

        if (pledgedAmount[_id][msg.sender] == 0) {
            c.backerCount--;
        }

        (bool success, ) = msg.sender.call{value: _amount}("");
        if (!success) revert TransferFailed();

        emit Unpledged(_id, msg.sender, _amount);
    }

    /**
     * @notice 众筹期满且失败（未达到目标金额），支持者全额退款
     */
    function refund(uint256 _id) external nonReentrant {
        Campaign storage c = campaigns[_id];
        if (block.timestamp <= c.endAt) revert CampaignNotActive();
        if (c.totalPledged >= c.goal) revert GoalAlreadyReached();

        uint256 bal = pledgedAmount[_id][msg.sender];
        if (bal == 0) revert NothingToRefund();

        pledgedAmount[_id][msg.sender] = 0;
        c.currentBalance -= bal;

        (bool success, ) = msg.sender.call{value: bal}("");
        if (!success) revert TransferFailed();

        emit Refunded(_id, msg.sender, bal);
    }

    // =========================================================================
    // 创新治理：里程碑资金拨付 DAO 机制 (防止项目方卷款跑路)
    // =========================================================================

    /**
     * @notice 发起人提交阶段性里程碑用款申请
     */
    function proposeMilestone(
        uint256 _id,
        string calldata _desc,
        uint256 _amount,
        address payable _recipient
    ) external returns (uint256 milestoneId) {
        Campaign storage c = campaigns[_id];
        if (msg.sender != c.creator) revert NotCreator();
        if (block.timestamp <= c.endAt) revert CampaignNotActive();
        if (c.totalPledged < c.goal) revert GoalNotReached();
        if (_amount > c.currentBalance) revert ExceedsAvailableBalance();

        milestoneId = ++c.milestoneCount;
        Milestone storage m = campaignMilestones[_id][milestoneId];
        m.description = _desc;
        m.amount = _amount;
        m.recipient = _recipient;
        m.votesInFavor = 0;
        m.executed = false;

        emit MilestoneProposed(_id, milestoneId, _amount, _desc);
    }

    /**
     * @notice 支持者对里程碑用款方案进行加权投票 (投票权重正比于出资金额)
     */
    function voteMilestone(uint256 _campaignId, uint256 _milestoneId) external {
        uint256 weight = pledgedAmount[_campaignId][msg.sender];
        if (weight == 0) revert NotBacker();

        Milestone storage m = campaignMilestones[_campaignId][_milestoneId];
        if (m.executed) revert MilestoneAlreadyExecuted();
        if (m.hasVoted[msg.sender]) revert AlreadyVoted();

        m.hasVoted[msg.sender] = true;
        m.votesInFavor += weight;

        emit MilestoneVoted(_campaignId, _milestoneId, msg.sender, weight);
    }

    /**
     * @notice 当赞成票超过总筹资额 50% 时，执行里程碑拨款
     */
    function executeMilestone(uint256 _campaignId, uint256 _milestoneId) external nonReentrant {
        Campaign storage c = campaigns[_campaignId];
        Milestone storage m = campaignMilestones[_campaignId][_milestoneId];

        if (m.executed) revert MilestoneAlreadyExecuted();
        if (m.votesInFavor * 2 <= c.totalPledged) revert InsufficientMilestoneVotes();
        if (m.amount > c.currentBalance) revert ExceedsAvailableBalance();

        m.executed = true;
        c.currentBalance -= m.amount;

        (bool success, ) = m.recipient.call{value: m.amount}("");
        if (!success) revert TransferFailed();

        emit MilestoneExecuted(_campaignId, _milestoneId, m.amount, m.recipient);
    }
}

