# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import re
import sys
import json
from datetime import datetime, timezone

emoji_map = {}
unknown_emojis = []
user_map = {}
unknown_users = []
channel_map = {}
unknown_channels = []


def wikify(post):
    post = convert_underlines(post)
    post = convert_bold_italic(post)
    post = escape_brackets(post)
    lines = post.splitlines()
    processed_lines = []
    for line in lines:
        processed_lines.append(process_line(line))
    post = '\n'.join(processed_lines)
    post = """<h3 style="visibility: hidden;">pagename [mo-da-ye]</h3>

> ![](/userchangelog.png =40x) <font size="+4">title</font>
> <kbd>:spiral_calendar:Month 0 2025</kbd> | Posted by `ign`
> 
> ---
> 
""" + post
    return post


def convert_underlines(text):
    return re.sub(r"__(.*?)__", r"<u>\1</u>", text, flags=re.DOTALL)


def convert_bold_italic(text):
    return re.sub(r"(\*{1,3})\s*(.*?)\s*\1", r"\1\2\1", text, flags=re.DOTALL)


def escape_brackets(text):
    # find valid markdown links (don't wanna escape those brackets!)
    link_matches = list(re.finditer(r"\[[^\]]*\]\([^\)]*\)", text))  # need to use finditer not findall to get pos
    skip_ranges = [match.span() for match in link_matches]

    def should_escape(index):
        # check if it's in the ranges we shouldn't escape (valid links)
        return not any(start <= index < end for start, end in skip_ranges)

    result = []
    for i, char in enumerate(text):
        if char in "[]":
            if should_escape(i):
                result.append("\\" + char)
            else:
                result.append(char)
        else:
            result.append(char)

    return ''.join(result)


def process_line(line):
    line = convert_headings(line)
    line = convert_emojis(line)
    line = convert_tags(line)
    line = convert_channels(line)
    line = convert_times(line)
    line = "> " + line
    return line


def convert_tags(text):
    text = text.replace("@everyone", "")

    def tag_replacer(match):
        tag = match.group(1)
        if tag in user_map:
            return user_map[tag]
        else:
            unknown_users.append(match.group(0))
            return f"[⚠️ UNKNOWN USER: {match.group(0)}]"  # original text with warning if not found

    text = re.sub(r"<@([&!]?\d+)>", tag_replacer, text)

    # remove events/changelog pings that aren't part of eg "get the `ping events` role in #welcome"
    text = re.sub(r"`@ping (?:changelog|events)`(?![ ]*(?:role|in))", "", text)

    return text


def convert_channels(text):
    def channel_replacer(match):
        channel = match.group(1)
        if channel in channel_map:
            return f"`#{channel_map[channel]}`"
        else:
            unknown_channels.append(match.group(0))
            return f"[⚠️ UNKNOWN CHANNEL: {match.group(0)}]"  # original text with warning if not found

    return re.sub(r"<#(\d+)>", channel_replacer, text)


def convert_headings(line):
    heading_levels = {
        "# ": "<font size=\"+3\">",
        "## ": "<font size=\"+2\">",
        "### ": "",
        "-# ": "<font size=\"-1\" color=\"grey\">"
    }

    for prefix, tag in heading_levels.items():
        if line.startswith(prefix):
            content = line[len(prefix):].strip()

            if prefix != "-# ":
                if not (content.startswith("**") and content.endswith("**")):
                    content = "**" + content + "**"
            if tag:
                return tag + content + "</font>"
            else:
                return content
    return line


def load_emoji_map(path="emoji_map.json"):
    global emoji_map
    with open(path, "r") as f:
        emoji_map = json.load(f)


def convert_emojis(line):
    def emoji_replacer(match):
        emoji_id = match.group(1)
        if emoji_id in emoji_map:
            return f"![](/discord/emojis/{emoji_map[emoji_id]}){{.emoji}}"
        else:
            unknown_emojis.append(match.group(0))
            return f"[⚠️ UNKNOWN EMOJI: {match.group(0)}]"  # original text with warning if not found

    return re.sub(r"<a?:\w+:(\d+)>", emoji_replacer, line)


def convert_times(text):
    def time_replacer(match):
        timestamp = int(match.group(1))
        fmt_code = match.group(2) or 'f'  # default to f if no format specified
        utc_timestamp = datetime.fromtimestamp(timestamp, timezone.utc)
        format_map = {
            'F': "%A, %B %-d, %Y at %-I:%M %p",
            'f': "%B %d, %Y at %I:%M %p",
            'D': "%B %-d, %Y",
            'd': "%m/%d/%y",
            'T': "%-I:%M:%S %p",
            't': "%-I:%M %p"
            # no relative
        }

        fmt = format_map.get(fmt_code, "%B %-d, %Y at %-I:%M %p")  # default to f
        return f"<kbd>{utc_timestamp.strftime(fmt)} [UTC](https://dateful.com/convert/utc)</kbd>"

    text = re.sub(r"<t:(\d+):([a-zA-Z])?>", time_replacer, text)
    return text


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    load_emoji_map()

    print("Discord \"Wikifier\" - made by BlurplePanda/Panda185")
    print("1. Paste Discord post (right click on post -> 'Copy Text' then paste here)\n"
          + "2. Press Enter so you're on a blank line\n"
          + "3. Press Ctrl+D (or Ctrl+Z)\n"
          + "4. Copy the output!")
    post = sys.stdin.read()
    print(wikify(post))
    if unknown_emojis:
        print("\n⚠️ The following emojis' IDs were not found in emoji_map and will need to be manually modified.\n"
              + "They are listed here in order and also emphasised in the above output for convenience (search for 'UNKNOWN EMOJI').")
        print(unknown_emojis)
        for emoji in unknown_emojis:
            print(emoji)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
