import astrbot.api.message_components as Comp
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Star, Context, register
from astrbot.core.utils.session_waiter import session_waiter, SessionController, SessionFilter

# 自定义过滤器：会话只对某个用户生效
class SingleUserFilter(SessionFilter):
    def __init__(self, user_id: str):
        self.user_id = user_id

    def filter(self, event: AstrMessageEvent) -> str:
        """群聊返回 群ID:用户ID；私聊返回 用户ID"""
        try:
            gid = event.get_group_id()
        except AttributeError:
            gid = None
        if gid:
            return f"{gid}:{self.user_id}"
        return self.user_id


@register("menu_plugin", "YourName", "一个带菜单的演示插件", "1.0.0")
class MyPlugins(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.sum_data = {}  # 保存数字累加的结果

    def show_menu_text(self) -> str:
        return (
            "功能菜单：\n"
            "1. 成语接龙\n"
            "2. 数字累加\n"
            "3. 简单问答\n"
            "请输入功能编号进入，或输入“退出”结束"
        )

    # 菜单会话（入口）
    @filter.command("菜单")
    @session_waiter(timeout=60, record_history_chains=False)
    async def menu_waiter(self, controller: SessionController, event: AstrMessageEvent):
        msg = event.message_str.strip()

        # 第一次进入会话时显示菜单
        if controller.session_round == 1:
            await event.send(event.plain_result(self.show_menu_text()))
            controller.keep(timeout=60, reset_timeout=True)
            return

        # 退出菜单
        if msg == "退出":
            await event.send(event.plain_result("已退出菜单~"))
            controller.stop()
            return

        # 根据选择进入功能会话
        if msg == "1":
            await event.send(event.plain_result("进入成语接龙模式~ 输入成语，输入“退出”可结束"))
            await self.start_idiom_game(event, session_filter=SingleUserFilter(event.get_sender_id()))
        elif msg == "2":
            await event.send(event.plain_result("进入数字累加模式~ 输入数字，输入“退出”可结束"))
            await self.start_number_sum(event, session_filter=SingleUserFilter(event.get_sender_id()))
        elif msg == "3":
            await event.send(event.plain_result("进入简单问答模式~ 输入问题，输入“退出”可结束"))
            await self.start_simple_qa(event, session_filter=SingleUserFilter(event.get_sender_id()))
        else:
            await event.send(event.plain_result("无效选择，请输入 1 / 2 / 3，或“退出”"))
            controller.keep(timeout=60, reset_timeout=True)

    # 成语接龙功能
    @session_waiter(timeout=60, record_history_chains=False)
    async def start_idiom_game(self, controller: SessionController, event: AstrMessageEvent):
        idiom = event.message_str.strip()
        if idiom == "退出":
            await event.send(event.plain_result("成语接龙已结束~"))
            controller.stop()
            return
        if len(idiom) != 4:
            await event.send(event.plain_result("成语必须是四个字哦~"))
        else:
            await event.send(event.plain_result(f"你输入的成语：{idiom}\n接龙示例：先见之明"))
        controller.keep(timeout=60, reset_timeout=True)

    # 数字累加功能
    @session_waiter(timeout=60, record_history_chains=False)
    async def start_number_sum(self, controller: SessionController, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        if user_id not in self.sum_data:
            self.sum_data[user_id] = 0

        msg = event.message_str.strip()
        if msg == "退出":
            await event.send(
                event.plain_result(f"数字累加结束，总和为：{self.sum_data[user_id]}")
            )
            self.sum_data[user_id] = 0
            controller.stop()
            return
        if msg.isdigit():
            self.sum_data[user_id] += int(msg)
            await event.send(event.plain_result(f"当前总和：{self.sum_data[user_id]}"))
        else:
            await event.send(event.plain_result("请输入数字或“退出”结束"))
        controller.keep(timeout=60, reset_timeout=True)

    # 简单问答功能
    @session_waiter(timeout=60, record_history_chains=False)
    async def start_simple_qa(self, controller: SessionController, event: AstrMessageEvent):
        question = event.message_str.strip()
        if question == "退出":
            await event.send(event.plain_result("问答会话已结束~"))
            controller.stop()
            return
        await event.send(event.plain_result(f"你问的是：{question}\n示例回答：这是一个测试回答~"))
        controller.keep(timeout=60, reset_timeout=True)
