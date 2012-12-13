from django.template import VARIABLE_TAG_END, VARIABLE_TAG_START
import re

def parse(text):
    tag_re = (re.compile('(%s.*?%s)' % (re.escape(VARIABLE_TAG_START), re.escape(VARIABLE_TAG_END))))
    parameter_list = []

    for bit in tag_re.split(text):
        if bit.startswith(VARIABLE_TAG_START) and bit.endswith(VARIABLE_TAG_END):
            parameter = bit[2:-2].strip()
            if parameter not in parameter_list and re.match("^[A-Za-z0-9_.]*$", parameter):
                parameter_list.append(parameter)

    return parameter_list