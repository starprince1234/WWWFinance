import openpyxl
import pandas as pd
import numpy as np

wb_path = 'projects/05_crowdfunding_books_analysis/data/original/Copy of CrowdfundingBook.xlsx'
wb = openpyxl.load_workbook(wb_path, data_only=True)
ws = wb['Crowdfunding']

data = []
headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]
for r in range(2, ws.max_row + 1):
    row_vals = [ws.cell(r, c).value for c in range(1, ws.max_column + 1)]
    data.append(row_vals)

df = pd.DataFrame(data, columns=headers)
print(f"Loaded DataFrame: {df.shape[0]} rows, {df.shape[1]} columns")

# 1. Outcome counts
print("\n--- 1. 全局 Outcome 统计 ---")
print(df['outcome'].value_counts())

# 2. Parent Category vs Outcome
print("\n--- 2. Parent Category 交叉表 ---")
ct_cat = pd.crosstab(df['parent category '], df['outcome'], margins=True)
print(ct_cat)

# 3. Subcategory vs Outcome
print("\n--- 3. Sub-Category 交叉表 (Top 10 及 特殊项) ---")
ct_sub = pd.crosstab(df['sub-category'], df['outcome'], margins=True)
print(ct_sub.sort_values(by='All', ascending=False).head(15))
if 'world music' in ct_sub.index:
    print("\n[world music 专项查看]:")
    print(ct_sub.loc['world music'])

# 4. 12 Goal Ranges COUNTIFS
print("\n--- 4. 12 档目标金额区间统计 (Goal Analysis) ---")
bins = [
    ("Less than 1000", -np.inf, 999.99),
    ("1000 to 4999", 1000, 4999.99),
    ("5000 to 9999", 5000, 9999.99),
    ("10000 to 14999", 10000, 14999.99),
    ("15000 to 19999", 15000, 19999.99),
    ("20000 to 24999", 20000, 24999.99),
    ("25000 to 29999", 25000, 29999.99),
    ("30000 to 34999", 30000, 34999.99),
    ("35000 to 39999", 35000, 39999.99),
    ("40000 to 44999", 40000, 44999.99),
    ("45000 to 49999", 45000, 49999.99),
    ("Greater than or equal to 50000", 50000, np.inf)
]

goal_results = []
for label, low, high in bins:
    sub = df[(df['goal'] >= low) & (df['goal'] <= high)]
    n_succ = (sub['outcome'] == 'successful').sum()
    n_fail = (sub['outcome'] == 'failed').sum()
    n_canc = (sub['outcome'] == 'canceled').sum()
    total = n_succ + n_fail + n_canc
    p_succ = (n_succ / total * 100) if total > 0 else 0
    p_fail = (n_fail / total * 100) if total > 0 else 0
    p_canc = (n_canc / total * 100) if total > 0 else 0
    goal_results.append({
        'Goal': label,
        'Number Successful': n_succ,
        'Number Failed': n_fail,
        'Number Canceled': n_canc,
        'Total Projects': total,
        'Percentage Successful': round(p_succ, 2),
        'Percentage Failed': round(p_fail, 2),
        'Percentage Canceled': round(p_canc, 2)
    })

goal_df = pd.DataFrame(goal_results)
print(goal_df.to_string(index=False))

# 5. Statistical Analysis of Backers
print("\n--- 5. 支持者数量描述性统计 (Statistical Analysis) ---")
succ_backers = df[df['outcome'] == 'successful']['backers_count'].astype(float)
fail_backers = df[df['outcome'] == 'failed']['backers_count'].astype(float)

stats_summary = {
    'Metric': ['Mean', 'Median', 'Minimum', 'Maximum', 'Variance (Sample)', 'Std Dev (Sample)'],
    'Successful Campaigns': [
        round(succ_backers.mean(), 2),
        round(succ_backers.median(), 2),
        round(succ_backers.min(), 2),
        round(succ_backers.max(), 2),
        round(succ_backers.var(ddof=1), 2),
        round(succ_backers.std(ddof=1), 2)
    ],
    'Unsuccessful (Failed) Campaigns': [
        round(fail_backers.mean(), 2),
        round(fail_backers.median(), 2),
        round(fail_backers.min(), 2),
        round(fail_backers.max(), 2),
        round(fail_backers.var(ddof=1), 2),
        round(fail_backers.std(ddof=1), 2)
    ]
}
stats_df = pd.DataFrame(stats_summary)
print(stats_df.to_string(index=False))

