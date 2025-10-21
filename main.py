import astrbot.api.message_components as Comp
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Star, Context, register
from astrbot.core.utils.session_waiter import session_waiter, SessionController

@register("menu_plugin", "YourName", "一个带菜单的演示插件", "1.0.0")
class MyPlugins(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.sum_data = {}

    @filter.command("菜单")
    async def show_menu(self, event: AstrMessageEvent):
        # 完全使用 await event.send 发送消息
        await event.send(event.plain_result(
            "功能菜单：\n1. 成语接龙\n2. 数字累加\n3. 简单问答\n请输入功能编号进入，或者输入“退出”结束。"
        ))
        
        # 定义一个新的会话处理方式，避免可能的装饰器问题
        async def menu_handler():
            # 创建一个会话ID
            session_id = f"menu_{event.get_sender_id()}"
            
            # 使用一个简单的会话循环代替session_waiter装饰器
            import asyncio
            timeout = 60
            start_time = asyncio.get_event_loop().time()
            
            while True:
                # 检查超时
                current_time = asyncio.get_event_loop().time()
                if current_time - start_time > timeout:
                    await event.send(event.plain_result("菜单会话超时了！"))
                    break
                
                # 等待用户回复
                reply = await self.context.wait_for_message(event.get_sender_id())
                if not reply:
                    continue
                
                choice = reply.strip()
                if choice == "退出":
                    await event.send(event.plain_result("已退出菜单~"))
                    break
                
                if choice == "1":
                    await event.send(event.plain_result("进入成语接龙模式，输入成语，输入“退出”可结束~"))
                    await self.idiom_game_handler(event)
                elif choice == "2":
                    await event.send(event.plain_result("进入数字累加模式，输入数字，输入“退出”可结束~"))
                    await self.number_sum_handler(event)
                elif choice == "3":
                    await event.send(event.plain_result("进入简单问答模式，输入问题，输入“退出”可结束~"))
                    await self.qa_handler(event)
                else:
                    await event.send(event.plain_result("无效选择，请输入 1, 2 或 3，或输入“退出”结束。"))
                
                # 重置超时计时器
                start_time = asyncio.get_event_loop().time()
            
            event.stop_event()
        
        # 启动会话处理
        try:
            await menu_handler()
        except Exception as e:
            await event.send(event.plain_result(f"发生错误：{str(e)}"))

    async def idiom_game_handler(self, event: AstrMessageEvent):
        import asyncio
        timeout = 60
        start_time = asyncio.get_event_loop().time()
        
        while True:
            # 检查超时
            current_time = asyncio.get_event_loop().time()
            if current_time - start_time > timeout:
                await event.send(event.plain_result("成语接龙会话超时了！"))
                break
            
            # 等待用户输入成语
            idiom = await self.context.wait_for_message(event.get_sender_id())
            if not idiom:
                continue
            
            idiom = idiom.strip()
            if idiom == "退出":
                await event.send(event.plain_result("成语接龙已结束~"))
                break
            
            if len(idiom) != 4:
                await event.send(event.plain_result("成语必须是四个字哦~"))
            else:
                await event.send(event.plain_result("接龙示例：先见之明"))
            
            # 重置超时计时器
            start_time = asyncio.get_event_loop().time()

    async def number_sum_handler(self, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        if user_id not in self.sum_data:
            self.sum_data[user_id] = 0
        
        import asyncio
        timeout = 60
        start_time = asyncio.get_event_loop().time()
        
        while True:
            # 检查超时
            current_time = asyncio.get_event_loop().time()
            if current_time - start_time > timeout:
                await event.send(event.plain_result("数字累加会话超时了！"))
                break
            
            # 等待用户输入数字
            msg = await self.context.wait_for_message(event.get_sender_id())
            if not msg:
                continue
            
            msg = msg.strip()
            if msg == "退出":
                await event.send(event.plain_result(f"数字累加结束，总和为：{self.sum_data[user_id]}"))
                self.sum_data[user_id] = 0
                break
            
            if msg.isdigit():
                self.sum_data[user_id] += int(msg)
                await event.send(event.plain_result(f"当前总和：{self.sum_data[user_id]}"))
            else:
                await event.send(event.plain_result("请输入数字或“退出”结束。"))
            
            # 重置超时计时器
            start_time = asyncio.get_event_loop().time()

    async def qa_handler(self, event: AstrMessageEvent):
        import asyncio
        timeout = 60
        start_time = asyncio.get_event_loop().time()
        
        while True:
            # 检查超时
            current_time = asyncio.get_event_loop().time()
            if current_time - start_time > timeout:
                await event.send(event.plain_result("问答会话超时了！"))
                break
            
            # 等待用户输入问题
            question = await self.context.wait_for_message(event.get_sender_id())
            if not question:
                continue
            
            question = question.strip()
            if question == "退出":
                await event.send(event.plain_result("问答会话已结束~"))
                break
            
            await event.send(event.plain_result(f"你问的是：{question}\n示例回答：这是一个测试回答~"))
            
            # 重置超时计时器
            start_time = asyncio.get_event_loop().time()
