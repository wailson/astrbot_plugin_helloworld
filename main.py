import astrbot.api.message_components as Comp
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Star, Context, register
from astrbot.core.utils.session_waiter import session_waiter, SessionController, SessionFilter

# 会话过滤器：确保同一个用户或同一个群内同一个用户
class SingleUserFilter(SessionFilter):
    def __init__(self, user_id: str):
        self.user_id = user_id

    def filter(self, event: AstrMessageEvent) -> str:
        try:
            gid = event.get_group_id()
        except AttributeError:
            gid = None
        if gid:
            return f"{gid}:{self.user_id}"
        return self.user_id

@register("menu_plugin", "YourName", "多功能菜单插件", "1.0.0")
class MyPlugins(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.sum_data = {}

    def show_menu_text(self) -> str:
        return (
            "功能菜单：\n"
            "1. 成语接龙\n"
            "2. 数字累加\n"
            "3. 简单问答\n"
            "请输入功能编号进入，或输入“退出”结束"
        )

    # 入口命令：不要加 @session_waiter
    @filter.command("菜单")
    async def menu_cmd(self, event: AstrMessageEvent):
        await self.context.session_service.start_session(
            func=self.menu_session,
            session_filter=SingleUserFilter(event.get_sender_id()),
            event=event
        )

    # 菜单的会话处理逻辑
    @session_waiter(timeout=60, record_history_chains=False)
    async def menu_session(self, controller: SessionController, event: AstrMessageEvent):
        msg = event.message_str.strip()

        if controller.session_round == 1:
            await event.send(event.plain_result(self.show_menu_text()))
            controller.keep(timeout=60, reset_timeout=True)
            return

        if msg == "退出":
            await event.send(event.plain_result("已退出菜单~"))
            controller.stop()
            return

        if msg == "1":
            await event.send(event.plain_result("进入成语接龙模式~ 输入成语，输入“退出”结束"))
            await self.context.session_service.start_session(
                func=self.start_idiom_game,
                session_filter=SingleUserFilter(event.get_sender_id()),
                event=event
            )
        elif msg == "2":
            await event.send(event.plain_result("进入数字累加模式~ 输入数字，输入“退出”结束"))
            await self.context.session_service.start_session(
                func=self.start_number_sum,
                session_filter=SingleUserFilter(event.get_sender_id()),
                event=event
            )
        elif msg == "3":
            await event.send(event.plain_result("进入简单问答模式~ 输入问题，输入“退出”结束"))
            await self.context.session_service.start_session(
                func=self.start_simple_qa,
                session_filter=SingleUserFilter(event.get_sender_id()),
                event=event
            )
        else:
            await event.send(event.plain_result("输入无效，请重新选择："))
            controller.keep(timeout=60, reset_timeout=True)

    # 成语接龙模式
    @session_waiter(timeout=60, record_history_chains=False)
    async def start_idiom_game(self, controller: SessionController, event: AstrMessageEvent):
        msg = event.message_str.strip()
        if controller.session_round == 1:
            controller.keep(timeout=60, reset_timeout=True)
            return
        if msg == "退出":
            await event.send(event.plain_result("成语接龙结束~"))
            controller.stop()
        else:
            await event.send(event.plain_result(f"你输入的成语是：{msg}"))
            controller.keep(timeout=60, reset_timeout=True)

    # 数字累加模式
    @session_waiter(timeout=60, record_history_chains=False)
    async def start_number_sum(self, controller: SessionController, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        msg = event.message_str.strip()

        if controller.session_round == 1:
            self.sum_data[user_id] = 0
            controller.keep(timeout=60, reset_timeout=True)
            return

        if msg == "退出":
            await event.send(event.plain_result(f"数字累加结束，总和为 {self.sum_data[user_id]}"))
            controller.stop()
        else:
            try:
                num = int(msg)
                self.sum_data[user_id] += num
                await event.send(event.plain_result(f"当前累加总和: {self.sum_data[user_id]}"))
            except ValueError:
                await event.send(event.plain_result("请输入有效的数字或“退出”"))
            controller.keep(timeout=60, reset_timeout=True)

    # 简单问答模式
    @session_waiter(timeout=60, record_history_chains=False)
    async def start_simple_qa(self, controller: SessionController, event: AstrMessageEvent):
        msg = event.message_str.strip()
        if controller.session_round == 1:
            controller.keep(timeout=60, reset_timeout=True)
            return
        if msg == "退出":
            await event.send(event.plain_result("问答模式结束~"))
            controller.stop()
        else:
            await event.send(event.plain_result(f"你问的是：{msg}，我暂时还不会回答哦"))
            controller.keep(timeout=60, reset_timeout=True)
