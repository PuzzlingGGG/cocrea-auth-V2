import random
import string
import requests
from flask import Flask, render_template, request, session, redirect, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gtfhjusjkhdernfbl,o.mserxaol;kdm,fjn.itedaslmkinjb,ugf'

codes = {} # this SUCKS!! change it later! like uh... get a ACTUAL DB!!!

CREATION_ID = '1766942744927846401'

def generate_temp_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def verify_code(code):
    url = f'https://api.cocrea.world/creation-comments?creationId={CREATION_ID}&page=1&perPage=20&sortField=id&sortType=DESC'
    response = requests.get(url)
    if response.status_code == 200:
        comments = response.json().get('body', {}).get('data', [])
        for comment in comments:
            content = comment.get('content')
            if code in content:
                return comment
    return None

@app.route('/', methods=['GET', 'POST'])
def home():
    generated_code = None
    user_info = None
    url = request.args.get('url')
    verification_message = None
    if request.method == 'POST':
        if 'generate' in request.form:
            generated_code = generate_temp_code()
            session['generated_code'] = generated_code
            codes[generated_code] = None
        elif 'verify' in request.form:
            code = request.form['code']
            if code != session.get('generated_code'):
                verification_message = 'Invalid code for this session!' # erm acktually
            else:
                comment = verify_code(code)
                if comment:
                    user_info = {
                        'username': comment['commenter']['username'],
                        'bio': comment['commenter']['bio'],
                        'avatar': comment['commenter']['avatar'],
                        'commenter_id': comment['commenterId'],
                        'comment_id': comment['id']
                    }
                    codes[code] = user_info
                else:
                    verification_message = 'Code not found! Are you sure you did it right?'
    return render_template('home.html', generated_code=session.get('generated_code'), user_info=user_info, url=url, verification_message=verification_message)

@app.route('/continue')
def continue_page():
    code = request.args.get('code')
    url = request.args.get('url')
    user_info = codes.get(code)
    if user_info:
        return redirect(f'{url}?code={code}')
    return "Invalid or expired code." # yap yap yap

@app.route('/api/generate', methods=['GET'])
def api_generate():
    code = generate_temp_code()
    return jsonify({'code': code})

@app.route('/api/verify', methods=['POST'])
def api_verify():
    data = request.json
    code = data.get('code')
    if not code:
        return jsonify({'error': 'Code is required'}), 400
    comment = verify_code(code)
    if comment:
        return jsonify({
            'username': comment['commenter']['username'],
            'bio': comment['commenter']['bio'],
            'avatar': comment['commenter']['avatar'],
            'commenter_id': comment['commenterId'],
            'comment_id': comment['id']
        })
    return jsonify({'error': 'Code not found'}), 404

@app.route('/api/user_info', methods=['GET'])
def api_user_info():
    code = request.args.get('code')
    user_info = codes.get(code)
    if user_info:
        return jsonify(user_info)
    return jsonify({'error': 'Invalid or expired code'}), 404 # shitty

if __name__ == '__main__':
    app.run(debug=True)
