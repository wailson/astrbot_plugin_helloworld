import astrbot.api.message_components as Comp
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Star, Context, register
from astrbot.core.utils.session_waiter import session_waiter, SessionController

@register("menu_plugin", "YourName", "数字菜单演示插件", "1.0.0")
class MenuPlugin(Star):
    """
    一个数字选择菜单插件，支持：
    1. 成语接龙
    2. 数字累加
    3. 简单问答
    使用 AstrBot 官方插件标准写法
    """

    def __init__(self, context: Context):
        super().__init__(context)
        self.user_state = {}  # uid: {"mode": None|"idiom"|"sum"|"qa", "sum_value": int}

    def show_menu(self) -> str:
        """返回菜单文本"""
        return (
            "功能菜单：\n"
            "1. 成语接龙\n"
            "2. 数字累加\n"
            "3. 简单问答\n"
            "请输入 1 / 2 / 3 进入功能\n"
            "输入“返回”回菜单，输入“退出”结束会话"
        )

    @filter.command("菜单")
    @session_waiter(timeout=600, record_history_chains=False)
    async def menu_session(self, controller: SessionController, event: AstrMessageEvent):
        """菜单指令会话入口"""
        uid = event.get_sender_id()
        msg = event.message_str.strip()

        # 初始化状态并显示菜单
        if uid not in self.user_state:
            self.user_state[uid] = {"mode": None, "sum_value": 0}
            await event.send(event.plain_result(self.show_menu()))
            controller.keep(timeout=60, reset_timeout=True)
            return

        # 退出会话
        if msg == "退出":
            await event.send(event.plain_result("已退出菜单~"))
            self.user_state.pop(uid, None)
            controller.stop()
            return

        mode = self.user_state[uid]["mode"]

        # 当前无模式 => 进行模式选择
        if mode is None:
            if msg == "1":
                self.user_state[uid]["mode"] = "idiom"
                await event.send(event.plain_result("进入成语接龙模式，请输入成语，输入“返回”回菜单"))
            elif msg == "2":
                self.user_state[uid]["mode"] = "sum"
                self.user_state[uid]["sum_value"] = 0
                await event.send(event.plain_result("进入数字累加模式，请输入数字，输入“返回”回菜单"))
            elif msg == "3":
                self.user_state[uid]["mode"] = "qa"
                await event.send(event.plain_result("进入问答模式，请输入你的问题，输入“返回”回菜单"))
            else:
                await event.send(event.plain_result("输入无效，请按数字选择：\n" + self.show_menu()))
            controller.keep(timeout=60, reset_timeout=True)
            return

        # 返回菜单
        if msg == "返回":
            self.user_state[uid]["mode"] = None
            await event.send(event.plain_result(self.show_menu()))
            controller.keep(timeout=60, reset_timeout=True)
            return

        # 模式逻辑
        if mode == "idiom":
            if len(msg) != 4:
                await event.send(event.plain_result("成语必须是四个字哦~"))
            else:
                await event.send(event.plain_result(f"你输入的成语：{msg}\n接龙示例：先见之明"))

        elif mode == "sum":
            if msg.isdigit():
                self.user_state[uid]["sum_value"] += int(msg)
                await event.send(event.plain_result(f"当前总和：{self.user_state[uid]['sum_value']}"))
            else:
                await event.send(event.plain_result("请输入数字，或输入“返回”回菜单"))

        elif mode == "qa":
            await event.send(event.plain_result(f"你问的是：{msg}\n示例回答：这是一个测试回答"))

        controller.keep(timeout=60, reset_timeout=True)
