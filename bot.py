from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import os

TOKEN = "8200537504:AAG_rTfmZLs54UhmnDG69BDMBTpO6EwSjfU"
ADMIN_ID = 1293649098

# 📁 PDF FILES
PDF_FILES = {
    "Chemistry Handbook": "chemistry_handbook.pdf",
    "Physics Handbook": "physics_handbook.pdf",
    "Biology Handbook": "biology_handbook.pdf"
}

# 💰 PRICES
PRICES = {
    "Chemistry Handbook": 499,
    "Physics Handbook": 499,
    "Biology Handbook": 499
}

# 💾 USER DATA
USERS = {}

# 🏠 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📚 Courses", callback_data="courses")],
        [InlineKeyboardButton("🛒 My Purchases", callback_data="purchases")]
    ]
    await update.message.reply_text(
        "🎓 Welcome to StudyXpress",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 🔘 BUTTON HANDLER
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # 📚 COURSES
    if query.data == "courses":
        keyboard = [
            [InlineKeyboardButton("Class 11 (NEET)", callback_data="neet")]
        ]
        await query.edit_message_text("📚 Select Course", reply_markup=InlineKeyboardMarkup(keyboard))

    # 🎯 NEET SECTION
    elif query.data == "neet":
        keyboard = [
            [InlineKeyboardButton("Chemistry Handbook", callback_data="buy|Chemistry Handbook")],
            [InlineKeyboardButton("Physics Handbook", callback_data="buy|Physics Handbook")],
            [InlineKeyboardButton("Biology Handbook", callback_data="buy|Biology Handbook")],
            [InlineKeyboardButton("⬅️ Back", callback_data="courses")]
        ]
        await query.edit_message_text("📘 Select Handbook", reply_markup=InlineKeyboardMarkup(keyboard))

    # 💳 BUY (SHOW PRICE FIRST)
    elif query.data.startswith("buy"):
        item = query.data.split("|")[1]
        context.user_data["item"] = item

        price = PRICES.get(item, 99)

        keyboard = [
            [InlineKeyboardButton("📸 Send Payment Screenshot", callback_data=f"pay|{item}")],
            [InlineKeyboardButton("⬅️ Back", callback_data="neet")]
        ]

        await query.edit_message_text(
            f"""📘 {item}

🔥 Premium Course
💰 Price: ₹{price}

📚 Full NEET Handbook
⚡ Instant Access After Approval

💳 UPI: krishnarajput232008@ybl
""",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # 📸 PAY STEP
    elif query.data.startswith("pay"):
        item = query.data.split("|")[1]
        context.user_data["item"] = item
        await query.message.reply_text("📸 Send your payment screenshot here.")

    # 🛒 PURCHASES
    elif query.data == "purchases":
        purchased = USERS.get(user_id, [])

        if not purchased:
            await query.edit_message_text("❌ No purchases yet.")
        else:
            for item in purchased:
                file = PDF_FILES.get(item)
                if file and os.path.exists(file):
                    await query.message.reply_document(open(file, "rb"))

# 📸 HANDLE SCREENSHOT
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    item = context.user_data.get("item")

    if not item:
        return

    keyboard = [[
        InlineKeyboardButton("✅ Approve", callback_data=f"approve|{user.id}|{item}"),
        InlineKeyboardButton("❌ Reject", callback_data="reject")
    ]]

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=f"User ID: {user.id}\nItem: {item}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text("⏳ Waiting for admin approval...")

# 👨‍💼 ADMIN APPROVAL
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("approve"):
        _, user_id, item = query.data.split("|")
        user_id = int(user_id)

        USERS.setdefault(user_id, []).append(item)

        file = PDF_FILES.get(item)

        if file and os.path.exists(file):
            await context.bot.send_document(
                chat_id=user_id,
                document=open(file, "rb"),
                caption=f"✅ Approved! Here is your {item}"
            )

        await query.edit_message_caption("✅ Approved & Sent")

# 🚀 RUN
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(CallbackQueryHandler(admin, pattern="approve"))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

print("🚀 Bot Running...")
app.run_polling()