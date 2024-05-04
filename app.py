from flask import Flask, render_template, request, session, url_for, redirect
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "Qwerty16"
socketio = SocketIO(app)

rooms = {}


def generate_unique_code(length):
    """
    generating a random code and condition to check if the code already exists,
    because randomness is not completly random,
    if the code exists which is rare then repeat while loop to generate another code,
    if code doesnt not exsist then break WHILE loop and return code 
    """
    while True:
        code = ""
        for i in range(length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break
    
    return code


@app.route("/", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)
    
        if not name:
                return render_template("home.html", error="Please enter name!", code=code, name=name)
            
        if join != False and not code:
            return render_template("home.html", error="Please enter a room code!", code=code, name=name)
            
        room = code
        if create != False:
            # creating a room
            room = generate_unique_code(4)
            rooms[room] = {"members":0, "messages": []}
        elif code not in rooms:
            # if not creating a room then joining a room(wrong code)
            return render_template("home.html", error="Room does not exist!", code=code, name=name)
        
        session["room"] = room
        session["name"] = name

        # if not creating a room and code is correct
        return redirect(url_for("room"))
    
    return render_template("home.html")



@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))
    
    return render_template("room.html")

@socketio.on("connect")
def connect(auth): 
    """ User joining th room"""
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] +=1
    print(f"{name} joined room {room}")


@socketio.on("disconnect")
def disconnect():
    """User leaving the room"""
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <=0:
            del rooms[room]

    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")
    

if __name__ == "__main__":
    socketio.run(app, debug=True)