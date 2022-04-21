# %% [markdown]
"""
![Renode](https://dl.antmicro.com/projects/renode/renode.png)
<table align="left">
  <td>
    <a target="_blank" href="https://colab.research.google.com/github/antmicro/test-colabs/blob/master/test.ipynb"><img src="https://raw.githubusercontent.com/antmicro/test-colabs/master/.static/view-in-colab.png" />Run in Google Colab</a>
  </td>
  <td>
    <a target="_blank" href="https://github.com/antmicro/test-colabs/blob/master/test.ipynb"><img src="https://raw.githubusercontent.com/antmicro/test-colabs/master/.static/view-ipynb.png" />View ipynb on GitHub</a>
  </td>
  <td>
    <a target="_blank" href="https://github.com/antmicro/test-colabs/blob/master/test.py"><img src="https://raw.githubusercontent.com/antmicro/test-colabs/master/.static/view-source.png" />View Python source on GitHub</a>
  </td>
</table>
"""

# %% [markdown]
"""
## Install requirements
"""

# %%
! pip install -q git+https://github.com/antmicro/renode-colab-tools.git
! pip install -q git+https://github.com/antmicro/renode-run.git@testing

import sys
sys.path.append('/root/.config/renode/renode-run.download/renode_1.12.0+20220421git03004859_portable')

# %% [markdown]
"""## Run the philosophers example in Renode"""

# %%
! renode-run demo -b philosophers hifive1_revb

# %% [markdown]
"""## Renode metrics analysis"""

# %%
from renode_colab_tools import metrics
from tools.metrics_analyzer.metrics_parser import MetricsParser
metrics.init_notebook_mode(connected=False)
parser = MetricsParser('/tmp/metrics.dump')

# %%
metrics.configure_plotly_browser_state()
metrics.show_executed_instructions(parser)

# %%
metrics.configure_plotly_browser_state()
metrics.show_memory_access(parser)

# %%
metrics.configure_plotly_browser_state()
metrics.show_exceptions(parser)

# %%
metrics.configure_plotly_browser_state()
metrics.show_peripheral_access(parser)
