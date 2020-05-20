from typing import Optional

from setuptools import setup, find_packages


package_name = 'learn_python_bot'


def get_version() -> Optional[str]:
    with open(f'{package_name}/__init__.py', 'r') as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith('__version__'):
            return line.split('=')[-1].strip().strip("'")


def get_long_description() -> str:
    with open('README.md', encoding='utf8') as f:
        return f.read()


setup(
    name=package_name,
    description='Bot for learn.python.ru students&staff.',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    packages=find_packages(),
    version=get_version(),
    author='Ilya Lebedev',
    author_email='melevir@gmail.com',
    install_requires=[
        'setuptools',
        'python-telegram-bot[socks]>=12.7',
        'click>=7.1.2',
        'requests>=2.23.0',
    ],
    entry_points={
        'console_scripts': [
            'lp_run_bot = learn_python_bot.bot:main',
            'lp_ask_for_feedback = learn_python_bot.ask_for_feedback:main',
            'lp_send_stat_report = learn_python_bot.send_stat_report:main',
        ],
    },
    url='https://github.com/moscowpython/capaldi',
    license='MIT',
    py_modules=[package_name],
    zip_safe=False,
)
