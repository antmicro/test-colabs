# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/adp_xc7k_ae350_shell_module.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/adp_xc7k_ae350_shell_module.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/adp_xc7k_ae350_shell_module.py)
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
$name?="adp_xc7k_ae350"
mach create $name

machine LoadPlatformDescription @https://new-zephyr-dashboard.renode.io/zephyr_sim/3723493f60a10f17d8d117fb8288a75da20cdd74/36b60de1af1f7047573c8085a0c298f743270043/adp_xc7k_ae350/shell_module/shell_module.repl
machine EnableProfiler $ORIGIN/metrics.dump

showAnalyzer sysbus.uart1
sysbus.uart1 RecordToAsciinema $ORIGIN/output.asciinema

macro reset
"""
    sysbus LoadELF @https://new-zephyr-dashboard.renode.io/zephyr/3723493f60a10f17d8d117fb8288a75da20cdd74/adp_xc7k_ae350/shell_module/shell_module.elf
    cpu1 IsHalted true
    cpu2 IsHalted true
    cpu3 IsHalted true
    cpu4 IsHalted true
    cpu5 IsHalted true
    cpu6 IsHalted true
    cpu7 IsHalted true
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
ExecuteScript("script.resc")
CreateTerminalTester("sysbus.uart1", timeout=5)
StartEmulation()

WaitForPromptOnUart("uart:~$")
WriteLineToUart("")
WaitForPromptOnUart("uart:~$")
WriteLineToUart("demo board")
WaitForLineOnUart("adp_xc7k_ae350")

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
