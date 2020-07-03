from setuptools import setup


with open('README.md') as fp:
    readme = fp.read()

setup(
    name='correlation',
    version='1.0.0',
    description='Calculate the confidence intervals of correlation coeficients',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='Xiangwen Wang',
    author_email='wangxiangwen1989@gmail.com',
    url='https://github.com/XiangwenWang/correlation',
    keywords='correlation, confidence interval',
    py_modules=['correlation'],
    scripts=['correlation.py'],
    install_requires=['numpy', 'scipy'],
    license="BSD 2-Clause License",
    zip_safe=True,
    platforms='any',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ]
)
