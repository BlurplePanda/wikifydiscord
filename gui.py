import tkinter as tk
import tkinter.scrolledtext as st
import tkinter.messagebox as mb
from wikify_module import *

load_emoji_map()


def submit():
    unknown_emojis.clear()
    unknown_users.clear()
    unknown_channels.clear()

    input_text = input_textbox.get("1.0", tk.END)  # 1.0 is line 1 col 0 or beginning (tk.END is end)
    result = wikify(input_text)
    output_textbox.delete("1.0", tk.END)
    output_textbox.insert(tk.END, result)

    output_textbox.tag_config("warn", background="red", font=("TkDefaultFont", 9, "bold"))

    full_output = output_textbox.get("1.0", tk.END)
    for match in re.finditer(r"\[⚠️ UNKNOWN (?:EMOJI|USER|CHANNEL): [^\]]+\]", full_output):
        start = f"1.0 + {match.start()}c"
        end = f"1.0 + {match.end()}c"
        output_textbox.tag_add("warn", start, end)

    if unknown_emojis or unknown_users or unknown_channels:
        mb.showwarning("Unknown embeds",
                       "\n⚠️ The following emojis/channels/pings will need to be manually modified:\n"
                       + "\n".join(unknown_emojis + unknown_users + unknown_channels))


def copy_output():
    output = output_textbox.get("1.0", tk.END)
    gui.clipboard_clear()
    gui.clipboard_append(output)


if __name__ == '__main__':
    emoji_map = load_emoji_map()
    print(emoji_map)
    gui = tk.Tk()
    gui.title("Discord \"Wikifier\" - made by BlurplePanda/Panda185")
    gui.configure(bg="MediumPurple2")

    input_frame = tk.Frame(gui, bg="#d7b3ed", padx=10, pady=10)
    input_frame.pack(padx=20, pady=20)

    tk.Label(input_frame, text="Paste Discord post below:", bg="#d7b3ed").pack()
    input_textbox = st.ScrolledText(input_frame, width=60, height=10)
    input_textbox.pack(fill="both", expand=True)

    submit_button = tk.Button(input_frame, text="Wikify!", command=submit, bg="LightBlue1")
    submit_button.pack(pady=10)

    output_frame = tk.Frame(gui, bg="#d7b3ed", padx=10, pady=10)
    output_frame.pack(padx=20, pady=20)

    tk.Label(output_frame, text="Wikified Output:", bg="#d7b3ed").pack()
    output_textbox = st.ScrolledText(output_frame, width=60, height=10)
    output_textbox.pack(fill="both", expand=True)

    copy_button = tk.Button(output_frame, text="Copy Output", command=copy_output, bg="LightBlue1")
    copy_button.pack(pady=5)

    gui.mainloop()
