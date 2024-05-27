# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/roc_rk3568_pc_hello_world.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/roc_rk3568_pc_hello_world.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/roc_rk3568_pc_hello_world.py)
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
$name?="roc_rk3568_pc"
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/zephyr_sim/99adbadad5a2ccd70ed7e7a483b7615bd043d999/b672f64553038487a18982117c723859240f277e/roc_rk3568_pc/hello_world/hello_world.repl
machine EnableProfiler $ORIGIN/metrics.dump

showAnalyzer sysbus.uart2
sysbus.uart2 RecordToAsciinema $ORIGIN/output.asciinema

macro reset
"""
    sysbus LoadELF @https://zephyr-dashboard.renode.io/zephyr/99adbadad5a2ccd70ed7e7a483b7615bd043d999/roc_rk3568_pc/hello_world/hello_world.elf
    cpu1 IsHalted true
    cpu2 IsHalted true
    cpu3 IsHalted true
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
ExecuteScript("script.resc")
CreateTerminalTester("sysbus.uart2", timeout=5)
StartEmulation()

WaitForLineOnUart("Hello World! roc_rk3568_pc")

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
from renode_run import get_default_renode_path
sys.path.append(get_default_renode_path())

from renode_colab_tools import metrics
from tools.metrics_analyzer.metrics_parser import MetricsParser
metrics.init_notebook_mode(connected=False)
parser = MetricsParser('metrics.dump')

metrics.display_metrics(parser)
