import astrbot.api.message_components as Comp
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Star, Context, register
from astrbot.core.utils.session_waiter import session_waiter, SessionController

@register("menu_plugin", "YourName", "一个带菜单的演示插件", "1.0.0")
class MyPlugins(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.sum_data = {}        # 存数字累加的数据
        self.current_mode = {}    # 存每个用户当前模式: None | 'idiom' | 'sum' | 'qa'

    @filter.command("菜单")
    @session_waiter(timeout=60, record_history_chains=False)
    async def menu_session(self, controller: SessionController, event: AstrMessageEvent):
        uid = event.get_sender_id()
        msg = event.message_str.strip()

        # 退出整个会话
        if msg == "退出":
            await event.send(event.plain_result("已退出菜单~"))
            self.sum_data.pop(uid, None)
            self.current_mode.pop(uid, None)
            controller.stop()
            return

        # 状态为空，就显示菜单或进入模式
        if uid not in self.current_mode or self.current_mode[uid] is None:
            if msg == "1":
                self.current_mode[uid] = "idiom"
                await event.send(event.plain_result("进入成语接龙模式，请输入成语，输入“返回”回菜单"))
            elif msg == "2":
                self.current_mode[uid] = "sum"
                self.sum_data[uid] = 0
                await event.send(event.plain_result("进入数字累加模式，请输入数字，输入“返回”回菜单"))
            elif msg == "3":
                self.current_mode[uid] = "qa"
                await event.send(event.plain_result("进入简单问答模式，请输入你的问题，输入“返回”回菜单"))
            else:
                await event.send(event.plain_result(
                    "功能菜单：\n"
                    "1. 成语接龙\n"
                    "2. 数字累加\n"
                    "3. 简单问答\n"
                    "请输入 1 / 2 / 3 进入，或输入“退出”结束会话"
                ))
            controller.keep(timeout=60, reset_timeout=True)
            return

        # 已选择模式的情况
        mode = self.current_mode[uid]
        if msg == "返回":
            self.current_mode[uid] = None
            await event.send(event.plain_result(
                "功能菜单：\n"
                "1. 成语接龙\n"
                "2. 数字累加\n"
                "3. 简单问答\n"
                "请输入 1 / 2 / 3 进入，或输入“退出”结束会话"
            ))
            controller.keep(timeout=60, reset_timeout=True)
            return

        # 模式处理逻辑
        if mode == "idiom":
            if len(msg) != 4:
                await event.send(event.plain_result("成语必须是四个字哦~"))
            else:
                await event.send(event.plain_result(f"你输入的成语是：{msg}，接龙示例：先见之明"))

        elif mode == "sum":
            if msg.isdigit():
                self.sum_data[uid] += int(msg)
                await event.send(event.plain_result(f"当前总和：{self.sum_data[uid]}"))
            else:
                await event.send(event.plain_result("请输入数字，或输入“返回”回菜单"))

        elif mode == "qa":
            await event.send(event.plain_result(f"你问的是：{msg}\n示例回答：这是一个测试回答~"))

        controller.keep(timeout=60, reset_timeout=True)
