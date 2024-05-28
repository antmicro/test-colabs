# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/stm32g071b_disco_kenning-zephyr-runtime-microtvm.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/stm32g071b_disco_kenning-zephyr-runtime-microtvm.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/stm32g071b_disco_kenning-zephyr-runtime-microtvm.py)
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
$name?="stm32g071b_disco"
mach create $name

machine LoadPlatformDescription @https://zephyr-dashboard.renode.io/zephyr_sim/99adbadad5a2ccd70ed7e7a483b7615bd043d999/b672f64553038487a18982117c723859240f277e/stm32g071b_disco/kenning-zephyr-runtime-microtvm/kenning-zephyr-runtime-microtvm.repl
machine EnableProfiler $ORIGIN/metrics.dump

showAnalyzer sysbus.usart3
sysbus.usart3 RecordToAsciinema $ORIGIN/output.asciinema

macro reset
"""
    sysbus LoadELF @https://zephyr-dashboard.renode.io/zephyr/99adbadad5a2ccd70ed7e7a483b7615bd043d999/stm32g071b_disco/kenning-zephyr-runtime-microtvm/kenning-zephyr-runtime-microtvm.elf
    cpu0 VectorTableOffset `sysbus GetSymbolAddress "_vector_table"`
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
ExecuteScript("script.resc")
CreateTerminalTester("sysbus.usart3", timeout=5)

WaitForLineOnUart("\*\*\* Booting Zephyr OS build.+99adbadad5a2 \*\*\*", treatAsRegex=True)

WaitForLineOnUart("I: model output: [wing: 1.000000, ring: 0.000000, slope: 0.000000, negative: 0.000000]")
WaitForLineOnUart("I: model output: [wing: 0.000000, ring: 0.000000, slope: 0.000000, negative: 1.000000]")
WaitForLineOnUart("I: model output: [wing: 0.000000, ring: 0.000000, slope: 1.000000, negative: 0.000000]")
WaitForLineOnUart("I: model output: [wing: 1.000000, ring: 0.000000, slope: 0.000000, negative: 0.000000]")
WaitForLineOnUart("I: model output: [wing: 0.000000, ring: 0.997465, slope: 0.000000, negative: 0.002535]")
WaitForLineOnUart("I: model output: [wing: 0.000000, ring: 0.000000, slope: 1.000000, negative: 0.000000]")
WaitForLineOnUart("I: model output: [wing: 1.000000, ring: 0.000000, slope: 0.000000, negative: 0.000000]")
WaitForLineOnUart("I: model output: [wing: 1.000000, ring: 0.000000, slope: 0.000000, negative: 0.000000]")
WaitForLineOnUart("I: model output: [wing: 1.000000, ring: 0.000000, slope: 0.000000, negative: 0.000000]")
WaitForLineOnUart("I: model output: [wing: 0.000000, ring: 0.000000, slope: 1.000000, negative: 0.000000]")
WaitForLineOnUart("I: inference done")

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
