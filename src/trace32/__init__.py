"""
@文件: __init__.py.py
@作者: 雷小鸥
@日期: 2025/5/6 14:02
@描述: 
@许可: MIT License
@版本: Version 1.0
"""
from . import errors as T32Error

from ._trace32 import DeviceType, T32

__all__ = ['DeviceType', 'T32', 'T32Error']



