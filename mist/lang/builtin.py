import re
import json
import xml.etree.ElementTree as ET

from dataclasses import dataclass

from jsonpath_ng import parse

from mist.sdk import get_id, stack, config, execution


@dataclass
class BuiltExec:
    parent: object
    command: str
    params: list
    commands: list

    def run(self):
        command = self.command.format(**{
            p.key: p.value
            for p in self.params
        })

        if config.debug:
            print( f"-> Exec '{command}'")

        with execution(command) as (executor, in_files, out_files):

            with executor as console_lines:
                if config.real_time and config.console_output:
                    for line in console_lines:
                        print(line)

            stack.append({
                "result": executor.status_text(),
                "resultCode": executor.status(),
                "consoleOutput": executor.console_output(),
                "consoleError": executor.stderr_output()
            })

        for c in self.commands:
            c.run()
        stack.pop()

@dataclass
class BuiltSearchInText:
    parent: object
    regex: str
    text: str
    commands: list

    def run(self):
        text = get_id(self.text)

        if config.debug:
            print( f"-> SearchInText '{self.regex}'")

        found = "False"
        try:
            if re.search(self.regex, text):
                found = "True"

            result = "Success"
        except Exception as e:
            print(f" Error in 'BuiltSearchInText' -> {e}")
            result = "Error"

        stack.append({
            "regex": self.regex,
            "text": text,
            "result": result,
            "found": found
        })
        for c in self.commands:
            c.run()
        stack.pop()

@dataclass
class BuiltSearchInXML:
    parent: object
    xpath: str
    text: str
    commands: list

    def run(self):
        text = get_id(self.text)

        if config.debug:
            print( f"-> SearchInXML '{self.xpath}'")

        try:
            root = ET.fromstring(text)
            found = root.find(self.xpath)
        except Exception as e:
            found = None
            print(f" Error in 'BuiltSearchInXML' -> {e}")

        stack.append({
            "xpath": self.xpath,
            "text": text,
            "result": "Success" if found else "Error",
            "found": "True" if found else "False",
            "value": found.text if found else "None"
        })
        for c in self.commands:
            c.run()
        stack.pop()

@dataclass
class BuiltSearchInJSON:
    parent: object
    jsonpath: str
    text: str
    commands: list

    def run(self):
        text = get_id(self.text)

        if config.debug:
            print( f"-> SearchInJSON '{self.jsonpath}'")

        try:
            json_data = json.loads(text)
            jsonpath_expression = parse(self.jsonpath)
            found = jsonpath_expression.find(json_data)
        except Exception as e:
            found = None
            print(f" Error in 'BuiltSearchInJSON' -> {e}")

        stack.append({
            "xpath": self.jsonpath,
            "text": text,
            "result": "Success" if found else "Error",
            "found": "True" if found else "False",
            "value": found.value if found else "None"
        })
        for c in self.commands:
            c.run()
        stack.pop()

exports = [BuiltExec, BuiltSearchInText, BuiltSearchInXML, BuiltSearchInJSON]