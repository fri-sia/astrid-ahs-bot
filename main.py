
import os
import discord
import sqlite3 as sql
import re
import secret as s

TOKEN = s.TOKEN
QUEEN = "Frisia#8619"
client = discord.Client(intents=discord.Intents.all())
conn = sql.connect('astrid.db')
c = conn.cursor()

def db_init():
    c.execute(
        '''CREATE TABLE IF NOT EXISTS valentine_letter
        (recipent text, content text, sent bool)'''
    )
    conn.commit()

@client.event
async def on_ready():
    print(f'{client.user} has connected to discord')

@client.event
async def on_message(msg):
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
        (parsed_letter, err) = read_letter(msg)
        if err:
            await msg.channel.send("Unable to parse letter. No header found!")
            return
        [header, body] = parsed_letter
        text = "\n\n".join(body)
        m = re.search('[A-z]+#[0-9]+', header)
        recipent_tag = m.group(0)
        recipent = find_by(client.users, lambda u: user_has_tag(u, recipent_tag))
        if(recipent is not None):
            c.execute('INSERT INTO valentine_letter VALUES (?, ?, false)',
                      (recipent_tag, text))
            conn.commit()
            await msg.channel.send(f"I've put your letter in the mailbox, ready to be sent to {recipent_tag}.\n\n :heart: :heart: :heart:")
        else:
            await msg.channel.send("Couldn't find a user with that name :slight_frown:\n\nTry sending your letter again!")

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

# MAIN
db_init()
client.run(TOKEN)
