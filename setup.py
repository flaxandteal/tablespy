from setuptools import setup, find_packages

setup(
    name='tablespy',
    version='0.0.3',
    description='Table spotter for spreadsheets',
    url='https://github.com/flaxandteal/tablespy',
    author='Phil Weir',
    author_email='phil.weir@flaxandteal.co.uk',
    license='MIT',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7'
    ],
    keywords='pandas table ods xls',
    install_requires=[
        'Click',
        'pandas',
        'scikit-image',
        'tabulator[ods]'
    ],
    entry_points='''
        [console_scripts]
        tablespy=tablespy.scripts.tablespy:cli
    '''
)
