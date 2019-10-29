import time
import slack
import re
import sqlite3
import json
import datetime

BUOAAT = 'Your BUOAAT token'

rtmclient = slack.RTMClient(token=BUOAAT)
test_channel_id = 'GJ.....PM'
str_channel_id = 'CC.....18'
str_bot_id = 'UJ.....97'
str_my_id = 'DK.....48'

def show_help_message(user_id, bot_id, webclient, channel_id):
    text = f"Hi <@{user_id}>!\nPlease use direct messages " \
        f"via <@{bot_id}>\n"
    text += "*trivia* - get the last Trivia question\n"
    text += "*answer <Your answer>* - make a guess for Trivia\n"
    text += "*top* - top scores\n"
    text += "*help* - this guide\n"

    attachments = [
        {
            "title": "hint",
            "image_url": "https://i.yapx.ru/ENL5n.gif",
        }
    ]

    webclient.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text=text,
            attachments=attachments)


@slack.RTMClient.run_on(event='hello')
def starting(**payload):
    # data = payload['data']
    webclient = payload['web_client']
    webclient.chat_postMessage(channel=str_my_id, text='Start')

@slack.RTMClient.run_on(event='message')
def channel_message_processing(**payload):
    data = payload['data']
    print(str(payload['data']).encode('utf-8').strip())
    webclient = payload['web_client']
    if 'bot_id' not in data and ('subtype' not in data):
        current_time = round(time.time())
        channel_id = data['channel']
        # thread_ts = data['ts']
        user = data['user']
        text = data['text'].strip()
        privat_text = ''
        public_text = ''
        attachments = ''
        if text.lower() == 'trivia':
            conn = sqlite3.connect('trivia.db')
            c = conn.cursor()
            c.execute("SELECT * FROM questions WHERE id = (SELECT min(id) FROM questions WHERE id > (SELECT max(question_id) FROM winners));")
            question = c.fetchone()
            c.execute(f"SELECT is_trivia_time FROM winners where question_id={question[0] - 1};")
            is_trivia_time = c.fetchone()[0]
            conn.close()
            if is_trivia_time == 1:
                attachments = [{"title": "Hint: how to send a private message to @earthmonthbot", "image_url": "https://i.yapx.ru/ENL5n.gif"}]
                public_text = f"*{question[1]}*\nSend me a private message via <@{str_bot_id}>:\n*answer <Your Answer>*\n_(not case sensitive)_"
            else:
                public_text = f"*Please wait for a new question*"
        elif text[:6].lower() == 'answer':
            if channel_id == str_channel_id:
                privat_text = f"<@{user}> Please *remove* your message from the chat and send me privately! <@{str_bot_id}>"
            else:
                conn = sqlite3.connect('trivia.db')
                c = conn.cursor()
                c.execute("SELECT * FROM questions WHERE id = (SELECT min(id) FROM questions WHERE id > (SELECT max(question_id) FROM winners));")
                question = c.fetchone()
                c.execute(f"SELECT is_trivia_time FROM winners where question_id={question[0] - 1};")
                is_trivia_time = c.fetchone()[0]
                if is_trivia_time == 1:
                    answer = re.sub(r"[^\sa-zA-Z0-9_-]", "", text[7:100]).strip()
                    c.execute(f"SELECT * FROM attempts WHERE user_id=\'{user}\' and question_id={question[0]};")
                    answered = c.fetchone()
                    privat_text = f"*Your answer is*:\n{answer}\n"
                    if answered:
                        privat_text = f"*You've already answered*:\n{answered[3]}\n"
                    else:
                        answers = json.loads(question[2])
                        is_correct = 0
                        prize = 0
                        for a in answers:
                            if str(answer).lower() == str(a).lower():
                                is_correct = 1
                        c.execute(f"INSERT INTO attempts(user_id, question_id, answer, attempt_time, "
                                  f"is_correct) VALUES (\'{user}\',{question[0]},\'{answer.lower()}\',{current_time},{is_correct});")
                        conn.commit()
                        if is_correct == 1:
                            c.execute(f"SELECT * FROM attempts WHERE question_id={question[0]} and is_correct=1;")
                            winners_amount = len(c.fetchall())
                            if winners_amount == 1:
                                prize = 10
                            elif winners_amount == 2:
                                prize = 5
                            elif winners_amount == 3:
                                prize = 3
                            else:
                                prize = 1
                            privat_text += f"*Congratulations, you are right!* +{prize}🌲"
                            c.execute(f"INSERT OR IGNORE INTO scores (user_id, score) VALUES (\'{user}\', 0);")
                            c.execute(f"UPDATE scores SET score = score + {prize} WHERE user_id=\'{user}\';")
                            conn.commit()
                        else:
                            privat_text += "_Sorry, you are wrong :(_\n"
                else:
                    privat_text = f"*Please wait for a new question*"
                conn.close()

        elif text.lower() == 'top':
            conn = sqlite3.connect('trivia.db')
            public_text = '*🏆Top Scores*\n'
            c = conn.cursor()
            c.execute(f"SELECT * FROM scores order by score desc;")
            scores = c.fetchall()
            for top_place in range(len(scores)):
                public_text += f'*{top_place + 1}.* <@{scores[top_place][0]}> {scores[top_place][1]}🌲\n'
            conn.close()

        elif 'has joined the channel' in text.lower() or text.lower() == 'help':
            show_help_message(user, str_bot_id, webclient, channel_id)

        if privat_text:
            webclient.chat_postEphemeral(channel=channel_id, user=user, text=privat_text, attachments=attachments)
        if public_text:
            webclient.chat_postMessage(channel=channel_id, text=public_text, attachments=attachments)




rtmclient.start()
