import pandas as pd
import tools

class Config:
    def __init__(self, config_df: pd.DataFrame):
        self.url:str = config_df[config_df['name'] == 'url']['value'].iloc[0]
        self.headless:bool = tools.string_to_bool(config_df[config_df['name'] == 'headless']['value'].iloc[0])
        self.trace_mode:bool = tools.string_to_bool(config_df[config_df['name'] == 'trace_mode']['value'].iloc[0])
        self.screenshots: bool = tools.string_to_bool(config_df[config_df['name'] == 'screenshots']['value'].iloc[0])
        self.inspect: bool = tools.string_to_bool(config_df[config_df['name'] == 'inspect']['value'].iloc[0])
        self.trace_file:str = config_df[config_df['name'] == 'trace_file']['value'].iloc[0]
        self.platform:str = config_df[config_df['name'] == 'platform']['value'].iloc[0]
        self.browsers: list[str] = tools.str_to_list(config_df[config_df['name'] == 'browser']['value'].iloc[0])
        self.skip_steps: list[int] = tools.str_to_int_list(config_df[config_df['name'] == 'skip_steps']['value'].iloc[0])

    def display(self):
        return (f"  url:  {self.url}\n"
                f"    headless={self.headless}  trace_mode={self.trace_mode}  screenshots={self.screenshots}\n"
                f"    inspect:{self.inspect}  platform:{self.platform}  browser(s):{self.browsers} \n"
                f"    trace_file:{self.trace_file}  skip_steps={self.skip_steps}  \n")
