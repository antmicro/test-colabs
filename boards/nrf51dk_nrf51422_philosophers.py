# %% [markdown]
"""
![Renode](https://dl.antmicro.com/projects/renode/renode.svg)
<table align="left">
  <td>
    <a target="_blank" href="https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/nrf51dk_nrf51422_philosophers.ipynb"><img src="https://raw.githubusercontent.com/antmicro/test-colabs/main/.static/view-in-colab.png" />Run in Google Colab</a>
  </td>
  <td>
    <a target="_blank" href="https://github.com/antmicro/test-colabs/blob/main/boards/nrf51dk_nrf51422_philosophers.ipynb"><img src="https://raw.githubusercontent.com/antmicro/test-colabs/main/.static/view-ipynb.png" />View ipynb on GitHub</a>
  </td>
  <td>
    <a target="_blank" href="https://github.com/antmicro/test-colabs/blob/main/boards/nrf51dk_nrf51422_philosophers.py"><img src="https://raw.githubusercontent.com/antmicro/test-colabs/main/.static/view-source.png" />View Python source on GitHub</a>
  </td>
</table>
"""

# %% [markdown]
"""
## Install requirements
"""

# %%
! pip install -q git+https://github.com/antmicro/renode-colab-tools.git@tabbed-metrics
! pip install -q git+https://github.com/antmicro/renode-run.git@new-features
! pip install -q git+https://github.com/antmicro/pyrenode.git@renode-run-experiments
! pip install -q robotframework==4.0.1
! renode-run download

# %% [markdown]
"""## Start Renode"""

# %%
from pyrenode import connect_renode, get_keywords
connect_renode()
get_keywords()

# %% [markdown]
"""## Setup a script"""

# %%
%%writefile script.resc

using sysbus
$name?="nrf51dk_nrf51422"
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/nrf51dk_nrf51422-philosophers.repl
machine EnableProfiler $ORIGIN/metrics.dump

showAnalyzer sysbus.uart0

macro reset
"""
    sysbus LoadELF @https://zephyr-dashboard.renode.io/nrf51dk_nrf51422-zephyr-philosophers.elf
    cpu0 VectorTableOffset `sysbus GetSymbolAddress "_vector_table"`
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
ExecuteCommand("include @script.resc")
CreateTerminalTester("sysbus.uart0", timeout=5)
StartEmulation()

WaitForLineOnUart("Philosopher 0.*THINKING", treatAsRegex=True)
WaitForLineOnUart("Philosopher 0.*HOLDING", treatAsRegex=True)
WaitForLineOnUart("Philosopher 0.*EATING", treatAsRegex=True)
print(ExecuteCommand("sysbus.uart0 DumpHistoryBuffer"))

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

metrics.display_metrics(parser)
