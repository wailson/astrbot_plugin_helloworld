import astrbot.api.message_components as Comp
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Star, Context, register
from astrbot.core.utils.session_waiter import session_waiter, SessionController, SessionFilter


@register("menu_plugin", "YourName", "一个带菜单选择的演示插件", "1.0.0")
class MenuPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.sum_data = {}  # 用于数字累加

    def show_menu(self) -> str:
        return (
            "功能菜单：\n"
            "1. 成语接龙\n"
            "2. 数字累加\n"
            "3. 简单问答\n"
            "请输入功能编号进入\n"
            "输入“返回”回到菜单，输入“退出”结束会话"
        )

    # ===== 菜单入口，会话开始 =====
    @filter.command("菜单")
    @session_waiter(timeout=300, record_history_chains=False)
    async def menu_session(self, event: AstrMessageEvent, controller: SessionController):
        """
        菜单选择会话入口
        只有在这个会话中输入数字才有效
        """
        msg = event.message_str.strip()

        # 第一次触发时显示菜单
        if controller.session_round == 1:
            await event.send(event.plain_result(self.show_menu()))
            controller.keep(timeout=60, reset_timeout=True)
            return

        # 退出整个会话
        if msg == "退出":
            await event.send(event.plain_result("已退出菜单~"))
            controller.stop()
            return

        # 选择功能
        if msg == "1":
            await event.send(event.plain_result("进入成语接龙模式~ 输入成语，输入“返回”回到菜单"))
            await self.start_idiom_game(event, session_filter=SessionFilter(scope="user"))
        elif msg == "2":
            await event.send(event.plain_result("进入数字累加模式~ 输入数字，输入“返回”回到菜单"))
            await self.start_number_sum(event, session_filter=SessionFilter(scope="user"))
        elif msg == "3":
            await event.send(event.plain_result("进入问答模式~ 输入问题，输入“返回”回到菜单"))
            await self.start_simple_qa(event, session_filter=SessionFilter(scope="user"))
        else:
            await event.send(event.plain_result("无效选择，请输入 1 / 2 / 3，或“退出”"))

        controller.keep(timeout=60, reset_timeout=True)

    # ===== 成语接龙模式 =====
    @session_waiter(timeout=60, record_history_chains=False)
    async def start_idiom_game(self, event: AstrMessageEvent, controller: SessionController):
        msg = event.message_str.strip()

        if msg == "返回":
            await event.send(event.plain_result(self.show_menu()))
            await self.menu_session(event, session_filter=SessionFilter(scope="user"))
            controller.stop()
            return

        if msg == "退出":
            await event.send(event.plain_result("成语接龙已结束~"))
            controller.stop()
            return

        if len(msg) != 4:
            await event.send(event.plain_result("成语必须是四个字哦~"))
        else:
            await event.send(event.plain_result(f"你输入的成语：{msg}\n接龙示例：先见之明"))

        controller.keep(timeout=60, reset_timeout=True)

    # ===== 数字累加模式 =====
    @session_waiter(timeout=60, record_history_chains=False)
    async def start_number_sum(self, event: AstrMessageEvent, controller: SessionController):
        user_id = event.get_sender_id()
        msg = event.message_str.strip()

        if user_id not in self.sum_data:
            self.sum_data[user_id] = 0

        if msg == "返回":
            await event.send(event.plain_result(self.show_menu()))
            await self.menu_session(event, session_filter=SessionFilter(scope="user"))
            controller.stop()
            return

        if msg == "退出":
            await event.send(event.plain_result(f"数字累加结束，总和为：{self.sum_data[user_id]}"))
            self.sum_data[user_id] = 0
            controller.stop()
            return

        if msg.isdigit():
            self.sum_data[user_id] += int(msg)
            await event.send(event.plain_result(f"当前总和：{self.sum_data[user_id]}"))
        else:
            await event.send(event.plain_result("请输入数字，或输入“返回”/“退出”"))

        controller.keep(timeout=60, reset_timeout=True)

    # ===== 问答模式 =====
    @session_waiter(timeout=60, record_history_chains=False)
    async def start_simple_qa(self, event: AstrMessageEvent, controller: SessionController):
        msg = event.message_str.strip()

        if msg == "返回":
            await event.send(event.plain_result(self.show_menu()))
            await self.menu_session(event, session_filter=SessionFilter(scope="user"))
            controller.stop()
            return

        if msg == "退出":
            await event.send(event.plain_result("问答会话已结束~"))
            controller.stop()
            return

        await event.send(event.plain_result(f"你问的是：{msg}\n示例回答：这是一个测试回答~"))
        controller.keep(timeout=60, reset_timeout=True)
