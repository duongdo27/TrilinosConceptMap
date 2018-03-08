import requests
from lxml import html
import json
from random import shuffle

class CommentReader(object):
    def __init__(self, data_filename):
        self.data_filename = data_filename

    @staticmethod
    def read_one_file(filename):
        is_comment = False
        all_data = []
        data = {}
        with open(filename, 'r') as f:
            lines = f.readlines()

        for line in lines:
            # Read title
            line = line.strip()
            if line.endswith(".cpp") and not is_comment:
                data["name"] = line

            # Read comments
            elif line.startswith("/*---"):
                is_comment = True
            elif line.startswith("Categories"):
                data["Categories"] = [x.strip() for x in line.split(":")[1].split(",")]
            elif line.startswith("Topics"):
                data["Topics"] = [x.strip() for x in line.split(":")[1].split(",")]
            elif line.startswith("Prerequisites"):
                data["Prerequisites"] = [x.strip() for x in line.split(":")[1].split(",")]
            elif line.endswith("*/"):
                is_comment = False
                all_data.append(data.copy())
        return all_data

    def run(self):
        data = self.read_one_file("Metadatablock.txt")

        with open(self.data_filename, "w") as f:
            f.write(json.dumps(data))


class ColorPicker(object):
    def __init__(self, filename):
        self.filename = filename

    @staticmethod
    def check_good_color(color_hex):
        assert len(color_hex) == 7 and color_hex.startswith('#')
        red = int(color_hex[1:3], 16)
        green = int(color_hex[3:5], 16)
        blue = int(color_hex[5:7], 16)
        delta = 20
        return abs(red-green) > delta or abs(blue-green) > delta or abs(blue-red) > delta

    def get_all_colors(self):
        url = "http://www.graphviz.org/doc/info/colors.html"
        res = requests.get(url)
        tree = html.fromstring(res.text)

        ls = []
        color_elements = tree.xpath('//table[2]//a')
        for color_element in color_elements:
            try:
                color_name = color_element.xpath('./text()')[0].replace(u'\xa0', '')
                color_hex = color_element.xpath('./@title')[0]
                if self.check_good_color(color_hex):
                    ls.append(color_name)
            except IndexError:
                pass
        return ls

    def run(self):
        colors = self.get_all_colors()
        print 'Read {} files'.format(len(colors))

        with open(self.filename, "w") as f:
            f.write(json.dumps(colors))


class GraphGenerator(object):
    def __init__(self, data_filename, color_filename, output_filename, group_by):
        self.data_filename = data_filename
        self.color_filename = color_filename
        self.output_filename = output_filename
        self.group_by = group_by

    def write_graphviz(self, data, colors):
        result = """digraph bettersoftware {
            rankdir = LR;
            ratio = fill;
            node [style=filled];
            node [shape = box];\n"""

        cnt = 0
        cache_lookup = {}
        for line in data:
            if self.group_by not in line:
                continue

            if type(line[self.group_by]) == list:
                groups = line[self.group_by]
            else:
                groups = [line[self.group_by]]
            for group in groups:
                group = group.lower()
                if group in cache_lookup:
                    color = cache_lookup[group]
                else:
                    color = colors[cnt]
                    cnt += 1
                    cache_lookup[group] = color
                    result += '"{}" [colorscheme="svg" color="{}"];\n'.format(group, color)
                result += '"{}" ->  "{}" [colorscheme="svg" color="{}"];\n'.format(group, line["name"], color)
        result += "}"
        return result

    def run(self):
        with open(self.color_filename) as f:
            colors = json.loads(f.read())
        shuffle(colors)

        with open(self.data_filename) as f:
            data = json.loads(f.read())

        text = self.write_graphviz(data, colors)
        with open(self.output_filename, "w") as f:
            f.write(text)


class Graph1Generator(object):
    def __init__(self, data_filename, color_filename, output_filename, group_by):
        self.data_filename = data_filename
        self.color_filename = color_filename
        self.output_filename = output_filename
        self.group_by = group_by

    def write_graphviz(self, data, colors):
        result = """digraph bettersoftware {
            ratio = fill;
            node [style=filled];
            node [shape = box];\n"""

        cnt = 0
        cache_lookup = {}
        for line in data:
            if self.group_by not in line:
                continue

            if type(line[self.group_by]) == list:
                groups = line[self.group_by]
            else:
                groups = [line[self.group_by]]
            for group in groups:
                if group in cache_lookup:
                    color = cache_lookup[group]
                else:
                    color = colors[cnt]
                    cnt += 1
                    cache_lookup[group] = color
                    result += '"{}" [colorscheme="svg" color="{}"];\n'.format(group, color)
                result += '"{}" ->  "{}" [colorscheme="svg" color="{}"];\n'.format(group, line["name"], color)
        result += "}"
        return result

    def run(self):
        with open(self.color_filename) as f:
            colors = json.loads(f.read())
        shuffle(colors)

        with open(self.data_filename) as f:
            data = json.loads(f.read())

        text = self.write_graphviz(data, colors)
        with open(self.output_filename, "w") as f:
            f.write(text)


def graphiz_generator():
    color_filename = 'color.json'
    data_filename = 'data.json'
    #data_filename = 'data1.json'
    #ColorPicker(color_filename).run()
    CommentReader(data_filename).run()

    #GraphGenerator(data_filename, color_filename,
    #               "topics.dot", "Topics").run()
    #GraphGenerator(data_filename, color_filename,
    #               "categories.dot", "Categories").run()
    Graph1Generator(data_filename, color_filename,
                   "prerequisites.dot", "Prerequisites").run()


if __name__ == '__main__':
    graphiz_generator()
