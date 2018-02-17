from flask import Flask, send_from_directory
from flask import request
import json
import sys
import random
import time
from time import gmtime, strftime
import numpy as np

try:
    time.tzset()
except:
    pass

colors = [
    "#e6194b",
    "#3cb44b",
    "#ffe119",
    "#0082c8",
    "#f58231",
    "#911eb4",
    "#46f0f0",
    "#f032e6",
    "#d2f53c",
    "#fabebe",
    "#008080",
    "#e6beff",
    "#aa6e28",
    "#fffac8",
    "#800000",
    "#aaffc3",
    "#808000",
    "#ffd8b1",
    "#000080",
    "#808080"
]
color_counter = 0
names = [_[:-1].lower() for _ in open("./names.txt")]
count = 0
messages_file = "./temp_messages.npy"


app = Flask(__name__)


# send -> recieve a message on server
# get_messages (id)-> sends all mesages after an id
# register(username) -> create a new user name
# log out -> delete given username
usernames = {}
messages = []

try:
    messages = np.load(messages_file).tolist()
except:
    pass


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
def root():
    return send_from_directory('build', 'index.html')

@app.route('/app')
def app_root():
    return send_from_directory('build', 'index.html')

@app.route('/register', methods=['POST'])
def register():  ## {username: ""}
    global color_counter
    print_("register")
    print_(usernames)

    userinfo = request.json
    print_(userinfo)

    username = userinfo['username']
    username = username.replace(" ", "").lower()

    if username in names:
        return json.dumps({'status': 'fail'})

    if username != "" and username not in usernames.keys():
        try:
            color = colors[color_counter]
        except:
            color = colors[0]

        color_counter += 1
        if color_counter == len(colors):
            color_counter = 0

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

        np.save(messages_file, messages)

        return json.dumps({'status': 'success'})

    else:
        return json.dumps({'status': 'fail'})


@app.route('/get_message', methods=['POST'])
def get_message():  ## {id: 12}
    print_("get_messages")

    id = request.json['id']
    if len(messages) == 0:
        return json.dumps({'status': 'success', "id":-1, "messages":[], "usercount": len(usernames.keys())})
    else:
        return json.dumps({'status': 'success', "id": messages[-1]['id'], "messages": getMessagesAfterID(id), "usercount": len(usernames.keys())})


@app.route('/logout', methods=['POST'])
def logout():  ## {id: 12}
    print_("logout")
    print_(usernames)

    userinfo = request.json
    print_(userinfo)

    username = userinfo['username']
    username = username.replace(" ", "").lower()

    if username != "" and username in usernames.keys():
        usernames.pop(username)

    return json.dumps({'status': 'success', 'color': "", 'id': -1, 'username':""})


if __name__ == "__main__":
    app.run("0.0.0.0", 19001, debug=False)
