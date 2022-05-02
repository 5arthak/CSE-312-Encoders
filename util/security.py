def secure_html(html):
    comment = ""
    for x in html:
        if x == '&':
            comment += "&amp;"
        elif x == '<':
            comment += "&lt;"
        elif x == '>':
            comment += "&gt;"
        else:
            comment += x
    return comment