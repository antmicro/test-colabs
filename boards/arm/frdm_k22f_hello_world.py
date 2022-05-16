# %% [markdown]
"""
![Renode](https://dl.antmicro.com/projects/renode/renode.svg)
<table align="left">
  <td>
    <a target="_blank" href="https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/arm/frdm_k22f_hello_world.ipynb"><img src="https://raw.githubusercontent.com/antmicro/test-colabs/main/.static/view-in-colab.png" />Run in Google Colab</a>
  </td>
  <td>
    <a target="_blank" href="https://github.com/antmicro/test-colabs/blob/main/boards/arm/frdm_k22f_hello_world.ipynb"><img src="https://raw.githubusercontent.com/antmicro/test-colabs/main/.static/view-ipynb.png" />View ipynb on GitHub</a>
  </td>
  <td>
    <a target="_blank" href="https://github.com/antmicro/test-colabs/blob/main/boards/arm/frdm_k22f_hello_world.py"><img src="https://raw.githubusercontent.com/antmicro/test-colabs/main/.static/view-source.png" />View Python source on GitHub</a>
  </td>
</table>
"""

# %% [markdown]
"""
## Install requirements
"""

# %%
! pip install -q git+https://github.com/antmicro/renode-colab-tools.git
! pip install -q git+https://github.com/antmicro/renode-run.git@new-features
! pip install -q git+https://github.com/antmicro/pyrenode.git@renode-run-experiments
! pip install -q robotframework==4.0.1
! renode-run download

# %% [markdown]
"""## Start Renode"""

# %%
from pyrenode import connect_renode, get_keywords
connect_renode(robot_port=3456)
get_keywords()

# %% [markdown]
"""## Setup a script"""

# %%
%%writefile script.resc

using sysbus
$name?="frdm_k22f"
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/frdm_k22f-hello_world.repl
machine EnableProfiler @metrics.dump

showAnalyzer sysbus.uart1

macro reset
"""
    sysbus LoadELF @https://zephyr-dashboard.renode.io/frdm_k22f-zephyr-hello_world.elf
    cpu0 VectorTableOffset `sysbus GetSymbolAddress "_vector_table"`
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
ExecuteCommand("include @script.resc")
CreateTerminalTester("sysbus.uart1", timeout=5)
StartEmulation()

WaitForLineOnUart("Hello World! frdm_k22f")
print(ExecuteCommand("sysbus.uart1 DumpHistoryBuffer"))

ResetEmulation()
# %% [markdown]
"""## Renode metrics analysis"""

# %%
import sys
from pathlib import Path
sys.path.append(Path('/root/.config/renode/renode-run.path').read_text())

from renode_colab_tools import metrics
from tools.metrics_analyzer.metrics_parser import MetricsParser
metrics.init_notebook_mode(connected=False)
parser = MetricsParser('metrics.dump')

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
