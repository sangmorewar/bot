import discord
from discord.ext import commands
import random
import json
import os

# --- CẤU HÌNH HỆ THỐNG ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

DATA_FILE = "tu_tien_sangmore_final.json"
CANH_GIOI = ["Phàm Nhân", "Luyện Khí", "Trúc Cơ", "Kim Đan", "Nguyên Anh", "Hóa Thần", "Luyện Hư", "Hợp Thể", "Đại Thừa", "Độ Kiếp", "Tiên Nhân"]

# Cấp độ linh thú và sức mạnh cộng dồn
CAP_DO_THU = {
    "Thường": {"icon": "🐾", "power": 50, "rate": 60},
    "Hiếm": {"icon": "✨", "power": 200, "rate": 25},
    "Cực Hiếm": {"icon": "🔥", "power": 600, "rate": 10},
    "Huyền Thoại": {"icon": "👑", "power": 2000, "rate": 5}
}
DANH_SACH_TEN_THU = ["Linh Miêu", "Hỏa Kỳ Lân", "Hắc Long", "Kim Phượng", "Thiên Hổ", "Băng Xà"]

# --- QUẢN LÝ DỮ LIỆU ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

user_data = load_data()

def get_power(uid):
    data = user_data[uid]
    # Sức mạnh = (Cảnh giới * 200) + Tổng sức mạnh linh thú
    pwr = data["level"] * 200
    for thu in data["tui_do"]["thu"]:
        pwr += CAP_DO_THU[thu["cap"]]["power"]
    return pwr

# --- LỆNH HỆ THỐNG ---

@bot.command()
async def menu(ctx):
    """Bảng danh lục thần thông"""
    embed = discord.Embed(title="🏮 THIÊN THƯ CÁC - SANGMORE EDITION 🏮", color=0xffd700)
    embed.add_field(name="🧘 Tu Luyện", value="`!nhapdao` • Khai mở linh căn\n`!thongtin` • Xem trạng thái & túi đồ\n`!dokiep`   • Đột phá cảnh giới", inline=False)
    embed.add_field(name="⚔️ Tranh Đấu & Shop", value="`!pk @user` • Tỷ thí cướp linh thạch\n`!muado`    • Đến Vạn Bảo Cát mua trứng\n`!mo_trung` • Khai mở linh thú", inline=False)
    embed.add_field(name="💬 Chú thích", value="*Nhắn tin để nhận Tu Vi & Tỷ lệ 1% rơi trứng ngẫu nhiên*", inline=False)
    embed.set_footer(text="✍️ Chế tác bởi Đạo Hữu Sangmore")
    await ctx.send(embed=embed)

@bot.command()
async def nhapdao(ctx):
    uid = str(ctx.author.id)
    if uid not in user_data:
        user_data[uid] = {"name": ctx.author.name, "level": 0, "tu_vi": 0, "linh_thach": 100, "tui_do": {"trung": 0, "thu": []}}
        save_data(user_data)
        await ctx.send(f"✨ **{ctx.author.name}** đã cảm nhận được linh khí, chính thức nhập đạo!")
    else:
        await ctx.send("🔹 Đạo hữu đã có tên trong Tiên Bảng.")

@bot.command()
async def thongtin(ctx):
    uid = str(ctx.author.id)
    if uid not in user_data: return await ctx.send("Gõ `!nhapdao` trước.")
    data = user_data[uid]
    pwr = get_power(uid)
    
    embed = discord.Embed(title=f"🎋 TIÊN BẢNG: {data['name']}", color=0x2ecc71)
    embed.add_field(name="🛡️ Cảnh Giới", value=f"**{CANH_GIOI[data['level']]}**", inline=True)
    embed.add_field(name="⚔️ Lực Chiến", value=f"**{pwr}**", inline=True)
    embed.add_field(name="✨ Tu Vi", value=f"`{data['tu_vi']}`", inline=True)
    embed.add_field(name="💎 Linh Thạch", value=f"`{data['linh_thach']}`", inline=True)
    
    thu_str = "\n".join([f"{t['icon']} {t['ten']} ({t['cap']})" for t in data["tui_do"]["thu"][-5:]]) or "Chưa có"
    embed.add_field(name="🥚 Túi đồ", value=f"Số trứng: {data['tui_do']['trung']}", inline=False)
    embed.add_field(name="🐾 Linh Thú Hộ Vệ (5 con gần nhất)", value=thu_str, inline=False)
    embed.set_footer(text="Làm bởi Đạo Hữu Sangmore")
    await ctx.send(embed=embed)

