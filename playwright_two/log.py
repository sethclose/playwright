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
        self.mode = "on" # "off", "debug"

    def start_file(self, title=""):
        """Creates/overwrites log file"""
        string = f"{title}"
        if self.mode in ("on", "debug"):
            self.file.write(string)
        if self.mode == "debug":
            print(string)

    def indent(self):
        string = "    "
        for n in range(len(self.sections)):
            if self.mode in ("on", "debug"):
                self.file.write(string)
            if self.mode == "debug":
                print(string, end="")

    def w(self, text, last='\n'):
        """ w(rite_log)
            Appends line of text to log file
        """
        self.indent()
        if self.mode in ("on", "debug"):
            self.file.write(text)
            self.file.write(last)
        if self.mode == "debug":
            print(text, end=last)

    def s(self, title: str):
        """
            s(tart_section)
            Adds indent and indicates start of new section
            Always precedes a call to (e)nd_function
        """
        self.indent()
        self.sections.append(title)
        self.starts.append(dt.now())
        string = f"START {title}"
        if self.mode in ("on", "debug"):
            self.file.write(string)
            self.file.write("\n")
        if self.mode == "debug":
            print(string)

    def e(self, message: str = ""):
        """ e(nd_section)
            Removes indent and indicates end of new section
            Always follows a call to (s)tart_function
        """
        func = self.sections.pop()
        start = self.starts.pop()
        #print(f"Calling e for {func=} {start=} {self.mode=}")
        seconds = (dt.now() - start).seconds + (dt.now() - start).microseconds / 1000000
        string = f"END {func} ({seconds:.3f}s) {message}"
        self.indent()
        if self.mode in ("on", "debug"):
            self.file.write(string)
            self.file.write("\n")
        if self.mode == "debug":
            print(string)

    def section_seconds(self):
        start = self.starts[-1:][0]
        seconds = (dt.now() - start).seconds + (dt.now() - start).microseconds / 1000000
        return round(seconds,3)


