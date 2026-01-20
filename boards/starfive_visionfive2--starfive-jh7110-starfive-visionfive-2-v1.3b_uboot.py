# %% [markdown]
"""
[![Renode](https://dl.antmicro.com/projects/renode/renode.svg)](https://renode.io)

[![Run in Google Colab](https://img.shields.io/badge/-Run%20in%20Google%20colab-%23007ded?logo=google-colab&logoColor=white&style=for-the-badge)](https://colab.research.google.com/github/antmicro/test-colabs/blob/main/boards/starfive_visionfive2--starfive-jh7110-starfive-visionfive-2-v1.3b_uboot.ipynb) [![View ipynb](https://img.shields.io/badge/-View%20ipynb%20source-%23007ded?logo=jupyter&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/starfive_visionfive2--starfive-jh7110-starfive-visionfive-2-v1.3b_uboot.ipynb) [![View Python source](https://img.shields.io/badge/-View%20Python%20source-%23007ded?logo=python&logoColor=white&style=for-the-badge)](https://github.com/antmicro/test-colabs/blob/main/boards/starfive_visionfive2--starfive-jh7110-starfive-visionfive-2-v1.3b_uboot.py)
"""

# %% [markdown]
"""
## Install requirements
"""

# %%
! pip install -q git+https://github.com/antmicro/renode-colab-tools.git
! pip install -q git+https://github.com/antmicro/renode-run.git
! pip install -q git+https://github.com/antmicro/pyrenode3.git
! renode-run download --renode-variant dotnet-portable

# %% [markdown]
"""## Start Renode"""

# %%
import os
from renode_run import get_default_renode_path
from renode_run.utils import RenodeVariant

os.environ['PYRENODE_RUNTIME'] = 'coreclr'
os.environ['PYRENODE_BIN'] = get_default_renode_path(variant=RenodeVariant.DOTNET_PORTABLE)

from pyrenode3.wrappers import Emulation, Monitor, TerminalTester, LEDTester
from Antmicro.Renode.Peripherals.UART import UARTBackend
from Antmicro.Renode.Analyzers import LoggingUartAnalyzer
from System import String

currentDirectory = os.getcwd()
emulation = Emulation()
monitor = Monitor()
emulation.BackendManager.SetPreferredAnalyzer(UARTBackend, LoggingUartAnalyzer)

# %% [markdown]
"""## Setup a script"""

# %%
%%writefile script.resc
logFile $ORIGIN/uboot-renode.log True

$name?="starfive_visionfive2--starfive-jh7110-starfive-visionfive-2-v1.3b"
$bin?=@https://zephyr-dashboard.renode.io/uboot/ff498a3c5efb424accc1d825cc45cede2540ca13/starfive_visionfive2--starfive-jh7110-starfive-visionfive-2-v1.3b/uboot/uboot.elf
$repl?=$ORIGIN/uboot.repl

using sysbus
mach create $name

machine LoadPlatformDescription @https://u-boot-dashboard.renode.io/uboot_sim/ff498a3c5efb424accc1d825cc45cede2540ca13/d228058428cec4d6b66916cf4133bcbab372011b/starfive_visionfive2--starfive-jh7110-starfive-visionfive-2-v1.3b/uboot/uboot.repl
machine EnableProfiler $ORIGIN/metrics.dump


showAnalyzer uart0

uart0 RecordToAsciinema $ORIGIN/uboot-asciinema
set osPanicHook
"""
self.ErrorLog("OS Panicked")
"""
cpu0 AddSymbolHook "hang" $osPanicHook
cpu0 AddSymbolHook "panic" $osPanicHook


macro reset
"""
    sysbus LoadELF $bin 
    cpu0 EnableUbootMode
    cpu0 EnableZephyrMode
    cpu1 IsHalted true
    cpu2 IsHalted true
    cpu3 IsHalted true
    sysbus LoadBinary @https://u-boot-dashboard.renode.io/uboot/6a0db9ee030f634731b792d864fc7a9df6cc6b80/microchip_mpfs_icicle--microchip-mpfs-icicle-kit/uboot/fw_dynamic.bin 0x80000000
    cpu0 PC 0x80000000

    cpu0 SetRegister "A0" 0x1                           # hart number
    cpu0 SetRegister "A1" 0x00000000402a1e60                # fdt location
    cpu0 SetRegister "A2" 0x80100000                    # struct fw_dynamic_info address

    # struct fw_dynamic_info
    sysbus WriteQuadWord 0x80100000 0x4942534f          # magic
    sysbus WriteQuadWord 0x80100008 0x2                 # version
    sysbus WriteQuadWord 0x80100010 0x40200000    # next_addr
    sysbus WriteQuadWord 0x80100018 0x1                 # next_mode
    sysbus WriteQuadWord 0x80100020 0x0                 # options
    sysbus WriteQuadWord 0x80100028 0x1                 # boot hart
"""

runMacro $reset

# %% [markdown]
"""## Run the sample"""

# %%
monitor.execute_script(currentDirectory + "/script.resc")
machine = emulation.get_mach("starfive_visionfive2--starfive-jh7110-starfive-visionfive-2-v1.3b")
terminalTester = TerminalTester(machine.sysbus.uart0, 5)

terminalTester.WaitFor(String("Hit any key to stop autoboot"), includeUnfinishedLine=True, pauseEmulation=True)
terminalTester.Write("\n")
terminalTester.WaitFor(String(">"), includeUnfinishedLine=True, pauseEmulation=True)
terminalTester.WriteLine("version")
terminalTester.WaitFor(String("U-Boot"), pauseEmulation=True)
terminalTester.WaitFor(String(">"), includeUnfinishedLine=True, pauseEmulation=True)

emulation.Dispose()

# %% [markdown]
"""## UART output"""

# %%
from renode_colab_tools import asciinema
asciinema.display_asciicast('uboot-asciinema')

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