@bot.command()
async def muado(ctx):
    """Vạn Bảo Cát"""
    uid = str(ctx.author.id)
    if uid not in user_data: return
    gia = 500
    if user_data[uid]["linh_thach"] < gia:
        return await ctx.send(f"❌ Thiếu Linh Thạch! Cần `{gia}` 💎 để mua trứng.")
    
    user_data[uid]["linh_thach"] -= gia
    user_data[uid]["tui_do"]["trung"] += 1
    save_data(user_data)
    await ctx.send("🛍️ Đạo hữu đã mua 1 **Trứng Linh Thú** từ Vạn Bảo Cát!")

@bot.command()
async def mo_trung(ctx):
    """Mở trứng nhận thú"""
    uid = str(ctx.author.id)
    if uid not in user_data or user_data[uid]["tui_do"]["trung"] <= 0:
        return await ctx.send("❌ Đạo hữu không có trứng để mở!")

    user_data[uid]["tui_do"]["trung"] -= 1
    caps = list(CAP_DO_THU.keys())
    weights = [CAP_DO_THU[c]["rate"] for c in caps]
    cap_nhan = random.choices(caps, weights=weights)[0]
    
    ten = random.choice(DANH_SACH_TEN_THU)
    moi = {"ten": ten, "cap": cap_nhan, "icon": CAP_DO_THU[cap_nhan]["icon"]}
    user_data[uid]["tui_do"]["thu"].append(moi)
    save_data(user_data)
    
    await ctx.send(f"🥚 **Trứng nở!** Chúc mừng đạo hữu nhận được **{moi['icon']} {moi['ten']}** phẩm cấp **{cap_nhan}** (Sức mạnh +{CAP_DO_THU[cap_nhan]['power']})!")

@bot.command()
async def pk(ctx, member: discord.Member):
    """Tỷ thí cướp linh thạch"""
    p1, p2 = str(ctx.author.id), str(member.id)
    if p1 not in user_data or p2 not in user_data: return await ctx.send("Cả hai cần nhập đạo!")
    if p1 == p2: return
    
    pow1, pow2 = get_power(p1), get_power(p2)
    win_rate = pow1 / (pow1 + pow2)
    
    if random.random() < win_rate:
        cuop = random.randint(30, 150)
        if user_data[p2]["linh_thach"] < cuop: cuop = user_data[p2]["linh_thach"]
        user_data[p1]["linh_thach"] += cuop
        user_data[p2]["linh_thach"] -= cuop
        await ctx.send(f"⚔️ **{ctx.author.name}** thắng trận! Cướp được `{cuop}` 💎 của **{member.name}**.")
    else:
        await ctx.send(f"💀 **{ctx.author.name}** đã bại trận!")
    save_data(user_data)

@bot.command()
async def dokiep(ctx):
    """Đột phá cảnh giới"""
    uid = str(ctx.author.id)
    if uid not in user_data: return
    lv = user_data[uid]["level"]
    req = (lv + 1) * 300
    if user_data[uid]["tu_vi"] < req: return await ctx.send(f"🔹 Cần `{req}` tu vi!")
    
    if random.random() < 0.65:
        user_data[uid]["level"] += 1
        user_data[uid]["tu_vi"] = 0
        user_data[uid]["linh_thach"] += 200
        await ctx.send(f"⚡ **THÀNH CÔNG!** Đạo hữu đã đột phá lên **{CANH_GIOI[lv+1]}**!")
    else:
        user_data[uid]["tu_vi"] //= 2
        await ctx.send("🏮 **THẤT BẠI!** Đạo hữu bị phản phệ, tu vi giảm một nửa.")
    save_data(user_data)

@bot.event
async def on_message(message):
    if message.author.bot: return
    uid = str(message.author.id)
    if uid in user_data:
        user_data[uid]["tu_vi"] += 1
        if random.random() < 0.01: # 1% rơi trứng khi chat
            user_data[uid]["tui_do"]["trung"] += 1
            await message.channel.send(f"🍀 **{message.author.name}** nhặt được 1 Trứng Linh Thú khi đang tu luyện!")
        save_data(user_data)
    await bot.process_commands(message)

bot.run('')
