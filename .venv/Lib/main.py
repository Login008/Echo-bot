from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes


# Инициализация пустой доски игры
def init_board():
    return [[" " for _ in range(3)] for _ in range(3)]


def board_to_text(board):
    return "\n".join([" | ".join(row) for row in board])


def check_winner(board):
    # Проверка строк, столбцов и диагоналей
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != " ":
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] != " ":
            return board[0][i]
    if board[0][0] == board[1][1] == board[2][2] != " ":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != " ":
        return board[0][2]
    return None


def is_draw(board):
    return all(cell != " " for row in board for cell in row)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['board'] = init_board()
    context.user_data['current_player'] = 'X'
    await update.message.reply_text(
        "Добро пожаловать в игру Крестики-Нолики!\n" +
        board_to_text(context.user_data['board']),
        reply_markup=generate_keyboard(context.user_data['board'])
    )


def generate_keyboard(board):
    keyboard = []
    for i, row in enumerate(board):
        buttons = [InlineKeyboardButton(text=cell if cell != " " else "⬜", callback_data=f"{i},{j}") for j, cell in
                   enumerate(row)]
        keyboard.append(buttons)
    return InlineKeyboardMarkup(keyboard)


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    board = context.user_data['board']
    current_player = context.user_data['current_player']

    i, j = map(int, query.data.split(","))

    if board[i][j] != " ":
        await query.edit_message_text(
            "Эта клетка уже занята!\n" + board_to_text(board),
            reply_markup=generate_keyboard(board)
        )
        return

    board[i][j] = current_player
    winner = check_winner(board)
    if winner:
        await query.edit_message_text(f"Игрок {winner} победил!\n" + board_to_text(board))
        return

    if is_draw(board):
        await query.edit_message_text("Ничья!\n" + board_to_text(board))
        return

    context.user_data['current_player'] = 'O' if current_player == 'X' else 'X'
    await query.edit_message_text(
        f"Ход игрока {context.user_data['current_player']}\n" + board_to_text(board),
        reply_markup=generate_keyboard(board)
    )


def main():
    application = Application.builder().token("7946086349:AAHYLVwHJyAJkj3GOSL_LjcIMuTlzx8ZNnA").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))

    application.run_polling()


if __name__ == "__main__":
    main()
