from html.parser import HTMLParser


class Link:

    def __init__(self, tag):
        self.tag = tag
        self.data = None
        self.attributes = dict()

    def addData(self, data):
        self.data = data

    def addAttribute(self, attributeName, attributeValue):
        self.attributes[attributeName] = attributeValue


class HTMLParserForLinks(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []
        self.currentLink = None

    def parse(self, data):
        self.links = []
        self.currentLink = None
        self.reset()
        self.feed(data)

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.currentLink = Link(tag)
            for attribute in attrs:
                self.currentLink.addAttribute(attribute[0], attribute[1])

    def handle_endtag(self, tag):
        if tag == "a":
            self.links.append(self.currentLink)
            self.currentLink = None

    def handle_data(self, data):
        if self.currentLink:
            self.currentLink.addData(data)


if __name__ == "__main__":
    parser = HTMLParserForLinks()
    parser.parse('<fes>some text</fes><a href="www">linkkkk</a>')
    for link in parser.links:
        print(link.tag, link.attributes, link.data)

