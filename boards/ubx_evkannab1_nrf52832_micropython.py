# %% [markdown]
"""
![Renode](https://dl.antmicro.com/projects/renode/renode.svg)
<table align="left">
  <td>
    <a target="_blank" href="https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/ubx_evkannab1_nrf52832_micropython.ipynb"><img src="https://raw.githubusercontent.com/antmicro/test-colabs/main/.static/view-in-colab.png" />Run in Google Colab</a>
  </td>
  <td>
    <a target="_blank" href="https://github.com/antmicro/test-colabs/blob/main/boards/ubx_evkannab1_nrf52832_micropython.ipynb"><img src="https://raw.githubusercontent.com/antmicro/test-colabs/main/.static/view-ipynb.png" />View ipynb on GitHub</a>
  </td>
  <td>
    <a target="_blank" href="https://github.com/antmicro/test-colabs/blob/main/boards/ubx_evkannab1_nrf52832_micropython.py"><img src="https://raw.githubusercontent.com/antmicro/test-colabs/main/.static/view-source.png" />View Python source on GitHub</a>
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
connect_renode()
get_keywords()

# %% [markdown]
"""## Setup a script"""

# %%
%%writefile script.resc

using sysbus
$name?="ubx_evkannab1_nrf52832"
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/ubx_evkannab1_nrf52832-micropython.repl
machine EnableProfiler $ORIGIN/metrics.dump

showAnalyzer sysbus.uart0

macro reset
"""
    sysbus LoadELF @https://zephyr-dashboard.renode.io/ubx_evkannab1_nrf52832-zephyr-micropython.elf
    cpu0 VectorTableOffset `sysbus GetSymbolAddress "_vector_table"`
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
ExecuteCommand("include @script.resc")
CreateTerminalTester("sysbus.uart0", timeout=5)
StartEmulation()

WaitForPromptOnUart(">>>")
WaitForLineOnUart("2+2")
WriteLineToUart("")
WaitForLineOnUart("4")
WriteLineToUart("def compare(a, b): return True if a > b else False")
WriteLineToUart("")
WriteLineToUart("compare(3.2, 2.4)")
WaitForLineOnUart("True")
WriteLineToUart("compare(2.2, 5.8)")
WaitForLineOnUart("False")

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
