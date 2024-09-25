import os
from flask import Flask, redirect, url_for, session, request, render_template
from authlib.integrations.flask_client import OAuth
from main import oauthRegister, User
from decouple import config

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'

# Carregando CLIENT_ID e CLIENT_SECRET do arquivo .env
client_id = config("CLIENT_ID")
client_secret = config("CLIENT_SECRET")

# Configurando OAuth
oauth = OAuth(app)
oauthRegister(oauth, 
              name="suap", 
              api_base_url="https://suap.ifrn.edu.br/api/", 
              request_token_url=None, 
              access_token_method="POST", 
              access_token_url="https://suap.ifrn.edu.br/o/token/", 
              authorize_url="https://suap.ifrn.edu.br/o/authorize/", 
              token="suap_token")

# Rota principal (Index)
@app.route('/')
def index():
    if 'suap_token' in session:
        user = User(oauth)
        data = user.get_user_dados()  # Alterado para o método correto
        return render_template('profile.html', user_info=data.json())
    else:
        return render_template('index.html')

# Rota de login
@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)  # Esta deve gerar http://localhost:5000/login/authorized
    print(f"Redirecionando para: {redirect_uri}")  # Log para depuração
    return oauth.suap.authorize_redirect(redirect_uri)


# Rota de logout
@app.route('/logout')
def logout():
    session.pop('suap_token', None)
    return redirect(url_for('index'))

# Rota de autorização (callback após login OAuth)
@app.route('/login/authorized')
def auth():
    try:
        token = oauth.suap.authorize_access_token()
        session['suap_token'] = token
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Erro ao autorizar acesso: {e}")
        return redirect(url_for('index'))

# Rota para visualização de boletins
@app.route("/boletins", methods=["GET", "POST"])
def boletins():
    if 'suap_token' in session:
        user = User(oauth)
        if request.method == "POST":
            ano = request.form['ano']
            semestre = request.form['semestre']
            data = user.get_user_boletim(ano, semestre)
            return render_template("boletins.html", boletins=data.json(), ano=ano, semestre=semestre) 
        return render_template("select_boletins.html")
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
