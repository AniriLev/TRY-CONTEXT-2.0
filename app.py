import os

from cs50 import SQL
from flask import Flask,render_template, request, session

from main import gen_sentence, check_answers

# Configure application
app = Flask(__name__)
app.secret_key = "my_secret_key"

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///learnt_voco.db")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":


        noun = [word.strip() for word in request.form.get("noun").split(",")]
        if not noun or noun[0] == "" or noun[0] == " ":
            noun = ["cat", "fish"]
        elif len(noun) == 1:
            if noun[0] == "cat":
                noun.append("fish")
            elif noun[0] == "fish":
                noun.append("cat")

        trans_verb = [word.strip() for word in request.form.get("transitive_verb").split(",")]
        if not trans_verb or trans_verb[0] == "":
            trans_verb = ["eat"]

        intrans_verb = [word.strip() for word in request.form.get("intransitive_verb").split(",")]
        if not intrans_verb or intrans_verb[0] == "":
            intrans_verb = ["play"]

        adjective = [word.strip() for word in request.form.get("adjective").split(",")]
        if not adjective or adjective[0] == "":
            adjective = ["cute"]

        place = [word.strip() for word in request.form.get("place").split(",")]
        if not place or place[0] == "":
            place = ["at home"]

        time = [word.strip() for word in request.form.get("time").split(",")]
        if not time or time[0] == "":
            time = ["at night"]

        pos = {"nouns": noun, "transitive_verbs": trans_verb, "intransitive_verbs": intrans_verb, "adjectives": adjective, "places": place, "times": time}
        for poses, words in pos.items():
            for word in words:
                if word.isdigit():
                    message = "Please, type words in correctly"
                    return render_template("error.html", message=message)

        sentence, question, context, word_list = gen_sentence(pos)
        session["sentence"] = sentence
        session["question"] = question
        session["context"] = context

        db_content = db_insertion(word_list, sentence)
        if db_content is True:
            return render_template("sentence.html", sentence=sentence, question=question)
        else:
            used = db.execute("SELECT voco.word, context.sentence FROM voco JOIN link ON voco.id = link.word_id JOIN context ON context.id = link.sentence_id")
            return render_template("history.html", used_words=db_content, used=used)

    return render_template("index.html")

def db_insertion(word_list, sentence):
        DEFAULT_SET = {"cat", "fish", "eat", "play", "cute", "at home", "at night"}

        used_id = []
        for word_l, pos in word_list:
            if word_l in DEFAULT_SET:
                continue

            word_id = db.execute("SELECT id FROM voco WHERE word=? AND part_of_speach NOT IN (?,?)", word_l, "places", "times")
            if word_id:
                word_info=[word_id, pos, word_l]
                used_id.append(word_info)

        if len(used_id) == 0:
            db.execute("INSERT OR IGNORE INTO context (sentence) VALUES(?)", sentence)
            sen_id = db.execute("SELECT id FROM context WHERE sentence=?", sentence)[0]['id']
            for word_l, pos in word_list:
                if word_l in DEFAULT_SET:
                    continue

                db.execute("INSERT OR IGNORE INTO voco (word, part_of_speach) VALUES(?, ?)", word_l, pos)
                w_id = db.execute("SELECT id FROM voco WHERE word=?", word_l)[0]['id']
                db.execute("INSERT OR IGNORE INTO link (word_id, sentence_id) VALUES(?,?)", w_id, sen_id)
            return True

        else:
            used_list = []
            for word_id, pos, w in used_id:
                l_sent = db.execute("""SELECT context.sentence FROM context
                                    JOIN link ON context.id = link.sentence_id
                                    JOIN voco ON voco.id = link.word_id
                                    WHERE voco.word =?""", w)
                for sent in l_sent:
                    if sent != ' ':
                        word_sent = f"{w}: {sent['sentence']}"
                        used_list.append(word_sent)
            return used_list


@app.route("/sentence", methods=["GET", "POST"])
def sentence():
    sentence = session["sentence"]
    question = session["question"]
    context = session["context"]
    if request.method == "POST":

        answer = request.form.get("answer")
        result = check_answers(sentence, question, context, answer)

        if result == "Correct":
            return render_template("result.html", correct=result)
        else:
            return render_template("result.html", incorrect=result)

    return render_template("sentence.html", sentence=sentence, question=question)

@app.route("/history", methods=["GET", "POST"])
def history():
    used = db.execute("SELECT voco.word, context.sentence FROM voco JOIN link ON voco.id = link.word_id JOIN context ON context.id = link.sentence_id")
    return render_template("history.html", used=used)



