# %% [markdown]
"""
![Renode](https://dl.antmicro.com/projects/renode/renode.svg)
<table align="left">
  <td>
    <a target="_blank" href="https://colab.research.google.com/github/antmicro/test-colabs/blob/main/philosophers.ipynb"><img src="https://raw.githubusercontent.com/antmicro/test-colabs/main/.static/view-in-colab.png" />Run in Google Colab</a>
  </td>
  <td>
    <a target="_blank" href="https://github.com/antmicro/test-colabs/blob/main/philosophers.ipynb"><img src="https://raw.githubusercontent.com/antmicro/test-colabs/main/.static/view-ipynb.png" />View ipynb on GitHub</a>
  </td>
  <td>
    <a target="_blank" href="https://github.com/antmicro/test-colabs/blob/main/philosophers.py"><img src="https://raw.githubusercontent.com/antmicro/test-colabs/main/.static/view-source.png" />View Python source on GitHub</a>
  </td>
</table>
"""

# %% [markdown]
"""
## Install requirements
"""

# %%
! pip install -q git+https://github.com/antmicro/renode-colab-tools.git
! pip install -q git+https://github.com/antmicro/renode-run.git
! pip install -q git+https://github.com/antmicro/pyrenode.git@2.0
! pip install -q robotframework==4.0.1

# %% [markdown]
"""## Start Renode"""

# %%
from msilib.schema import ReserveCost
from pyrenode import connect_renode, get_keywords
connect_renode(robot_port=3456)
get_keywords()

# %% [markdown]
"""## Setup a script"""

# %% 
%%writefile script.resc

using sysbus
$name?="{{zephyr_platform}}"
mach create $name

machine LoadPlatformDescription @{{zephyr_platform}}-{{sample_name}}.repl

showAnalyzer {{uart_name}}
{{uart_name}} RecordToAsciinema @{{zephyr_platform}}-{{sample_name}}-asciinema

macro reset
"""
    sysbus LoadELF $ORIGIN/{{zephyr_platform}}-zephyr-{{sample_name}}.elf
    {{ script }}
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
ExecuteCommand("include @script.resc")
CreateTerminalTester("{{uart_name}}", timeout=5)
StartEmulation()

WaitForLineOnUart("Philosopher 0.*THINKING", treatAsRegex=True)
WaitForLineOnUart("Philosopher 0.*HOLDING", treatAsRegex=True)
WaitForLineOnUart("Philosopher 0.*EATING", treatAsRegex=True)

ExecuteCommand("{{uart_name}} DumpHistoryBuffer")


# %% [markdown]
"""## Renode metrics analysis"""

# %%
import sys
from pathlib import Path
sys.path.append(Path('/root/.config/renode/renode-run.path').read_text())

from renode_colab_tools import metrics
from tools.metrics_analyzer.metrics_parser import MetricsParser
metrics.init_notebook_mode(connected=False)
parser = MetricsParser('/tmp/metrics.dump')

# %%
metrics.configure_plotly_browser_state()
metrics.show_executed_instructions(parser)

# %%
metrics.configure_plotly_browser_state()
metrics.show_memory_access(parser)

# %%
metrics.configure_plotly_browser_state()
metrics.show_exceptions(parser)

# %%
metrics.configure_plotly_browser_state()
metrics.show_peripheral_access(parser)
