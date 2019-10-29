import os
import slack
import time
import re
import sqlite3
import json

str_channel_id = 'CC.....18'
str_bot_id = 'UJ.....97'
str_my_id = 'DK.....48'
token='Your BUOAAT token'

def send_message(channel, text, attachments):
    client = slack.WebClient(token=token)
    response = client.chat_postMessage(
        channel=channel,
        text=text,
        attachments=attachments)

current_time = round(time.time())
conn = sqlite3.connect('trivia.db')
c = conn.cursor()
public_text = "Results\n"
c.execute("SELECT * FROM questions WHERE id = (SELECT min(id) FROM questions WHERE id > (SELECT max(question_id) FROM winners WHERE is_trivia_time = 1));")
question = c.fetchone()
public_text += f"*The last question was:*\n{question[1]}\n"
answers = json.loads(question[2])
if len(answers) > 1:
    public_text += f"*Correct answers:*\n"
else:
    public_text += f"*Correct answer:*\n"
c.execute(f"SELECT * FROM attempts WHERE question_id = {question[0]};")
attempts = c.fetchall()

for answer in answers:
    public_text += f"_{answer}_\n"

attachments = [{"title": question[4], "image_url": question[3]}]
send_message(channel=str_channel_id, text=public_text, attachments=attachments)

attachments =''
public_text = f"*Our Winners:*\n"
c.execute(f"SELECT * FROM attempts WHERE question_id={question[0]} and is_correct=1 order by attempt_time asc;")
winners = c.fetchall()

if winners:
    for i in range(len(winners)):
        if i == 0:
            prize = 10
        elif i == 1:
            prize = 5
        elif i == 2:
            prize = 3
        else:
            prize = 1
        if i < 3:
            public_text += f"*{i+1}.* <@{winners[i][1]}> +{prize}🌲\n"
        else:
            public_text += f"<@{winners[i][1]}> +{prize}🌲 "
    c.execute(f"INSERT OR IGNORE INTO winners VALUES ({question[0]},\'{winners[0][1]}\', {winners[0][2]}, 0);")
else:
    public_text += f"OMG *No One*\n"
    c.execute(f"INSERT OR IGNORE INTO winners VALUES ({question[0]},\'No one\', 0, 0);")
conn.commit()
send_message(channel=str_channel_id, text=public_text, attachments=attachments)
conn.close()


