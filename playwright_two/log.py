from io import TextIOWrapper
from datetime import datetime as dt

class Log:
    def __init__(self, file: TextIOWrapper, test_name: str, output_path: str = 'data', trace_mode: bool = False, screenshots: bool = False) -> None:
        self.file = file
        self.test_name = test_name
        self.output_path = output_path
        self.trace_mode = trace_mode
        self.screenshots = screenshots
        self.sections: list[str] = []
        self.starts: list[dt] = []
        self.on = True

    def start_file(self, title=""):
        """Creates/overwrites log file"""
        if self.on:
            #with open(self.file_name, 'w', encoding='utf-8') as file:
            self.file.write(f"{title}")

    def indent(self):
        if self.on:
            #with open(self.file_name, 'a+', encoding='utf-8') as file:
            for n in range(len(self.sections)):
                self.file.write("    ")

    def w(self, text):
        """ w(rite_log)
            Appends line of text to log file
        """
        if self.on:
            self.indent()
            #with open(self.file_name, 'a+', encoding='utf-8') as file:
            self.file.write(text)
            self.file.write("\n")

    def s(self, title: str):
        """
            s(tart_section)
            Adds indent and indicates start of new section
            Always precedes a call to (e)nd_function
        """
        if self.on:
            self.indent()
            self.sections.append(title)
            self.starts.append(dt.now())
            #with open(self.file_name, 'a+', encoding='utf-8') as file:
            self.file.write(f"START {title}")
            self.file.write("\n")

    def e(self):
        """ e(nd_section)
            Removes indent and indicates end of new section
            Always follows a call to (s)tart_function
        """
        if self.on:
            func = self.sections.pop()
            start = self.starts.pop()
            seconds = (dt.now() - start).seconds + (dt.now() - start).microseconds / 1000000
            self.indent()
            #with open(self.file_name, 'a+', encoding='utf-8') as file:
            self.file.write(f"END {func} ({seconds:.3f}s)\n")

    def section_seconds(self):
        start = self.starts[-1:][0]
        seconds = (dt.now() - start).seconds + (dt.now() - start).microseconds / 1000000
        return round(seconds,3)


