"""
Planning agent prompt constants
"""


class PlanningPrompt:
    """
    Planning agent prompt constants
    """
    
    SYSTEM_PROMPT = (
        "\\n{{sopPrompt}}\\n\\n===\\n# 环境变量\\n## 当前日期\\n{{date}}\\n\\n"
        "# 当前可用的文件名及描述\\n{{files}}\\n\\n# 约束\\n- 思考过程中，不要透露你的工具名称\\n"
        "- 调用planning生成任务列表，完成所有子任务就能完成任务。\\n- 以上是你需要遵循的指令。\\n\\n"
        "Let's think step by step (让我们一步步思考)\\n"
    )
    
    NEXT_STEP_PROMPT = (
        "工具planing的参数有\\n必填参数1：命令command\\n可选参数2：当前步状态step_status。\\n\\n"
        "必填参数1：命令command的枚举值有：\\n'mark_step', 'finish'\\n含义如下：\\n"
        "- 'finish' 根据已有的执行结果，可以判断出任务已经完成，输出任务结束，命令command为：finish\\n"
        "- 'mark_step' 标记当前任务规划的状态，设置当前任务的step_status\\n\\n"
        "当参数command值为mark_step时，需要可选参数2step_status，其中当前步状态step_status的枚举值如下：\\n"
        "- 没有开始'not_started'\\n- 进行中'in_progress' \\n- 已完成'completed'\\n\\n"
        "对应如下几种情况：\\n1.当前任务是否执行完成，完成以及失败都算执行完成，执行完成将入参step_status设置为`completed`\\n\\n"
        "一步一步分析完成任务，确定工具planing的入参，调用planing工具"
    )