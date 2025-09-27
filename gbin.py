import csv
import pycountry
import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Your API credentials
API_ID = 28075471
API_HASH = "6db86d600105807f18519ebbb515d676"
BOT_TOKEN = "7534237564:AAEuRDGG9NP5Z8WkGS7zUYMwxTqAwMa2kq0"

# Initialize the Pyrogram Client
app = Client("gbin_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Store user search states
user_search_states = {}

def get_country_name(code, fallback_country_name):
    try:
        country = pycountry.countries.get(alpha_2=code)
        return country.name if country else fallback_country_name
    except Exception as e:
        print(f"Error getting country name: {e}")
        return fallback_country_name

def search_bins_in_csv(prefix, csv_file='bins_all.csv'):
    """Search for all bins starting with the given prefix"""
    try:
        matching_bins = []
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0].startswith(prefix):
                    matching_bins.append({
                        "bin": row[0],
                        "country": row[1],
                        "flag": row[2],
                        "brand": row[3],
                        "type": row[4],
                        "level": row[5],
                        "bank": row[6]
                    })
        return matching_bins
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return []

def get_bins_for_page(matching_bins, page, bins_per_page=3):
    """Get bins for a specific page"""
    start_index = page * bins_per_page
    end_index = start_index + bins_per_page
    return matching_bins[start_index:end_index]

def create_keyboard(user_id, prefix, current_page, total_pages):
    """Create keyboard with navigation buttons"""
    keyboard = []
    
    # Navigation buttons
    nav_buttons = []
    if current_page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"gbin_prev_{user_id}_{prefix}_{current_page}"))
    
    if current_page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"gbin_next_{user_id}_{prefix}_{current_page}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Exit button
    keyboard.append([InlineKeyboardButton("𝗘𝘅𝗶𝘁⚠️", callback_data=f"gbin_exit_{user_id}_{prefix}_{current_page}")])
    
    return InlineKeyboardMarkup(keyboard)

@app.on_callback_query(filters.regex(r"^gbin_"))
async def handle_gbin_buttons(client, callback_query):
    try:
        data_parts = callback_query.data.split('_')
        action = data_parts[1]
        user_id = int(data_parts[2])
        search_prefix = data_parts[3]
        current_page = int(data_parts[4])
        
        # Check if the user clicking is the same as the original user
        if callback_query.from_user.id != user_id:
            await callback_query.answer("⚠️ This is not your search! Use /gbin to start your own search.", show_alert=True)
            return
        
        matching_bins = search_bins_in_csv(search_prefix)
        
        if not matching_bins:
            await callback_query.answer("No BINs found!", show_alert=True)
            return
        
        bins_per_page = 3
        total_pages = (len(matching_bins) + bins_per_page - 1) // bins_per_page
        
        if action == "next":
            current_page = min(current_page + 1, total_pages - 1)
        elif action == "prev":
            current_page = max(current_page - 1, 0)
        elif action == "exit":
            await callback_query.message.delete()
            await callback_query.answer()
            return
        
        # Get bins for current page
        page_bins = get_bins_for_page(matching_bins, current_page, bins_per_page)
        
        # Format the response
        a_symbol = f"<a href='tg://user?id={user_id}'>ア</a>"
        ki_symbol = f"<a href='tg://user?id={user_id}'>キ</a>"
        ka_symbol = f"<a href='tg://user?id={user_id}'>カ</a>"
        shu_symbol = f"<a href='tg://user?id={user_id}'>朱</a>"
        zero_symbol = f"<a href='tg://user?id={user_id}'>零</a>"
        gen_symbol = f"<a href='tg://user?id={user_id}'>ᥫ᭡</a>"
        user_link = f"<a href='tg://user?id={user_id}'>SPYDE</a>"
        
        # Build response with multiple bins
        resp = f"〈{a_symbol}〉𝙎𝙚𝙚𝙙 -» {search_prefix}xxx\n"
        resp += "- - - - - - - - - - - - - - - - - - - - -\n"
        
        for i, bin_info in enumerate(page_bins):
            brand = bin_info.get("brand", "N/A").upper()
            card_type = bin_info.get("type", "N/A").upper()
            level = bin_info.get("level", "N/A").upper()
            bank = bin_info.get("bank", "N/A")
            country_code = bin_info.get("country", "N/A")
            flag = bin_info.get("flag", "")
            country_full_name = get_country_name(country_code, country_code).upper()
            
            resp += f"〈{ki_symbol}〉𝘽𝙞𝙣 -» {bin_info['bin']}\n"
            resp += f"〈{ka_symbol}〉𝙄𝙣𝙛𝙤 -» {brand} - {card_type} - {level}\n"
            resp += f"〈{shu_symbol}〉𝘽𝙖𝙣𝙠 -» {bank}\n"
            resp += f"〈{zero_symbol}〉𝘾𝙤𝙪𝙣𝙩𝙧y -» {country_full_name} {flag}\n"
            
            if i < len(page_bins) - 1:
                resp += "- - - - - - - - - - - - - - - - - - - - -\n"
        
        resp += f"- - - - - - - - - - - - - - - - - - - - -\n"
        resp += f"〈{ki_symbol}〉𝙋𝙖𝙜𝙚 -» {current_page + 1}/{total_pages}\n"
        resp += f"- - - - - - - - - - - - - - - - - - - - -\n"
        resp += f"〈{gen_symbol}〉 𝙂𝙚𝙣 𝙗𝙮 -» {user_link}"
        
        # Create keyboard
        keyboard = create_keyboard(user_id, search_prefix, current_page, total_pages)
        
        await callback_query.message.edit_text(resp, reply_markup=keyboard, disable_web_page_preview=True)
        await callback_query.answer()
            
    except Exception as e:
        await callback_query.answer()
        print(f"Error in gbin callback: {e}")

