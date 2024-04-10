# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/arty_a7_designstart_fpga_cortex_m1_synchronization.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/arty_a7_designstart_fpga_cortex_m1_synchronization.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/arty_a7_designstart_fpga_cortex_m1_synchronization.py)
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
$name?="arty_a7_designstart_fpga_cortex_m1"
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/zephyr_sim/25812289779f471143cf1a2cc34c245c603bd941/a62db5c9be07ce1bc43c383460194ee0fbc9ee72/arty_a7_designstart_fpga_cortex_m1/synchronization/synchronization.repl
machine EnableProfiler $ORIGIN/metrics.dump

showAnalyzer sysbus.uartlite0
sysbus.uartlite0 RecordToAsciinema $ORIGIN/output.asciinema

macro reset
"""
    sysbus LoadELF @https://zephyr-dashboard.renode.io/zephyr/25812289779f471143cf1a2cc34c245c603bd941/arty_a7_designstart_fpga_cortex_m1/synchronization/synchronization.elf
    cpu0 VectorTableOffset `sysbus GetSymbolAddress "_vector_table"`
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
ExecuteScript("script.resc")
CreateTerminalTester("sysbus.uartlite0", timeout=5)
StartEmulation()

WaitForLineOnUart(r"thread_a: Hello World from cpu \d on arty_a7_designstart_fpga_cortex_m1", treatAsRegex=True)
WaitForLineOnUart(r"thread_b: Hello World from cpu \d on arty_a7_designstart_fpga_cortex_m1", treatAsRegex=True)
WaitForLineOnUart(r"thread_a: Hello World from cpu \d on arty_a7_designstart_fpga_cortex_m1", treatAsRegex=True)
WaitForLineOnUart(r"thread_b: Hello World from cpu \d on arty_a7_designstart_fpga_cortex_m1", treatAsRegex=True)

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
