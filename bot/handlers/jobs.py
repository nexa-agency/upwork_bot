from aiogram import Router, types

router = Router()

@router.message()
async def echo_handler(message: types.Message) -> None:
    """
    Этот обработчик будет отвечать на любое входящее сообщение.
    В реальном проекте здесь будет логика обработки задач.
    """
    try:
        await message.send_copy(message.chat.id)
    except TypeError:
        await message.answer("Nice try!")