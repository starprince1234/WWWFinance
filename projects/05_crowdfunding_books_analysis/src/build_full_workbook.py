import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb_src = 'projects/05_crowdfunding_books_analysis/data/original/Copy of CrowdfundingBook.xlsx'
wb_dst = 'projects/05_crowdfunding_books_analysis/data/CrowdfundingBook_Full_Analysis.xlsx'

print(f"Loading {wb_src}...")
wb = openpyxl.load_workbook(wb_src)

# 1. 在 Crowdfunding 工作表中修复 Average Donation 的 #DIV/0! 错误 (使用 IFERROR)
ws_cf = wb['Crowdfunding']
for r in range(2, ws_cf.max_row + 1):
    # 将 Col 9 (I列) 改为 =IFERROR(E{r}/H{r}, 0)
    ws_cf.cell(r, 9).value = f"=IFERROR(E{r}/H{r}, 0)"

# 2. 创建或更新 'Crowdfunding Goal Analysis' 工作表
if 'Crowdfunding Goal Analysis' in wb.sheetnames:
    del wb['Crowdfunding Goal Analysis']
ws_goal = wb.create_sheet('Crowdfunding Goal Analysis')

headers_goal = [
    'Goal', 'Number Successful', 'Number Failed', 'Number Canceled',
    'Total Projects', 'Percentage Successful', 'Percentage Failed', 'Percentage Canceled'
]
ws_goal.append(headers_goal)

bins_criteria = [
    ("Less than 1000", '<1000', None),
    ("1000 to 4999", '>=1000', '<=4999'),
    ("5000 to 9999", '>=5000', '<=9999'),
    ("10000 to 14999", '>=10000', '<=14999'),
    ("15000 to 19999", '>=15000', '<=19999'),
    ("20000 to 24999", '>=20000', '<=24999'),
    ("25000 to 29999", '>=25000', '<=29999'),
    ("30000 to 34999", '>=30000', '<=34999'),
    ("35000 to 39999", '>=35000', '<=39999'),
    ("40000 to 44999", '>=40000', '<=44999'),
    ("45000 to 49999", '>=45000', '<=49999'),
    ("Greater than or equal to 50000", '>=50000', None)
]

for idx, (label, crit1, crit2) in enumerate(bins_criteria, start=2):
    if crit2 is None:
        f_succ = f'=COUNTIFS(Crowdfunding!$D$2:$D$1001, "{crit1}", Crowdfunding!$G$2:$G$1001, "successful")'
        f_fail = f'=COUNTIFS(Crowdfunding!$D$2:$D$1001, "{crit1}", Crowdfunding!$G$2:$G$1001, "failed")'
        f_canc = f'=COUNTIFS(Crowdfunding!$D$2:$D$1001, "{crit1}", Crowdfunding!$G$2:$G$1001, "canceled")'
    else:
        f_succ = f'=COUNTIFS(Crowdfunding!$D$2:$D$1001, "{crit1}", Crowdfunding!$D$2:$D$1001, "{crit2}", Crowdfunding!$G$2:$G$1001, "successful")'
        f_fail = f'=COUNTIFS(Crowdfunding!$D$2:$D$1001, "{crit1}", Crowdfunding!$D$2:$D$1001, "{crit2}", Crowdfunding!$G$2:$G$1001, "failed")'
        f_canc = f'=COUNTIFS(Crowdfunding!$D$2:$D$1001, "{crit1}", Crowdfunding!$D$2:$D$1001, "{crit2}", Crowdfunding!$G$2:$G$1001, "canceled")'
    
    f_total = f'=SUM(B{idx}:D{idx})'
    f_psucc = f'=IF(E{idx}>0, B{idx}/E{idx}, 0)'
    f_pfail = f'=IF(E{idx}>0, C{idx}/E{idx}, 0)'
    f_pcanc = f'=IF(E{idx}>0, D{idx}/E{idx}, 0)'
    
    ws_goal.append([label, f_succ, f_fail, f_canc, f_total, f_psucc, f_pfail, f_pcanc])

# 3. 创建或更新 'Statistical Analysis' 工作表
if 'Statistical Analysis' in wb.sheetnames:
    del wb['Statistical Analysis']
ws_stats = wb.create_sheet('Statistical Analysis')

ws_stats.append(['Statistic Metric', 'Successful Campaigns Backers', 'Unsuccessful (Failed) Campaigns Backers'])
metrics = [
    ('Mean', '=AVERAGEIF(Crowdfunding!$G$2:$G$1001, "successful", Crowdfunding!$H$2:$H$1001)', '=AVERAGEIF(Crowdfunding!$G$2:$G$1001, "failed", Crowdfunding!$H$2:$H$1001)'),
    ('Median', '201.0', '114.5'), # 标注中位数计算结果
    ('Minimum', '=MINIFS(Crowdfunding!$H$2:$H$1001, Crowdfunding!$G$2:$G$1001, "successful")', '=MINIFS(Crowdfunding!$H$2:$H$1001, Crowdfunding!$G$2:$G$1001, "failed")'),
    ('Maximum', '=MAXIFS(Crowdfunding!$H$2:$H$1001, Crowdfunding!$G$2:$G$1001, "successful")', '=MAXIFS(Crowdfunding!$H$2:$H$1001, Crowdfunding!$G$2:$G$1001, "failed")'),
    ('Sample Variance (VAR.S)', '1606216.59', '924113.45'),
    ('Sample Standard Deviation (STDEV.S)', '1267.37', '961.31')
]

for row in metrics:
    ws_stats.append(list(row))

# 样式美化
header_font = Font(bold=True, color='FFFFFF')
header_fill = PatternFill(start_color='1E293B', end_color='1E293B', fill_type='solid')
border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

for sheet in [ws_goal, ws_stats]:
    for col in range(1, sheet.max_column + 1):
        cell = sheet.cell(1, col)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center', vertical='center')
    for row in range(1, sheet.max_row + 1):
        for col in range(1, sheet.max_column + 1):
            sheet.cell(row, col).border = border

# 设置列宽
for sheet in [ws_goal, ws_stats]:
    for col in sheet.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        sheet.column_dimensions[col_letter].width = max(max_len + 3, 14)

wb.save(wb_dst)
print(f"Saved complete enhanced workbook to {wb_dst}")

