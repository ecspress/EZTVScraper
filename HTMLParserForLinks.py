from html.parser import HTMLParser


class Link:
    """Stores data regarding the tag <a> in HTML."""

    def __init__(self):
        self.data = None
        self.attributes = dict()

    def add_data(self, data):
        """Stores the text of <a> tag.

        Input:
            text between start and end of <a> tag.

        Output:
            None

        Raises:
            None
        """
        self.data = data

    def add_attribute(self, attributeName, attributeValue):
        """Stores the attributes of <a> tag in a dictionary.

        Input:
            AttributeName, AttributeValue

        Output:
            None

        Raises:
            None
        """
        self.attributes[attributeName] = attributeValue


class HTMLParserForLinks(HTMLParser):
    """Parses <a> tags in HTML"""

    def __init__(self):
        HTMLParser.__init__(self)

    def parse(self, data):
        """Initializes and resets the parser.

        Input:
            data to be parsed

        Output:
            None

        Raises:
            None
        """
        self.links = []
        self.currentLink = None
        self.reset()
        self.feed(data)

    def handle_starttag(self, tag, attrs):
        """Handles the start of a tag.

        Input:
            tagName, attributes of the tag as tuples(key, value)

        Output:
            None

        Raises:
            None
        """
        if tag == "a":
            self.currentLink = Link()
            for attribute in attrs:
                self.currentLink.add_attribute(attribute[0], attribute[1])

    def handle_endtag(self, tag):
        """Handles the end of a tag.

        Input:
            tagName

        Output:
            None

        Raises:
            None
        """
        if tag == "a":
            self.links.append(self.currentLink)
            self.currentLink = None

    def handle_data(self, data):
        """Handles the text of a tag.

        Input:
            text of tag

        Output:
            None

        Raises:
            None
        """
        if self.currentLink:
            self.currentLink.add_data(data)


if __name__ == "__main__":
    parser = HTMLParserForLinks()
    parser.parse('<fes>some text</fes><a href="www"><t>,</t>linkkkk</a>')
    for link in parser.links:
        print(link.attributes, link.data)

