# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/hifive1_philosophers.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/hifive1_philosophers.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/hifive1_philosophers.py)
"""

# %% [markdown]
"""
## Install requirements
"""

# %%
! pip install -q git+https://github.com/antmicro/renode-colab-tools.git
! pip install -q git+https://github.com/antmicro/renode-run.git@new-features
! pip install -q git+https://github.com/antmicro/pyrenode.git
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
$name?="hifive1"
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/hifive1-philosophers.repl
machine EnableProfiler $ORIGIN/metrics.dump

showAnalyzer sysbus.uart0

macro reset
"""
    sysbus LoadELF @https://zephyr-dashboard.renode.io/hifive1-zephyr-philosophers.elf
    
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
