from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Star, Context, register
from astrbot.core.utils.session_waiter import session_waiter, SessionController

@register("menu_plugin", "YourName", "菜单型插件示例", "1.0.0")
class MenuPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        # 保存每个用户的模式和数据
        self.current_mode = {}  # 当前模式: None | 'idiom' | 'sum' | 'qa'
        self.sum_data = {}      # 数字累加模式的数据

    @filter.command("菜单")
    @session_waiter(timeout=120, record_history_chains=False)
    async def menu_session(self, controller: SessionController, event: AstrMessageEvent):
        """
        单会话菜单：用户可选择不同功能，不开启子会话
        """
        user_id = event.get_sender_id()
        msg = event.message_str.strip()

        # 退出整个菜单会话
        if msg == "退出":
            await event.send(event.plain_result("菜单会话已退出~"))
            self.current_mode.pop(user_id, None)
            self.sum_data.pop(user_id, None)
            controller.stop()
            return

        # 如果当前没有选择模式，等待用户输入功能编号
        if user_id not in self.current_mode or self.current_mode[user_id] is None:
            if msg == "1":
                self.current_mode[user_id] = "idiom"
                await event.send(event.plain_result("进入成语接龙模式，请输入成语，输入“返回”回菜单"))
            elif msg == "2":
                self.current_mode[user_id] = "sum"
                self.sum_data[user_id] = 0
                await event.send(event.plain_result("进入数字累加模式，请输入数字，输入“返回”回菜单"))
            elif msg == "3":
                self.current_mode[user_id] = "qa"
                await event.send(event.plain_result("进入简单问答模式，请输入你的问题，输入“返回”回菜单"))
            else:
                await event.send(event.plain_result(
                    "功能菜单：\n"
                    "1. 成语接龙\n"
                    "2. 数字累加\n"
                    "3. 简单问答\n"
                    "请输入功能编号进入，或输入“退出”结束会话。"
                ))
            controller.keep(timeout=120, reset_timeout=True)
            return

        # 已经选择了模式
        mode = self.current_mode[user_id]

        # 回到菜单
        if msg == "返回":
            self.current_mode[user_id] = None
            await event.send(event.plain_result(
                "功能菜单：\n"
                "1. 成语接龙\n"
                "2. 数字累加\n"
                "3. 简单问答\n"
                "请输入功能编号进入，或输入“退出”结束会话。"
            ))
            controller.keep(timeout=120, reset_timeout=True)
            return

        # 处理不同模式的逻辑
        if mode == "idiom":
            if len(msg) != 4:
                await event.send(event.plain_result("成语必须是四个字哦~"))
            else:
                await event.send(event.plain_result(f"你输入的成语是：{msg}，接龙示例：先见之明"))

        elif mode == "sum":
            if msg.isdigit():
                self.sum_data[user_id] += int(msg)
                await event.send(event.plain_result(f"当前总和：{self.sum_data[user_id]}"))
            else:
                await event.send(event.plain_result("请输入数字，或输入“返回”回菜单"))

        elif mode == "qa":
            await event.send(event.plain_result(f"你问的是：{msg}\n我的回答是：这是一个演示回答~"))

        controller.keep(timeout=120, reset_timeout=True)
