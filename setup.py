import sys
from platform import uname

from setuptools import setup, find_packages




install_requires=['matplotlib>=3.5.2', 'numpy>=1.21.5', 'pandas>=1.4.4']




name = 'fmpAPI_terminal'

setup(name=name,
      version='1.0',
      packages=[name],
      package_dir={name: 'fmpAPI_terminal/'},
      package_data={name:['charts/watchlist/ticker.txt','SECfilings/quarter/*', 'SECfilings/ttm/*', 'help/*']},
      install_requires=install_requires,
	entry_points = {'console_scripts': [f'fmp_terminal={name}.terminal:main'],}
      )