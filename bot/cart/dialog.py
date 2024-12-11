from aiogram import F
from aiogram_dialog import Dialog, Window, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Row, Button
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.text import Format

from bot.cart.handlers import (
    get_cart_data, on_prev, on_next, on_set_quantity, on_remove_item, accept_delivery_address, get_entered_addr,
    register_order
)

from bot.states import StartStates, CartStates

cart_dialog = Dialog(
    Window(
        Const(
            'Cart is empty now.',
            when=F["cart_empty"],
        ),
        Format(
            "🛒 **Item {index}/{total_items}**\n\n"
            "🔹 **Name:** {item[name]}\n"
            "🔢 **Quantity:** {item[quantity]}\n"
            "💲 **Price:** {item[price]:.2f}\n"
            "💰 **Total:** {item[total]:.2f}",
            when=~F["cart_empty"],
        ),
        Row(
            Button(Const("⬅️ Previous"), id="prev", on_click=on_prev),
            Button(Const("📝 Set Quantity"), id="set_quantity", on_click=on_set_quantity),
            Button(Const("🗑 Remove Item"), id="remove_item", on_click=on_remove_item),
            Button(Const("➡️ Next"), id="next", on_click=on_next),
            when=~F["cart_empty"],
        ),
        Row(
            Button(
                Const("⬅️ Back"),
                id="back_to_categories",
                on_click=lambda c, d, m: m.start(StartStates.MAIN, mode=StartMode.RESET_STACK),
            ),
            Button(
                Const("✅ Confirm"),
                id="confirm_cart",
                on_click=lambda c, d, m: m.switch_to(CartStates.ENTER_ADDRESS),
                when=~F["cart_empty"],
            ),

        ),
        state=CartStates.VIEW_CART,
        getter=get_cart_data,
    ),
    Window(
        Const("Enter your delivery address:"),
        MessageInput(accept_delivery_address),
        Button(
            Const("⬅️ Back"),
            id="back_to_categories",
            on_click=lambda c, d, m: m.start(CartStates.VIEW_CART),
        ),
        state=CartStates.ENTER_ADDRESS,
    ),
    Window(
        Format("Deliver to:\n{entered_addr}?"),
        Row(
            Button(
                Const("⬅️ Back"),
                id="back_to_categories",
                on_click=lambda c, d, m: m.switch_to(CartStates.ENTER_ADDRESS),
            ),
            Button(
                Const("✅ Confirm"),
                id="confirm_cart",
                on_click=register_order
            ),
        ),
        state=CartStates.ADDRESS_CONFIRM,
        getter=get_entered_addr,
    )
)
