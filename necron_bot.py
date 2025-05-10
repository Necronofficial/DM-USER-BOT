
from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
import time, os, sys

# Bot login
api_id = 123456
api_hash = 'apni daal bhai '
bot = TelegramClient('session', api_id, api_hash)
bot.start()

approved_users = set()
warn_count = {}

# ========== BASIC COMMANDS ==========

@bot.on(events.NewMessage(outgoing=True, pattern=r"\.alive"))
async def alive(event):
    await event.respond("**I am alive! Powered by @NECRON_OFFICIAL.**")
    await event.delete()

@bot.on(events.NewMessage(outgoing=True, pattern=r"\.id"))
async def get_id(event):
    reply = await event.get_reply_message()
    if reply:
        await event.respond(f"**User ID:** `{reply.sender_id}`")
    else:
        await event.respond(f"**Chat ID:** `{event.chat_id}`")
    await event.delete()

@bot.on(events.NewMessage(outgoing=True, pattern=r"\.me"))
async def whoami(event):
    user = await bot.get_me()
    await event.respond(f"**Name:** `{user.first_name}`\n**Username:** @{user.username}")
    await event.delete()

@bot.on(events.NewMessage(outgoing=True, pattern=r"\.ping"))
async def ping(event):
    start = time.time()
    msg = await event.respond("`Pinging...`")
    end = time.time()
    await msg.edit(f"`Pong! {round((end - start) * 1000)}ms`")
    await event.delete()

@bot.on(events.NewMessage(outgoing=True, pattern=r"\.join (.+)"))
async def join(event):
    chat = event.pattern_match.group(1)
    try:
        await bot(JoinChannelRequest(chat))
        await event.respond(f"**Joined `{chat}` successfully!**")
    except Exception as e:
        await event.respond(f"**Error:** `{str(e)}`")
    await event.delete()

@bot.on(events.NewMessage(outgoing=True, pattern=r"\.leave"))
async def leave(event):
    await event.respond("**Leaving this chat...**")
    await event.delete()
    await bot(LeaveChannelRequest(event.chat_id))

@bot.on(events.NewMessage(outgoing=True, pattern=r"\.spam (\d+) (.+)"))
async def spam(event):
    count = int(event.pattern_match.group(1))
    message = event.pattern_match.group(2)
    await event.delete()
    for _ in range(count):
        await bot.send_message(event.chat_id, message)

@bot.on(events.NewMessage(outgoing=True, pattern=r"\.restart"))
async def restart(event):
    await event.respond("**Restarting...**")
    await event.delete()
    os.execl(sys.executable, sys.executable, *sys.argv)

# ========== DM PROTECTION SYSTEM ==========

@bot.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def dm_guard(event):
    sender = await event.get_sender()
    user_id = sender.id

    if user_id in approved_users or sender.bot:
        return

    warn_count[user_id] = warn_count.get(user_id, 0) + 1

    if warn_count[user_id] == 1:
        await event.reply("**WARNING 1:** Don't spam. You are not approved to DM.")
    elif warn_count[user_id] == 2:
        await event.reply("**WARNING 2:** One more message and you'll be blocked.")
    else:
        await event.reply("**BLOCKED:** You were warned. This userbot does not like attitude.")
        await bot(BlockRequest(user_id))
        del warn_count[user_id]

# ========== APPROVE / BLOCK COMMANDS ==========

@bot.on(events.NewMessage(outgoing=True, pattern=r"\.approve"))
async def approve(event):
    sender = await event.get_sender()
    approved_users.add(sender.id)
    await event.respond("**User approved. You may DM now.**")
    await event.delete()

@bot.on(events.NewMessage(outgoing=True, pattern=r"\.disapprove"))
async def disapprove(event):                                     
    reply = await event.get_reply_message()
    if reply and reply.sender_id in approved_users:
        approved_users.remove(reply.sender_id)
        await event.respond("User disapproved.")
    await event.delete()

@bot.on(events.NewMessage(outgoing=True, pattern=r"\.block"))
async def block(event):
    sender = await event.get_sender()
    approved_users.discard(sender.id)
    await bot(BlockRequest(sender.id))
    await event.respond("**User blocked.**")
    await event.delete()

@bot.on(events.NewMessage(outgoing=True, pattern=r"\.unblock"))
async def unblock_user(event):
    reply = await event.get_reply_message()                           
    if reply:
        await bot(UnblockRequest(reply.sender_id))
        await event.respond("User unblocked.")
    await event.delete()
