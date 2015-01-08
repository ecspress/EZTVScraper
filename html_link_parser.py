"""Parses and finds all the links in an html document"""
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

    def add_attribute(self, attribute_name, attribute_value):
        """Stores the attributes of <a> tag in a dictionary.

        Input:
            AttributeName, AttributeValue

        Output:
            None

        Raises:
            None
        """
        self.attributes[attribute_name] = attribute_value


class HTMLLinkParser(HTMLParser):
    """Parses <a> tags in HTML"""

    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []
        self.current_link = None

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
        self.current_link = None
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
            self.current_link = Link()
            for attribute in attrs:
                self.current_link.add_attribute(attribute[0], attribute[1])

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
            self.links.append(self.current_link)
            self.current_link = None

    def handle_data(self, data):
        """Handles the text of a tag.

        Input:
            text of tag

        Output:
            None

        Raises:
            None
        """
        if self.current_link:
            self.current_link.add_data(data)

def test_main():
    """Tests the current module"""
    parser = HTMLLinkParser()
    parser.parse('<fes>some text</fes><a href="www"><t>,</t>linkkkk</a>')
    for link in parser.links:
        print(link.attributes, link.data)


if __name__ == "__main__":
    test_main()
