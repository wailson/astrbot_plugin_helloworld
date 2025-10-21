import astrbot.api.message_components as Comp
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Star  # 入口基类
from astrbot.core.utils.session_waiter import (
    session_waiter,
    SessionController,
)

# 用类封装插件功能并继承 Star
class astrbot_plugin_Cs(Star):
    # 菜单触发
    @filter.command("菜单")
    async def show_menu(self, event: AstrMessageEvent):
        try:
            yield event.plain_result(
                "功能菜单：\n1. 成语接龙\n2. 数字累加\n3. 简单问答\n请输入功能编号进入，或者输入“退出”结束。"
            )

            # 会话控制器
            @session_waiter(timeout=60, record_history_chains=False)
            async def menu_waiter(controller: SessionController, event: AstrMessageEvent):
                choice = event.message_str.strip()

                if choice == "退出":
                    await event.send(event.plain_result("已退出菜单~"))
                    controller.stop()
                    return

                if choice == "1":
                    await event.send(event.plain_result("进入成语接龙模式，输入成语，输入“退出”可结束~"))
                    await self.start_idiom_game(controller, event)
                elif choice == "2":
                    await event.send(event.plain_result("进入数字累加模式，输入数字，输入“退出”可结束~"))
                    await self.start_number_sum(controller, event)
                elif choice == "3":
                    await event.send(event.plain_result("进入简单问答模式，输入问题，输入“退出”可结束~"))
                    await self.start_simple_qa(controller, event)
                else:
                    await event.send(event.plain_result("无效选择，请输入 1, 2 或 3，或输入“退出”结束。"))

            try:
                await menu_waiter(event)
            except TimeoutError:
                yield event.plain_result("菜单会话超时了！")
            finally:
                event.stop_event()

        except Exception as e:
            yield event.plain_result("发生错误：" + str(e))

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
            await event.send(event.plain_result("接龙示例：先见之明"))
        controller.keep(timeout=60, reset_timeout=True)

    # 数字累加功能
    sum_data = {}

    @session_waiter(timeout=60, record_history_chains=False)
    async def start_number_sum(self, controller: SessionController, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        if user_id not in self.sum_data:
            self.sum_data[user_id] = 0
        msg = event.message_str.strip()

        if msg == "退出":
            await event.send(event.plain_result(f"数字累加结束，总和为：{self.sum_data[user_id]}"))
            self.sum_data[user_id] = 0
            controller.stop()
            return
        
        if msg.isdigit():
            self.sum_data[user_id] += int(msg)
            await event.send(event.plain_result(f"当前总和：{self.sum_data[user_id]}"))
        else:
            await event.send(event.plain_result("请输入数字或“退出”结束。"))
        controller.keep(timeout=60, reset_timeout=True)

    # 简单问答功能
    @session_waiter(timeout=60, record_history_chains=False)
    async def start_simple_qa(self, controller: SessionController, event: AstrMessageEvent):
        question = event.message_str.strip()
        if question == "退出":
            await event.send(event.plain_result("问答会话已结束~"))
            controller.stop()
            return

        # 简单演示回答
        await event.send(event.plain_result(f"你问的是：{question}\n示例回答：这是一个测试回答~"))
        controller.keep(timeout=60, reset_timeout=True)
