from setuptools import setup

setup(name='pgen',
      version='0.0.1',
      description='Patterned workload generator',
      url='https://github.com/abcdabcd987/pgen',
      author='Lequn Chen',
      author_email='chenlequn22@gmail.com',
      python_requires='>=3.7',
      packages=['pgen'],
      install_requires=[
          'numpy',
          'aiohttp',
          'cchardet',
          'aiodns',
          'matplotlib',
      ]
)
