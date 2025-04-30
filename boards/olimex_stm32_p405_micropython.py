# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/olimex_stm32_p405_micropython.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/olimex_stm32_p405_micropython.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/olimex_stm32_p405_micropython.py)
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
$name?="olimex_stm32_p405"
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/zephyr_sim/29197ac9633c2542fd0c9b63639af1f75462844e/cb8e70c557b089373bca37e93d3af87f9392dbce/olimex_stm32_p405/micropython/micropython.repl
machine EnableProfiler $ORIGIN/metrics.dump

showAnalyzer sysbus.usart2
sysbus.usart2 RecordToAsciinema $ORIGIN/output.asciinema

macro reset
"""
    sysbus LoadELF @https://zephyr-dashboard.renode.io/zephyr/29197ac9633c2542fd0c9b63639af1f75462844e/olimex_stm32_p405/micropython/micropython.elf
    cpu0 VectorTableOffset `sysbus GetSymbolAddress "_vector_table"`
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
ExecuteScript("script.resc")
CreateTerminalTester("sysbus.usart2", timeout=5)
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
from renode_run import get_default_renode_path
sys.path.append(str(Path(get_default_renode_path()).parent))

from renode_colab_tools import metrics
from tools.metrics_analyzer.metrics_parser import MetricsParser
metrics.init_notebook_mode(connected=False)
parser = MetricsParser('metrics.dump')

metrics.display_metrics(parser)
