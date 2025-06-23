# === UPDATED: MULTIPLE QUIZ QUESTIONS PER LEVEL + RESTART ===
import tkinter as tk
from tkinter import scrolledtext
import tkinter.font as font
import random, re, sys

# ----------------------------
# 🎓 Game Data
# ----------------------------
def initialize_player():
    return {
        "location": "start",
        "inventory": [],
        "quiz1_passed": False,
        "quiz2_passed": False,
        "quiz3_passed": False,
        "quiz4_passed": False,
        "quiz5_passed": False,
        "score": 0
    }

player = initialize_player()

rooms = {
    "start": {
        "description": "You are in a dark dungeon. Exits are north.",
        "items": [],
        "north": "hall"
    },
    "hall": {
        "description": "You are in a grand hall. A sword lies here. Exits are south and east.",
        "items": ["sword"],
        "south": "start",
        "east": "throne"
    },
    "throne": {
        "description": "You enter the throne room. A dragon blocks your way! go east for further!",
        "items": ["dragon"],
        "west": "hall",
        "east": "icg_room"
    },
    "icg_room": {
        "description": "This is the Intermediate Code Generation chamber.go east for further!",
        "items": [],
        "west": "throne",
        "east": "opt_room"
    },
    "opt_room": {
        "description": "You step into the Optimization Room, filled with compiler scrolls.go east for further!",
        "items": [],
        "west": "icg_room",
        "east": "codegen_room"
    },
    "codegen_room": {
        "description": "This is the Code Generation Sanctum. You feel the end is near.",
        "items": [],
        "west": "opt_room"
    }
}

# ----------------------------
# 🧪 Lexer, Parser, Semantic
# ----------------------------
def lexer(command):
    return re.findall(r'\b\w+\b', command.lower())

def parser(tokens):
    if 1 <= len(tokens) <= 2:
        return tokens[0], tokens[1] if len(tokens) == 2 else None
    return None, None

def semantic_analyzer(verb, obj, output, ask_quiz_callback):
    location = player["location"]
    room = rooms[location]

    if verb == "go":
        if obj and obj in room:
            next_room = room[obj]
            if next_room == "hall" and not player["quiz1_passed"]:
                ask_quiz_callback(1, lambda passed: try_move(passed, next_room, output))
                return "wait"
            if next_room == "throne" and not player["quiz2_passed"]:
                ask_quiz_callback(2, lambda passed: try_move(passed, next_room, output))
                return "wait"
            if next_room == "icg_room" and not player["quiz3_passed"]:
                ask_quiz_callback(3, lambda passed: try_move(passed, next_room, output))
                return "wait"
            if next_room == "opt_room" and not player["quiz4_passed"]:
                ask_quiz_callback(4, lambda passed: try_move(passed, next_room, output))
                return "wait"
            if next_room == "codegen_room" and not player["quiz5_passed"]:
                ask_quiz_callback(5, lambda passed: try_move(passed, next_room, output))
                return "wait"
            player["location"] = next_room
            describe_room(output)
        else:
            output(f"🚫 You can't go {obj} from here.")

    elif verb == "look":
        describe_room(output)

    elif verb == "pick":
        if obj and obj in room["items"]:
            room["items"].remove(obj)
            player["inventory"].append(obj)
            output(f"👜 You picked up the {obj}.")
        else:
            output("❌ There's nothing like that to pick up.")

    elif verb == "attack":
        if obj == "dragon":
            if obj in room["items"]:
                if "sword" in player["inventory"]:
                    output("🐉 You slayed the dragon! You may now explore deeper.")
                    rooms["throne"].pop("items")
                else:
                    output("🔥 The dragon incinerates you! Game over.")
                    return "lose"
            else:
                output("❌ There's no dragon here.")
        else:
            output(f"❌ You can't attack {obj}.")
    else:
        output("❓ Unknown command.")
    return "continue"

def try_move(passed, room_name, output):
    if passed:
        qkey = f"quiz{room_name.count('_')+1}_passed"
        player[qkey] = True
        player["location"] = room_name
        describe_room(output)
    else:
        output("❌ You failed the quiz and cannot proceed.")

def describe_room(output):
    room = rooms[player["location"]]
    output(f"📍 {room['description']}")
    if room["items"]:
        output(f"You see: {', '.join(room['items'])}")

