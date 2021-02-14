
import discord
import sqlite3 as sql
import re
import secret
import db
import github
import asyncio

TOKEN = secret.TOKEN
QUEEN = "Frisia#8619"
client = discord.Client(intents=discord.Intents.all())
astrids_room = None
conn, c = db.with_db()

def db_init():
    c.execute(
        '''CREATE TABLE IF NOT EXISTS valentine_letter
        (recipent text, content text, sent bool)'''
    )
    c.execute(
        '''CREATE TABLE IF NOT EXISTS commits
        (sha text)'''
    )
    conn.commit()

@client.event
async def on_ready():
    global astrids_room
    astrids_room = client.get_channel(810425948120940574)
    asyncio.create_task(update_commits_loop())
    print(f'{client.user} has connected to discord')

@client.event
async def on_message(msg):
    global astrids_room
    if msg.author == client.user:
        return

    if msg.content == 'hi':
        await msg.channel.send('hey!')
    elif "not valid" in msg.content:
        await msg.channel.send('Everyone is valid')
    elif msg.content == 'userinfo':
        await msg.channel.send(str(msg.author))
    elif msg.content == 'who do you obey?' and str(msg.author) == QUEEN:
        await msg.channel.send("I obey only you.")
    elif msg.content == 'who do you obey?':
        await msg.channel.send("Queen Frisia")
    elif msg.content == 'users':
        print(client.users)
    elif starts_with('send letter', msg.content):
        await send_letter(msg)
    elif msg.content == 'update commits' and str(msg.author) == QUEEN:
        await github.post_new_commits(astrids_room)


def user_has_tag(user, tag):
    user_tag = user.name + '#' + user.discriminator
    return user_tag == tag

def find_by(ls, p):
    for el in ls:
        if p(el):
            return el
    return None

def read_letter(msg):
    try:
        [header, *paragraphs] = msg.content.split("\n\n")
        return ((header, paragraphs), False)
    except ValueError:
        return (0, True)

def starts_with(substring, string):
    start = string[:len(substring)].lower()
    if start == substring:
        return True
    return False

async def update_commits_loop():
    global astrids_room
    while True:
        print("Updating commits")
        await github.post_new_commits(astrids_room)
        await asyncio.sleep(60)

async def send_letter(msg):
    (parsed_letter, err) = read_letter(msg)
    if err:
        await msg.channel.send("Unable to parse letter. No header found!")
        return
    [header, body] = parsed_letter
    text = "\n\n".join(body)
    m = re.search('\w+(?:-\w+)*#[0-9]+', header)
    recipent_tag = m.group(0)
    recipent = find_by(client.users, lambda u: user_has_tag(u, recipent_tag))
    if(recipent is not None):
        c.execute('INSERT INTO valentine_letter VALUES (?, ?, false)',
                  (recipent_tag, text))
        conn.commit()
        await msg.channel.send(f"I've put your letter in the mailbox, ready to be sent to {recipent_tag}.\n\n :heart: :heart: :heart:")
    else:
        await msg.channel.send("Couldn't find a user with that name :slight_frown:\n\nTry sending your letter again!")


# MAIN
db_init()
client.run(TOKEN)
