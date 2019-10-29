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
public_text = "*It's Trivia Time!*\n"
c.execute("SELECT * FROM questions WHERE id = (SELECT min(id) FROM questions WHERE id > (SELECT max(question_id) FROM winners));")
question = c.fetchone()
c.execute(f"UPDATE winners set is_trivia_time = 1 where question_id = {question[0] - 1};")
conn.commit()
public_text += f"\n\n*The Next Question Is:*\n"
public_text += f"*{question[1]}*\nSend me a private message via <@{str_bot_id}>:\n*answer <Your Answer>*\n_(not case sensitive)_"
attachments = [{"title": "Hint: how to send a private message to @earthmonthbot", "image_url": "https://i.yapx.ru/ENL5n.gif"}]
send_message(channel=str_channel_id, text=public_text, attachments=attachments)
conn.close()
