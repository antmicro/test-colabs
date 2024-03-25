# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/rddrone_fmuk66_lz4.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/rddrone_fmuk66_lz4.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/rddrone_fmuk66_lz4.py)
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
$name?="rddrone_fmuk66"
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/rddrone_fmuk66-lz4/rddrone_fmuk66-lz4.repl
machine EnableProfiler $ORIGIN/metrics.dump

showAnalyzer sysbus.lpuart0
sysbus.lpuart0 RecordToAsciinema $ORIGIN/output.asciinema

macro reset
"""
    sysbus LoadELF @https://new-zephyr-dashboard.renode.io/zephyr/f90c2b1122ead7c8dcb4c9cbf98abf2544b77ee0/rddrone_fmuk66/lz4/lz4.elf
    cpu0 VectorTableOffset `sysbus GetSymbolAddress "_vector_table"`
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
ExecuteScript("script.resc")
CreateTerminalTester("sysbus.lpuart0", timeout=5)
StartEmulation()

WaitForLineOnUart(r"Original Data size: \d+", treatAsRegex=True)
WaitForLineOnUart(r"Compressed Data size : \d+", treatAsRegex=True)
WaitForLineOnUart("Successfully decompressed some data")
WaitForLineOnUart("Validation done. The string we ended up with is:")
WaitForLineOnUart(r".*", treatAsRegex=True)

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