@app.on_message(filters.command("gbin", [".", "/"]))
async def cmd_gbin(client, message):
    try:
        # Extract prefix from message
        if not message.text or len(message.text.split()) < 2:
            # Invalid format - with hyperlinked symbols
            jiu_symbol = f"<a href='tg://user?id={message.from_user.id}'>〆</a>"
            north_symbol = f"<a href='tg://user?id={message.from_user.id}'>北</a>"
            
            resp = f"""
〈{jiu_symbol}〉𝙎𝙮𝙨𝙩𝙚𝙢  

〈{north_symbol}〉 Invalid input ! ⚠
"""
            await message.reply_text(resp, quote=True)
            return
        
        prefix = message.text.split()[1].strip()
        
        # Validate prefix (should be numeric and between 1-6 digits)
        if not prefix.isdigit() or len(prefix) < 1 or len(prefix) > 6:
            jiu_symbol = f"<a href='tg://user?id={message.from_user.id}'>〆</a>"
            north_symbol = f"<a href='tg://user?id={message.from_user.id}'>北</a>"
            
            resp = f"""
〈{jiu_symbol}〉𝙎𝙮𝙨𝙩𝙚𝙢  

〈{north_symbol}〉 Invalid input ! ⚠
"""
            await message.reply_text(resp, quote=True)
            return
        
        # Search for matching bins
        matching_bins = search_bins_in_csv(prefix)
        
        if not matching_bins:
            jiu_symbol = f"<a href='tg://user?id={message.from_user.id}'>〆</a>"
            north_symbol = f"<a href='tg://user?id={message.from_user.id}'>北</a>"
            
            resp = f"""
〈{jiu_symbol}〉𝙎𝙮𝙨𝙩𝙚𝙢  

〈{north_symbol}〉 No BINs found starting with {prefix} ⚠
"""
            await message.reply_text(resp, quote=True)
            return
        
        # Store user state
        user_search_states[message.from_user.id] = {
            "prefix": prefix,
            "current_page": 0,
            "total_bins": len(matching_bins)
        }
        
        # Get bins for first page
        bins_per_page = 3
        total_pages = (len(matching_bins) + bins_per_page - 1) // bins_per_page
        page_bins = get_bins_for_page(matching_bins, 0, bins_per_page)
        
        # Create hyperlinked symbols
        a_symbol = f"<a href='tg://user?id={message.from_user.id}'>ア</a>"
        ki_symbol = f"<a href='tg://user?id={message.from_user.id}'>キ</a>"
        ka_symbol = f"<a href='tg://user?id={message.from_user.id}'>カ</a>"
        shu_symbol = f"<a href='tg://user?id={message.from_user.id}'>朱</a>"
        zero_symbol = f"<a href='tg://user?id={message.from_user.id}'>零</a>"
        gen_symbol = f"<a href='tg://user?id={message.from_user.id}'>ᥫ᭡</a>"
        user_link = f"<a href='tg://user?id={message.from_user.id}'>SPYDE</a>"
        
        # Build response with multiple bins
        resp = f"〈{a_symbol}〉𝙎𝙚𝙚𝙙 -» {prefix}xxx\n"
        resp += "- - - - - - - - - - - - - - - - - - - - -\n"
        
        for i, bin_info in enumerate(page_bins):
            brand = bin_info.get("brand", "N/A").upper()
            card_type = bin_info.get("type", "N/A").upper()
            level = bin_info.get("level", "N/A").upper()
            bank = bin_info.get("bank", "N/A")
            country_code = bin_info.get("country", "N/A")
            flag = bin_info.get("flag", "")
            country_full_name = get_country_name(country_code, country_code).upper()
            
            resp += f"〈{ki_symbol}〉𝘽𝙞𝙣 -» {bin_info['bin']}\n"
            resp += f"〈{ka_symbol}〉𝙄𝙣𝙛𝙤 -» {brand} - {card_type} - {level}\n"
            resp += f"〈{shu_symbol}〉𝘽𝙖𝙣𝙠 -» {bank}\n"
            resp += f"〈{zero_symbol}〉𝘾𝙤𝙪𝙣𝙩𝙧y -» {country_full_name} {flag}\n"
            
            if i < len(page_bins) - 1:
                resp += "- - - - - - - - - - - - - - - - - - - - -\n"
        
        resp += f"- - - - - - - - - - - - - - - - - - - - -\n"
        resp += f"〈{ki_symbol}〉𝙋𝙖𝙜𝙚 -» 1/{total_pages}\n"
        resp += f"- - - - - - - - - - - - - - - - - - - - -\n"
        resp += f"〈{gen_symbol}〉 𝙂𝙚𝙣 𝙗𝙮 -» {user_link}"
        
        # Create keyboard
        keyboard = create_keyboard(message.from_user.id, prefix, 0, total_pages)
        
        await message.reply_text(resp, quote=True, reply_markup=keyboard, disable_web_page_preview=True)

    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"Error in cmd_gbin: {error_msg}")
        await message.reply_text("❌ An error occurred while processing your request.", quote=True)

if __name__ == "__main__":
    print("🤖 GBIN Lookup Bot is starting...")
    print("Press Ctrl+C to stop the bot")
    app.run()
