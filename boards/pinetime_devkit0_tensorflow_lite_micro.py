# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/pinetime_devkit0_tensorflow_lite_micro.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/pinetime_devkit0_tensorflow_lite_micro.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/pinetime_devkit0_tensorflow_lite_micro.py)
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
$name?="pinetime_devkit0"
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/pinetime_devkit0-tensorflow_lite_micro.repl
machine EnableProfiler $ORIGIN/metrics.dump

showAnalyzer sysbus.uart0

macro reset
"""
    sysbus LoadELF @https://zephyr-dashboard.renode.io/pinetime_devkit0-zephyr-tensorflow_lite_micro.elf
    cpu0 VectorTableOffset `sysbus GetSymbolAddress "_vector_table"`
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
ExecuteCommand("include @script.resc")
CreateTerminalTester("sysbus.uart0", timeout=15)
StartEmulation()

WaitForLineOnUart("x_value: .* y_value: .*", treatAsRegex=True)
WaitForLineOnUart("x_value: .* y_value: .*", treatAsRegex=True)
WaitForLineOnUart("x_value: .* y_value: .*", treatAsRegex=True)
WaitForLineOnUart("x_value: .* y_value: .*", treatAsRegex=True)

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
