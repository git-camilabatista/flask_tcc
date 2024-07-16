from flask import Flask

app = Flask(__name__)

dict_item = {
    'key1': 'item 1',
    'key2': 'item 2',
}

@app.route('/items/<item_id>')
def show_item(item_id):
    return {'results': dict_item[item_id]}