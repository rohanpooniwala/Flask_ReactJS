from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from flask import request
import json
import sys
import random
from time import gmtime, strftime

colors = ["#%06x" % random.randint(0, 0xFFFFFF) for _ in range(20)]

app = Flask(__name__)

CORS(app)

count = 0

# send -> recieve a message on server
# get_messages (id)-> sends all mesages after an id
# register(username) -> create a new user name
# log out -> delete given username
usernames = {}
messages = []


def get_time():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())


def getID():
    ids = [user['id'] for user in messages]
    ran_id = random.randint(0, 10000000)
    while ran_id in ids:
        ran_id = random.randint(0, 10000000)
    return ran_id


def getMessagesAfterID(id):
    print_(id)
    if id == -1:
        return messages[-100:]

    index = [messages.index(_) for _ in messages if _['id'] == id]

    if len(index) == 0:
        return []

    return messages[index[0] + 1:]


def print_(_):
    print(_, file=sys.stdout)


@app.route('/')
def hello_world():
    global count
    # return 'http://192.168.0.2:1212/get_image'
    return send_from_directory('build', 'index.html')


@app.route('/register', methods=['POST'])
def register():  ## {username: ""}
    print_("register")
    print_(usernames)

    userinfo = request.json
    print_(userinfo)

    username = userinfo['username']

    if username != "" and username not in usernames.keys():
        color = random.choice(colors)
        usernames[username] = color
        return json.dumps({'status': 'success', 'color': color, 'id': -1, 'username':username})
    else:
        print_("Username already exist " + str(username))
        return json.dumps({'status': 'fail'})


@app.route('/send_message', methods=['POST'])
def send_message():  ## {username: "", message:""}
    print_("send_message")

    message = request.json
    print(request.json)
    username = message['username']

    print_('message' in message.keys())

    if (username in usernames.keys()) and ('message' in message.keys()):
        if message['message'] == '':
            return json.dumps({'status': 'fail'})

        prev_id = -1 if (len(messages) == 0) else messages[-1]['id']
        messages.append({
            'id': getID(),
            'message': message['message'],
            'time': get_time(),
            'username': username,
            'color': usernames[username]
        })
        return json.dumps({'status': 'success'})

    else:
        return json.dumps({'status': 'fail'})


@app.route('/get_message', methods=['POST'])
def get_message():  ## {id: 12}
    print_("get_messages")

    id = request.json['id']
    if len(messages) == 0:
        return json.dumps({'status': 'success', "id":-1, "messages":getMessagesAfterID(id)})
    else:
        return json.dumps({'status': 'success', "id": messages[-1]['id'], "messages": getMessagesAfterID(id)})


@app.route('/logout', methods=['POST'])
def logout():  ## {id: 12}
    print_("logout")
    print_(usernames)

    userinfo = request.json
    print_(userinfo)

    username = userinfo['username']

    if username != "" and username in usernames.keys():
        usernames.pop(username)

    return json.dumps({'status': 'success', 'color': "", 'id': -1, 'username':""})


if __name__ == "__main__":
    app.run("0.0.0.0", 19001, debug=False)
