from flask import Flask, render_template
from bountybotuniqueattestations import query_graphql

app = Flask(__name__)

# CONFIGURACION
app.secret_key = 'mysecretkey'

@app.route('/')
def Index():
    data = query_graphql()
    
    return render_template('index.html', wallets = data)

if __name__ == '__main__':
    app.run(debug=False)