all_quizzes = {
    1: [
        ("Which phase removes comments?", ["Syntax", "Lexical", "IR", "CodeGen"], "Lexical"),
        ("Which phase creates tokens?", ["Parser", "Lexer", "Optimizer", "CodeGen"], "Lexer")
    ],
    2: [
        ("Which structure helps in shift-reduce parsing?", ["Stack", "Queue", "Graph", "Tree"], "Stack"),
        ("What is used in bottom-up parsing?", ["First Set", "Follow Set", "Parse Table", "Shift/Reduce"], "Shift/Reduce")
    ],
    3: [
        ("Which is used to represent intermediate code?", ["Quadruples", "Tokens", "AST", "Opcodes"], "Quadruples"),
        ("What does IR stand for?", ["Intermediate Result", "Instruction Return", "Intermediate Representation", "Initial Render"], "Intermediate Representation")
    ],
    4: [
        ("Which is a local optimization technique?", ["Constant folding", "Peephole", "Inlining", "Loop unrolling"], "Peephole"),
        ("Which is global optimization?", ["Inlining", "Loop unrolling", "Dead code elimination", "Common subexpr elimination"], "Common subexpr elimination")
    ],
    5: [
        ("Which maps variables to registers?", ["Register Allocation", "Lexing", "Inlining", "Parsing"], "Register Allocation"),
        ("Which phase emits target machine code?", ["Lexical", "Semantic", "Code Generation", "Syntax"], "Code Generation")
    ],
}

# ----------------------------
# 🖼️ GUI Game Start
# ----------------------------
def start_game():
    global player
    player = initialize_player()

    def print_out(text):
        output_box.config(state="normal")
        output_box.insert(tk.END, text + "\n")
        output_box.config(state="disabled")
        output_box.see(tk.END)

    def ask_quiz(level, callback):
        quiz_frame = tk.Frame(root, bg="#282a36")
        quiz_frame.place(relx=0.5, rely=0.5, anchor="center")
        quiz_data = all_quizzes[level]
        answers = []

        def ask_question(index):
            for widget in quiz_frame.winfo_children():
                widget.destroy()
            if index >= len(quiz_data):
                score = sum(answers)
                quiz_frame.destroy()
                player["score"] += score
                callback(score == len(quiz_data))
                return
            question, options, correct = quiz_data[index]
            tk.Label(quiz_frame, text=f"Q{index+1}: {question}", fg="white", bg="#282a36").pack(pady=5)
            selected = tk.StringVar()
            for opt in options:
                tk.Radiobutton(quiz_frame, text=opt, variable=selected, value=opt, fg="white", bg="#282a36").pack(anchor="w")

            def submit():
                answers.append(selected.get() == correct)
                ask_question(index + 1)

            tk.Button(quiz_frame, text="Submit", command=submit).pack(pady=5)

        ask_question(0)

    def process_command(event=None):
        command = input_field.get().strip()
        input_field.delete(0, tk.END)
        if not command:
            print_out("⚠️ Please enter a command.")
            return
        tokens = lexer(command)
        verb, obj = parser(tokens)
        if not verb:
            print_out("🛑 Syntax error. Use commands like 'look', 'go east'.")
            return
        result = semantic_analyzer(verb, obj, print_out, ask_quiz)
        if result == "lose":
            input_field.config(state="disabled")
            send_btn.config(state="disabled")
            print_out("💀 You lost the game.")
        elif player['location'] == "codegen_room":
            print_out(f"🏁 You reached the end! Final score: {player['score']}/10")
            input_field.config(state="disabled")
            send_btn.config(state="disabled")

    def restart():
        root.destroy()
        start_game()

    root = tk.Tk()
    root.title("🛡️ Compiler Dungeon")
    root.geometry("700x520")
    root.configure(bg="#1e1e2e")

    tk.Label(root, text="🏰 Compiler Dungeon", font=("Georgia", 18, "bold"), fg="#f8f8f2", bg="#1e1e2e").pack(pady=5)
    global output_box
    output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15, font=("Consolas", 12),
                                           bg="#2e2e3a", fg="#f8f8f2", insertbackground="white")
    output_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    output_box.config(state="disabled")

    input_frame = tk.Frame(root, bg="#1e1e2e")
    input_frame.pack(fill=tk.X, padx=10)
    global input_field, send_btn
    input_field = tk.Entry(input_frame, font=("Arial", 12), bg="#2e2e3a", fg="white", insertbackground="white")
    input_field.pack(side=tk.LEFT, fill=tk.X, expand=True)
    input_field.bind("<Return>", process_command)
    send_btn = tk.Button(input_frame, text="Send", bg="#6272a4", fg="white", command=process_command)
    send_btn.pack(side=tk.RIGHT, padx=5)

    restart_btn = tk.Button(root, text="Restart Game", bg="#50fa7b", fg="black", command=restart)
    restart_btn.pack(pady=5)

    print_out("🎮 Welcome to Compiler Dungeon!")
    print_out("Type commands like: 'go north', 'look', 'pick sword', 'attack dragon'.\n")
    describe_room(print_out)

    root.mainloop()

if __name__ == "__main__":
    start_game()
