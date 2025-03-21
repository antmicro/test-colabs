# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/anbernic-rgxx3-rk3566--rockchip-rk3566-anbernic-rg353p_uboot.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/anbernic-rgxx3-rk3566--rockchip-rk3566-anbernic-rg353p_uboot.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/anbernic-rgxx3-rk3566--rockchip-rk3566-anbernic-rg353p_uboot.py)
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
$name?="anbernic-rgxx3-rk3566--rockchip-rk3566-anbernic-rg353p"
mach create $name

machine LoadPlatformDescription @https://u-boot-dashboard.renode.io/uboot_sim/ca3bea3fc415ce40dc58f1bea9327f6fa12928bb/728988758ca57c0a9486adf4f950b903c9203710/anbernic-rgxx3-rk3566--rockchip-rk3566-anbernic-rg353p/uboot/uboot.repl
machine EnableProfiler $ORIGIN/metrics.dump

showAnalyzer sysbus.uart2
sysbus.uart2 RecordToAsciinema $ORIGIN/output.asciinema

macro reset
"""
    sysbus LoadELF @https://u-boot-dashboard.renode.io/uboot/ca3bea3fc415ce40dc58f1bea9327f6fa12928bb/anbernic-rgxx3-rk3566--rockchip-rk3566-anbernic-rg353p/uboot/uboot.elf
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

WaitForPromptOnUart("Hit any key to stop autoboot")
SendKeyToUart(ord('a'))
WaitForPromptOnUart(">")
WriteLineToUart("version")
WaitForLineOnUart("U-Boot")

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
from renode_run import get_default_renode_path
sys.path.append(str(Path(get_default_renode_path()).parent))

from renode_colab_tools import metrics
from tools.metrics_analyzer.metrics_parser import MetricsParser
metrics.init_notebook_mode(connected=False)
parser = MetricsParser('metrics.dump')

metrics.display_metrics(parser)
