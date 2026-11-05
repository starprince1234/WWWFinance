# 众筹书籍实证分析数据字典 (Data Dictionary)

| 字段名称 (Variable) | 物理类型 | 业务含义与取值说明 |
| :--- | :---: | :--- |
| `project_id` | String | 项目全局唯一编码 (如 `BOOK_0001`) |
| `title` | String | 众筹图书标题 |
| `genre` | String | 图书题材类别 (`Sci-Fi/Fantasy`, `Academic/Tech`, `Art/Comics`, `Fiction`, `Children`) |
| `goal_cny` | Float | 发起人设定的目标筹资金额 (元) |
| `pledged_cny` | Float | 众筹结束时实际筹得总金额 (元) |
| `backers_count` | Integer | 参与出资的支持者总人数 |
| `duration_days` | Integer | 众筹在平台展示开放的筹集天数 (天) |
| `reward_tiers_count` | Integer | 发起人配置的不同回报档位数量 (档) |
| `pitch_word_count` | Integer | 众筹详情页主文案总字数 (字) |
| `sentiment_score` | Float | NLP 情感分析极性得分 ([-1.0, 1.0]，越接近 1 代表积极/热忱情绪越强) |
| `has_video` | Integer | 是否配备项目宣传视频 (1: 有, 0: 无) |
| `creator_past_projects` | Integer | 发起人过往成功发布众筹的项目数量 (声誉资产代理变量) |
| `state` | String | 众筹最终状态 (`successful` 或 `failed`) |
| `success` | Integer | 虚拟变量 (1: 达标成功, 0: 未达标失败) |
| `funding_ratio` | Float | 最终筹资完成比例 ($Pledged / Goal$) |

