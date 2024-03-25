# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/actinius_icarus_bee_nrf9160_ns_micropython.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/actinius_icarus_bee_nrf9160_ns_micropython.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/actinius_icarus_bee_nrf9160_ns_micropython.py)
"""

# %% [markdown]
"""
## Install requirements
"""

# %%
! pip install -q git+https://github.com/antmicro/renode-colab-tools.git
! pip install -q git+https://github.com/antmicro/renode-run.git
! pip install -q git+https://github.com/antmicro/pyrenode.git
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
$name?="actinius_icarus_bee_nrf9160_ns"
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/actinius_icarus_bee_nrf9160_ns-micropython/actinius_icarus_bee_nrf9160_ns-micropython.repl
machine EnableProfiler $ORIGIN/metrics.dump

showAnalyzer sysbus.uart0
sysbus.uart0 RecordToAsciinema $ORIGIN/output.asciinema

macro reset
"""
    sysbus LoadELF @https://new-zephyr-dashboard.renode.io/zephyr/f90c2b1122ead7c8dcb4c9cbf98abf2544b77ee0/actinius_icarus_bee_nrf9160_ns/micropython/micropython.elf
    cpu0 VectorTableOffset `sysbus GetSymbolAddress "_vector_table"`
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
ExecuteScript("script.resc")
CreateTerminalTester("sysbus.uart0", timeout=5)
StartEmulation()

WaitForPromptOnUart(">>>")
WriteLineToUart("2+2")
WriteLineToUart("")
WaitForLineOnUart("4")
WriteLineToUart("def compare(a, b): return True if a > b else False")
WriteLineToUart("")
WriteLineToUart("compare(3.2, 2.4)")
WaitForLineOnUart("True")
WriteLineToUart("compare(2.2, 5.8)")
WaitForLineOnUart("False")

ResetEmulation()

# %% [markdown]
"""## UART output"""

# %%
from renode_colab_tools import asciinema
asciinema.display_asciicast('output.asciinema')

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