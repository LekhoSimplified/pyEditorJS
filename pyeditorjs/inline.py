from html.parser import HTMLParser


class MyHTMLParser(HTMLParser):
    mithril_js = ''

    def handle_starttag(self, tag, attrs):
        href = None

        if (len(attrs) == 1):
            if (len(attrs[0]) == 2):
                if (attrs[0][0] == 'href'):
                    href = attrs[0][1]

        if (href is None):
            self.mithril_js += f"m('{tag}', ["
        else:
            self.mithril_js += f"m('{tag}', {{'href': `{href}`}}, ["
        # print("Encountered a start tag:", tag)

    def handle_endtag(self, tag):
        self.mithril_js += "]),"
        # print("Encountered an end tag :", tag)

    def handle_data(self, data):
        lines = data.split("<br>")
        self.mithril_js += "`" + "`,m('br'),`".join(lines) + "`,"
        # print("Encountered some data  :", data, self.mithril_js)

def mithril(data):
    parser = MyHTMLParser()
    parser.feed(data)
    # print("inline:", parser.mithril_js)
    return parser.mithril_js