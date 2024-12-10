# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources/icons/wind-energy.ico', 'resources/icons'),
        ('resources/fonts/DejaVuSans.ttf', 'resources/fonts'),
        ('resources/fonts/DejaVuSansCondensed-Bold.ttf', 'resources/fonts'),
        ('resources/images/calendar.png', 'resources/images'),
        ('transparent.ico', '.'),
        ('turbines.json', '.')
    ],
    hiddenimports=['babel.numbers', 'babel.localedata'],  # Include babel modules
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='WindEnergyApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='resources/icons/wind-energy.ico'
)
