import pymongo
import random
from flask import Flask, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId

app = Flask('jumbledwords')
app.secret_key = 'supersecretkey'

uri = "mongodb+srv://lauvacat:abcdef12345@cluster0.7fifn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = pymongo.MongoClient(uri, tls=True, tlsAllowInvalidCertificates=True)
db = client.notemanager

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        word = request.form.get('addWord')
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password is not None and confirm_password is not None:
            if password != confirm_password:
                flash('Passwords do not match!')
                return redirect('/')

        if word:
            db.notes.insert_one({'word': word})
            flash("Word added successfully!", "success")
        else:
            flash("Please enter a word!", "danger")
        return redirect(url_for('index'))

    notes = list(db.notes.find())
    return render_template('index.html', notes=notes)

@app.route('/play', methods=['GET', 'POST'])
def play():
    if request.method == 'POST':
        user_answers = {}
        correct_answers = {}
        score = 0

        for key in request.form:
            word_id = key
            user_input = request.form[key].strip().lower()
            word_doc = db.notes.find_one({'_id': ObjectId(word_id)})
            if word_doc:
                correct_word = word_doc['word'].lower()
                user_answers[word_id] = user_input
                correct_answers[word_id] = correct_word
                if user_input == correct_word:
                    score += 1

        return render_template(
            'result.html',
            score=score,
            user_answer=user_answers,
            correct_answer=correct_answers
        )

    words_cursor = list(db.notes.find())
    selected_words = random.sample(words_cursor, min(6, len(words_cursor)))

    jumbled_words = []
    for word_doc in selected_words:
        original_word = word_doc.get("word")
        if original_word:
            jumbled = ''.join(random.sample(original_word, len(original_word)))
            jumbled_words.append({'_id': word_doc['_id'], 'word': jumbled})

    return render_template('play_game.html', jumbledwords=jumbled_words)

if __name__ == '__main__':
    app.run(debug=True)
