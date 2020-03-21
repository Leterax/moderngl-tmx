from setuptools import setup, find_namespace_packages

setup(
    name="moderngl-tmx",
    version="0.1.0",
    description="moderngl-tmx allows you to display Tiled Map Editor (.tmx) files ",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/Leterax/moderngl_tmx",
    author="Leterax",
    author_email="leterax@leterax.com",
    packages=find_namespace_packages(include=['moderngl_tmx', 'moderngl_tmx.*']),
    include_package_data=True,
    keywords=['tmx' 'moderngl'],
    license='MIT',
    platforms=['any'],
    python_requires='>=3.5',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Games/Entertainment',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: 3D Rendering',
        'Topic :: Scientific/Engineering :: Visualization',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=[
        'moderngl<6',
    ],
)
