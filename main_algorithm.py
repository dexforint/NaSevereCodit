from autocorrect import Speller
import re

speller1 = Speller('ru')
email_pattern = r'(([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+)'
quotation_pattern1 = r'(?<=«)([^«»]+)(?=»)'
quotation_pattern2 = r'"([^"]+)"' 
site_pattern = re.compile(r'(\b(?<!@)(?<=http://)?(?<=https://)?(?<=www\.)?[a-z]+\.(ru|com|org))', re.IGNORECASE)

def spell1(text):
    return speller1(text)

def empty(text):
    return text

spell = spell1

def get_html(splits):
    if all([split[-1] != ":" and split[0].islower() for split in splits]):
        html = "<ul>"
        for split in splits:
            html = html + "<li>" + split + "</li>"
        html = html + "</ul>"
        return html

    html = ""
    is_list = False
    for split in splits:
        if is_list:
            if split[-1] == ":":
                html = html + "</ul>" + "<p>" + spell(split) + "</p><ul>"

            else:
                if split.lower().startswith("если"):
                    is_list = False
                    html = html + "<p>" + spell(split) + "</p>"
                elif len(re.findall(r"[А-Яа-я]{4,}\.[А-Яа-я]{4,}", split)) > 2:
                    subsplits = re.split(r"(?<=[А-Яа-я]{1,1})\.(?=[А-Яа-я]{2,2})", split)
                    for subsplit in subsplits:
                        html = html + "<li>" + spell(subsplit) + "</li>"
                else:
                    html = html + "<li>" + spell(split) + "</li>"
        else:
            if split[-1] == ":":
                is_list = True
                html = html + "<p>" + spell(split) + "</p><ul>"
            else:
                if split[0] in letters and split[0].islower():
                    html = html + "<ul><li>" + spell(split) + "</li></ul>"
                else:
                    html = html + "<p>" + spell(split) + "</p>"

    if is_list:
        html = html + "</ul>"

    digit_counter = len(re.findall(">\d\.", html))

    html = re.sub(r"</ul><ul>", "", html)

    if digit_counter > 1:
        html = re.sub(r"<ul>", "<ol>", html)
        html = re.sub(r"</ul>", "</ol>", html)
        html = re.sub(r"\d\.", "", html)

    html = re.sub(email_pattern, r"<a href='mailto:\1'>\1</a>", html)
    html = re.sub(quotation_pattern1, r"<b>\1</b>", html)
    html = re.sub(quotation_pattern2, r'"<b>\1</b>"', html)
    html = re.sub(site_pattern, r"<a href='https://www.\1'>\1</a>", html)
    return html

def text_spliting(text):
    text = re.sub(r'"+', '"', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'"$', '', text)
    text = re.sub(r'\n+', '\n', text)

    text = text.strip()
    text = " " + text + " "
    splits = []
    buffer = [text[1]]
    for i in range(2, len(text) - 1):
        symbol = text[i]
        prev_symbol = text[i - 1]
        prev_prev_symbol = text[i - 2]
        next_symbol = text[i + 1]

        symbol_is_letter = symbol in letters
        prev_symbol_is_letter = prev_symbol in letters
        symbol_is_upper = symbol.isupper()
        prev_symbol_is_upper = prev_symbol.isupper()

        if symbol in english_letters and prev_symbol in english_letters:
            buffer.append(symbol)
            continue

        if symbol == "/" or prev_symbol == "/":
            buffer.append(symbol)
            continue

        if symbol == "\n":
            if len(buffer) > 0:
                splits.append("".join(buffer))
                
            buffer = []
            continue

        if symbol == ";":
            if len(buffer) > 0:
                buffer.append(symbol)
                splits.append("".join(buffer))
            buffer = []
            continue

        if prev_symbol == ")" and not symbol in s2:
            if len(buffer) > 0:
                splits.append("".join(buffer))
            buffer = [symbol]
            continue

        if symbol == ':' and not (prev_symbol in digits and next_symbol in digits) and next_symbol != " ":
            if len(buffer) > 0:
                buffer.append(symbol)
                splits.append("".join(buffer))
            buffer = []
            continue

        if symbol_is_letter and prev_symbol_is_letter:
            if symbol_is_upper and not prev_symbol_is_upper:
                if len(buffer) > 0:
                    splits.append("".join(buffer))
                buffer = [symbol]
                continue

        
        if symbol in russian_letters and not prev_symbol_is_letter and prev_symbol not in s1:
            if symbol_is_upper and not prev_symbol_is_upper:
                if len(buffer) > 0:
                    splits.append("".join(buffer))
                buffer = [symbol]
                continue

        if prev_symbol == '"':
            if not symbol in s2 and text[i - 2] != " " and text[i - 2] != "\n":
                if len(buffer) > 0:
                    splits.append("".join(buffer))
                buffer = [symbol]
                continue

        if prev_symbol == '»':
            if not symbol in s2:
                if len(buffer) > 0:
                    splits.append("".join(buffer))
                buffer = [symbol]
                continue

        if symbol in digits and prev_symbol in letters:
            if len(buffer) > 0:
                splits.append("".join(buffer))
            buffer = [symbol]
            continue

        if (symbol in russian_letters and prev_symbol in english_letters) or (symbol in english_letters and prev_symbol in russian_letters):
            if len(buffer) > 0:
                splits.append("".join(buffer))
            buffer = [symbol]
            continue

        if symbol == '«':
            if not prev_symbol in s2:
                if len(buffer) > 0:
                    splits.append("".join(buffer))
                buffer = [symbol]
                continue

        buffer.append(symbol)
    
    if len(buffer) > 1:
        splits.append("".join(buffer))

    splits = [split.strip() for split in splits]
    splits = [re.sub("^ {,}- {,}", "", split) for split in splits]
    splits = [split for split in splits if len(split) > 0]
    return splits

if __name__ == '__main__':
    raw_text = input("Введите текст")
    splits = text_spliting(raw_text)
    pred_text = get_html(splits)
    
    print("Форматированный текст:\n", pred_text)
