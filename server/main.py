import threading
import json
from flask_socketio import SocketIO
from flask import Flask, request

app = Flask(__name__)
socketio = SocketIO(app)


class TimerList:
    def __init__(self) -> None:
        self.l = []

    def append(self, v):
        idx = len(self.l)
        self.l.append(v)
        threading.Timer(3660, self.remove, args=(v,)).start()

    def remove(self, v):
        self.l.remove(v)

    def __iter__(self):
        self._idx = 0
        return self

    def __next__(self):
        if self._idx < len(self.l):
            v = self.l[self._idx]
            self._idx += 1
            return v
        else:
            raise StopIteration


shop_users = {"s1": TimerList()}
for u in [
    {
        "avatarUrl": "https://gravatar.com/avatar/e352769376aed6577e8142f7cbd518db?s=400&d=robohash&r=x",
        "nickName": "tom",
    },
    # {
    #     "avatarUrl": "https://gravatar.com/avatar/5ead1bfde756bd693435fde2e39631e3?s=400&d=robohash&r=x",
    #     "nickName": "pop",
    # },
    # {
    #     "avatarUrl": "https://robohash.org/8b5e38be4eb8e5204686a9ff10b91acb?set=set4&bgset=&size=400x400",
    #     "nickName": "ax",
    # },
    # {
    #     "avatarUrl": "https://robohash.org/f02d530fa285506c2ea14919882914f4?set=set4&bgset=&size=400x400",
    #     "nickName": "cat",
    # },
]:
    shop_users["s1"].append(u)


# @socketio.on("connect")
# def handle_connect():
#     print("----connect websocket")


@app.route("/shop_users")
def get_shop_users():
    shop_id = request.args.get("shop")
    return list(shop_users.get(shop_id, TimerList()))


@app.route("/join_shop", methods=["POST"])
def post_join_shop_users():
    shop_id = request.args.get("shop")
    shop_users.get(shop_id, TimerList()).append(request.json)

    socketio.emit(shop_id, list(shop_users[shop_id]))
    return list(shop_users[shop_id])


@app.route("/test")
def test_ws():
    socketio.emit("e1", json.dumps({"a": "1", "b": 23}))
    return "wer"


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8086, debug=True, use_reloader=True)
