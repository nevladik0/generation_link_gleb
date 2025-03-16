import asyncio, logging

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import LabeledPrice, Message, PreCheckoutQuery
from config import *


logger = logging.getLogger(__name__)
invoices_router = Router(name=__name__)

@invoices_router.message(Command("start"))
async def command_start(message: Message) -> None:
    await message.answer(
        "Welcome! Please provide item details in the following format:\n"
        "Title|Description|Price\n"
        "For example: demo|Demo product|42"
    )


@invoices_router.message()
async def handle_item_details(message: Message, bot: Bot) -> None:
    item_details = message.text.split("|")
    
    if len(item_details) == 3:
        title, description, price = item_details
        try:
            price = int(price)
        except ValueError:
            await message.answer("Invalid price. Please enter a valid number.")
            return
        
        result = await bot.create_invoice_link(
            title=title,
            description=description,
            prices=[LabeledPrice(label=title, amount=price)],
            payload="gift-payload",
            currency="XTR",
        )
        await message.answer(result)
    else:
        await message.answer("Please provide item details in the correct format: Title|Description|Price")




@invoices_router.pre_checkout_query(F.invoice_payload == "gift-payload")
async def pre_checkout_query(query: PreCheckoutQuery) -> None:
    await query.answer(ok=True)


@invoices_router.message(F.successful_payment)
async def successful_payment(message: Message, bot: Bot) -> None:
    await bot.refund_star_payment(
        user_id=message.from_user.id,
        telegram_payment_charge_id=message.successful_payment.telegram_payment_charge_id,
    )
    await message.answer("Thanks. Your payment has been refunded.")


async def main() -> None:
    bot = Bot(token=TOKEN)

    dispatcher = Dispatcher()
    dispatcher.include_router(invoices_router)

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())