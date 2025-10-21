import astrbot.api.message_components as Comp
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Star, Context, register
from astrbot.core.utils.session_waiter import session_waiter, SessionFilter

@register("menu_plugin", "YourName", "一个带菜单的演示插件", "1.0.0")
class MyPlugins(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.sum_data = {}  # 用户数字累加数据字典

    @filter.command("菜单")
    async def show_menu(self, event: AstrMessageEvent):
        try:
            # 显示菜单提示
            await event.send(event.plain_result(
                "功能菜单：\n"
                "1. 成语接龙\n"
                "2. 数字累加\n"
                "3. 简单问答\n"
                "请输入功能编号进入，或者输入“退出”结束。"
            ))

            @session_waiter(timeout=60, record_history_chains=False)
            async def menu_session(event: AstrMessageEvent):
                choice = event.message_str.strip()

                if choice == "退出":
                    await event.send(event.plain_result("已退出菜单~"))
                    return

                if choice == "1":
                    await event.send(event.plain_result("进入成语接龙模式，输入成语，输入“退出”可结束~"))
                    await self.start_idiom_game(event, session_filter=SessionFilter())
                elif choice == "2":
                    await event.send(event.plain_result("进入数字累加模式，输入数字，输入“退出”可结束~"))
                    await self.start_number_sum(event, session_filter=SessionFilter())
                elif choice == "3":
                    await event.send(event.plain_result("进入简单问答模式，输入问题，输入“退出”可结束~"))
                    await self.start_simple_qa(event, session_filter=SessionFilter())
                else:
                    await event.send(event.plain_result("无效选择，请输入 1, 2 或 3，或输入“退出”结束。"))

            await menu_session(event)

        except Exception as e:
            await event.send(event.plain_result("发生错误：" + str(e)))

    # 成语接龙功能
    @session_waiter(timeout=60, record_history_chains=False)
    async def start_idiom_game(self, event: AstrMessageEvent):
        idiom = event.message_str.strip()

        if idiom == "退出":
            await event.send(event.plain_result("成语接龙已结束~"))
            return

        if len(idiom) != 4:
            await event.send(event.plain_result("成语必须是四个字哦~"))
        else:
            # 这里只是示例，实际可接数据库/接口判断
            await event.send(event.plain_result("接龙示例：先见之明"))

    # 数字累加功能
    @session_waiter(timeout=60, record_history_chains=False)
    async def start_number_sum(self, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        if user_id not in self.sum_data:
            self.sum_data[user_id] = 0

        msg = event.message_str.strip()

        if msg == "退出":
            await event.send(event.plain_result(f"数字累加结束，总和为：{self.sum_data[user_id]}"))
            self.sum_data[user_id] = 0
            return

        if msg.isdigit():
            self.sum_data[user_id] += int(msg)
            await event.send(event.plain_result(f"当前总和：{self.sum_data[user_id]}"))
        else:
            await event.send(event.plain_result("请输入数字或“退出”结束。"))

    # 简单问答功能
    @session_waiter(timeout=60, record_history_chains=False)
    async def start_simple_qa(self, event: AstrMessageEvent):
        question = event.message_str.strip()

        if question == "退出":
            await event.send(event.plain_result("问答会话已结束~"))
            return

        # 简单演示回答
        await event.send(event.plain_result(f"你问的是：{question}\n示例回答：这是一个测试回答~"))
