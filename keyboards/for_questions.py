from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def foo(btnList) -> ReplyKeyboardMarkup:
    kb = [ ]

    for btn in btnList:
        button = KeyboardButton(text=btn)
        row = [button]
        kb.append(row)

    return ReplyKeyboardMarkup(keyboard=kb)