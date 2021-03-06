
import discord
import requests
import db

REPO = "fri-sia/astrid-ahs-bot"
repo_url = lambda path: f'https://api.github.com/repos/{REPO}/{path}'

conn, c = db.with_db()

def fetch_commits():
    r = requests.get(repo_url('commits'))
    return r.json()

def commit_already_posted(commit):
    c.execute('''SELECT * FROM commits
    WHERE sha = ?''', (commit['sha'],))
    res = c.fetchone()
    return res is not None

async def post_new_commits(chan):
    commits = fetch_commits();
    i = 0
    while i < len(commits):
        if commit_already_posted(commits[i]):
            break
        i = i + 1
    new_commits_to_post = i
    if new_commits_to_post == 0:
        return
    for k in reversed(range(0, new_commits_to_post)):
        c.execute('INSERT INTO commits VALUES (?)', (commits[k]['sha'],))
        await chan.send(commits[k]['html_url'])
    conn.commit()
