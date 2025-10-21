import astrbot.api.message_components as Comp
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Star, Context, register
from astrbot.core.utils.session_waiter import session_waiter, SessionController

@register("menu_plugin", "YourName", "一个带菜单的演示插件", "1.0.0")
class MyPlugins(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        # 初始化用户数据存储
        self.sum_data = {}
        # 当前会话状态管理
        self.session_states = {}

    @filter.command("菜单")
    async def show_menu(self, event: AstrMessageEvent):
        """显示功能菜单"""
        try:
            # 使用标准方式发送消息
            await event.send(event.plain_result(
                "功能菜单：\n1. 成语接龙\n2. 数字累加\n3. 简单问答\n请输入功能编号进入，或者输入“退出”结束。"
            ))
            
            # 移除可能不支持的参数，避免session_filter错误
            @session_waiter(timeout=60)
            async def menu_waiter(controller: SessionController, event: AstrMessageEvent):
                user_id = event.get_sender_id()
                choice = event.message_str.strip()
                
                if choice == "退出":
                    # 清理会话状态
                    if user_id in self.session_states:
                        del self.session_states[user_id]
                    await event.send(event.plain_result("已退出菜单~"))
                    controller.stop()
                    return
                
                # 实现功能选择，不使用子会话，而是在同一会话中状态管理
                if choice == "1":
                    await event.send(event.plain_result("进入成语接龙模式，输入成语，输入“退出”可结束~"))
                    self.session_states[user_id] = "idiom_game"
                elif choice == "2":
                    await event.send(event.plain_result("进入数字累加模式，输入数字，输入“退出”可结束~"))
                    self.session_states[user_id] = "number_sum"
                elif choice == "3":
                    await event.send(event.plain_result("进入简单问答模式，输入问题，输入“退出”可结束~"))
                    self.session_states[user_id] = "simple_qa"
                else:
                    # 检查当前状态，根据状态调用不同处理方法
                    if user_id in self.session_states:
                        state = self.session_states[user_id]
                        if state == "idiom_game":
                            await self.handle_idiom_game(event)
                        elif state == "number_sum":
                            await self.handle_number_sum(event)
                        elif state == "simple_qa":
                            await self.handle_simple_qa(event)
                    else:
                        await event.send(event.plain_result("无效选择，请输入 1, 2 或 3，或输入“退出”结束。"))
                
                # 保持会话活动
                controller.keep(timeout=60, reset_timeout=True)

            try:
                await menu_waiter(event)
            except TimeoutError:
                await event.send(event.plain_result("菜单会话超时了！"))
            finally:
                event.stop_event()

        except Exception as e:
            await event.send(event.plain_result(f"发生错误：{str(e)}"))

    # 成语接龙处理函数
    async def handle_idiom_game(self, event: AstrMessageEvent):
        """处理成语接龙输入"""
        idiom = event.message_str.strip()
        if len(idiom) != 4:
            await event.send(event.plain_result("成语必须是四个字哦~"))
        else:
            await event.send(event.plain_result("接龙示例：先见之明"))

    # 数字累加处理函数
    async def handle_number_sum(self, event: AstrMessageEvent):
        """处理数字累加输入"""
        user_id = event.get_sender_id()
        msg = event.message_str.strip()
        
        if msg.isdigit():
            if user_id not in self.sum_data:
                self.sum_data[user_id] = 0
            self.sum_data[user_id] += int(msg)
            await event.send(event.plain_result(f"当前总和：{self.sum_data[user_id]}"))
        else:
            await event.send(event.plain_result("请输入数字或“退出”结束。"))

    # 简单问答处理函数
    async def handle_simple_qa(self, event: AstrMessageEvent):
        """处理问答输入"""
        question = event.message_str.strip()
        await event.send(event.plain_result(f"你问的是：{question}\n示例回答：这是一个测试回答~"))
