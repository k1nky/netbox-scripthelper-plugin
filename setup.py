from setuptools import find_packages, setup

setup(
    name='netbox_scripthelper',
    version='0.1.1',
    description='Collections of utilities for Netbox custom scripts.',
    url='https://github.com/k1nky/netbox-scripthelper-plugin',
    author='Andrey Shalashov',
    author_email='avshalashov@yandex.ru',
    license='Apache 2.0',
    keywords='netbox script custom helper plugin',
    install_requires=[
        'netaddr'
    ],
    packages=find_packages(),
    package_data={},
    include_package_data=True,
    zip_safe=False,
)
