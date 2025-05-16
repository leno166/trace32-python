"""
@文件: errors.py
@作者: 雷小鸥
@日期: 2025/5/6 14:36
@描述: 
@许可: MIT License
@版本: Version 1.0
"""
from functools import lru_cache


class T32Error(Exception):
    """TRACE32 API 错误基类"""
    code: int = 514
    message: str = "TRACE32 API 错误"

    def __init__(self, msg: str = None):
        super().__init__(msg or self.message)


# ============================================================================
# note 客户端 错误码
# ============================================================================
class T32ClientError(T32Error):
    """客户端相关错误的基类"""
    code = -114
    message = "客户端错误"


class T32ClientReceiveFailError(T32ClientError):
    """接收 API 响应失败"""
    code = -1
    message = "接收数据失败"


class T32ClientTransmitFailError(T32ClientError):
    """发送 API 消息失败"""
    code = -2
    message = "发送数据失败"


class T32ClientParameterFailError(T32ClientError):
    """函数参数错误"""
    code = -3
    message = "函数参数错误"


class T32ClientSequenceFailError(T32ClientError):
    """消息序列错误（如请求/响应不匹配）"""
    code = -4
    message = "消息序列错误"


class T32ClientNotifyMaxEventExceededError(T32ClientError):
    """通知事件数量超过最大限制"""
    code = -5
    message = "最大通知事件数超出限制"


class T32ClientMallocFailError(T32ClientError):
    """内存分配失败（malloc 失败）"""
    code = -6
    message = "内存分配失败"


# ============================================================================
# note 标准错误码（Standard Error Codes）
# ============================================================================
class T32StandardError(T32Error):
    """标准错误码基类，表示目标设备或调试器返回的标准状态/错误"""
    code = 515
    message = "标准错误"


class T32TargetRunningError(T32StandardError):
    """目标正在运行"""
    code = 2
    message = "目标正在运行"


class T32TargetNotRunningError(T32StandardError):
    """目标未运行"""
    code = 3
    message = "目标未运行"


class T32TargetInResetError(T32StandardError):
    """目标处于复位状态"""
    code = 4
    message = "目标处于复位状态"


class T32AccessTimeoutError(T32StandardError):
    """访问超时，目标正在运行"""
    code = 6
    message = "访问超时，目标正在运行"


class T32NotImplementedError(T32StandardError):
    """功能未实现"""
    code = 10
    message = "功能未实现"


class T32RegisterSetUndefinedError(T32StandardError):
    """寄存器集未定义"""
    code = 14
    message = "寄存器集未定义"


class T32VerifyError(T32StandardError):
    """校验错误"""
    code = 15
    message = "校验错误"


class T32BusError(T32StandardError):
    """总线错误"""
    code = 16
    message = "总线错误"


class T32NoMemoryMappedError(T32StandardError):
    """未映射内存"""
    code = 22
    message = "未映射内存"


class T32TargetResetDetectedError(T32StandardError):
    """检测到目标复位"""
    code = 48
    message = "检测到目标复位"


class T32FdxBufferError(T32StandardError):
    """FDX 缓冲区错误"""
    code = 49
    message = "FDX 缓冲区错误"


class T32RtckTimeoutError(T32StandardError):
    """未检测到 RTCK 信号"""
    code = 57
    message = "未检测到 RTCK 信号"


class T32InvalidLicenseError(T32StandardError):
    """无效许可证"""
    code = 60
    message = "未检测到有效许可证"


class T32CoreNotActiveError(T32StandardError):
    """多核系统中核心无时钟/电源/复位"""
    code = 64
    message = "核心无时钟/电源/复位（SMP 模式）"


class T32UserSignalError(T32StandardError):
    """用户信号触发"""
    code = 67
    message = "用户信号"


class T32NorapiError(T32StandardError):
    """尝试连接到仿真器失败"""
    code = 83
    message = "试图连接仿真器但不支持 RAPI"


class T32FailedError(T32StandardError):
    """操作失败"""
    code = 113
    message = "操作失败"


class T32AccessLockedError(T32StandardError):
    """访问被锁定"""
    code = 123
    message = "访问被锁定"


class T32PowerFailError(T32StandardError):
    """电源故障"""
    code = 128
    message = "电源故障"


class T32DebugPortFailError(T32StandardError):
    """调试端口故障"""
    code = 140
    message = "调试端口故障"


class T32DebugPortTimeoutError(T32StandardError):
    """调试端口超时"""
    code = 144
    message = "调试端口超时"


class T32NoDeviceError(T32StandardError):
    """未找到调试设备"""
    code = 147
    message = "未找到调试设备"


class T32TargetResetFailError(T32StandardError):
    """目标复位失败"""
    code = 161
    message = "目标复位失败"


class T32EmulatorTimeoutError(T32StandardError):
    """仿真器通信超时"""
    code = 162
    message = "仿真器通信超时"


class T32NoRtckError(T32StandardError):
    """仿真器上未检测到 RTCK 信号"""
    code = 164
    message = "未检测到 RTCK 信号（仿真器）"


class T32AttachMissingError(T32StandardError):
    """T32_Attach() 尚未调用"""
    code = 254
    message = "缺少 T32_Attach() 调用"


class T32FatalError(T32StandardError):
    """严重错误"""
    code = 255
    message = "严重错误"


# ============================================================================
# note 函数特定错误码（Function Specific Error Codes）
# ============================================================================

class T32FunctionError(T32Error):
    """函数调用相关的错误基类"""
    code = -116  # 可选统一标识函数错误类别
    message = "函数调用错误"


class T32FunctionGeneralError(T32FunctionError):
    """通用函数错误（FN1~FN4）"""
    pass


class T32FunctionFn1Error(T32FunctionGeneralError):
    """函数错误 1"""
    code = 90
    message = "函数错误 FN1"


class T32FunctionFn2Error(T32FunctionGeneralError):
    """函数错误 2"""
    code = 91
    message = "函数错误 FN2"


class T32FunctionFn3Error(T32FunctionGeneralError):
    """函数错误 3"""
    code = 92
    message = "函数错误 FN3"


class T32FunctionFn4Error(T32FunctionGeneralError):
    """函数错误 4"""
    code = 93
    message = "函数错误 FN4"


class T32GetRamInternalError(T32FunctionError):
    """T32_GetRam 内部失败"""
    code = 0x1000
    message = "T32_GetRam 内部失败"


# ----------------------------------------------------------------------------
# Register 操作相关错误
# ----------------------------------------------------------------------------

class T32RegisterError(T32FunctionError):
    """寄存器操作相关错误"""
    pass


class T32ReadRegisterByNameNotFoundError(T32RegisterError):
    """T32_ReadRegisterByName: 寄存器未找到"""
    code = 0x1010
    message = "寄存器未找到（读取）"


class T32ReadRegisterByNameFailedError(T32RegisterError):
    """T32_ReadRegisterByName: 读取寄存器失败"""
    code = 0x1011
    message = "读取寄存器失败"


class T32WriteRegisterByNameNotFoundError(T32RegisterError):
    """T32_WriteRegisterByName: 寄存器未找到"""
    code = 0x1020
    message = "寄存器未找到（写入）"


class T32WriteRegisterByNameFailedError(T32RegisterError):
    """T32_WriteRegisterByName: 写入寄存器失败"""
    code = 0x1021
    message = "写入寄存器失败"


class T32ReadRegisterObjParameterFailError(T32RegisterError):
    """T32_ReadRegisterObj: 参数错误"""
    code = 0x1030
    message = "T32_ReadRegisterObj 参数错误"


class T32ReadRegisterObjMaxCoreExceededError(T32RegisterError):
    """T32_ReadRegisterObj: 核心数超出限制"""
    code = 0x1031
    message = "核心数超过最大支持数量（读取寄存器）"


class T32ReadRegisterObjNotFoundError(T32RegisterError):
    """T32_ReadRegisterObj: 寄存器未找到"""
    code = 0x1032
    message = "寄存器未找到（读取）"


class T32ReadRegisterSetObjParameterFailError(T32RegisterError):
    """T32_ReadRegisterSetObj: 参数错误"""
    code = 0x1033
    message = "T32_ReadRegisterSetObj 参数错误"


class T32ReadRegisterSetObjNumRegistersWrongError(T32RegisterError):
    """T32_ReadRegisterSetObj: 读取的寄存器数量不正确"""
    code = 0x1034
    message = "读取的寄存器数量不正确"


class T32WriteRegisterObjParameterFailError(T32RegisterError):
    """T32_WriteRegisterObj: 参数错误"""
    code = 0x1040
    message = "T32_WriteRegisterObj 参数错误"


class T32WriteRegisterObjMaxCoreExceededError(T32RegisterError):
    """T32_WriteRegisterObj: 核心数超出限制"""
    code = 0x1041
    message = "核心数超过最大支持数量（写入寄存器）"


class T32WriteRegisterObjNotFoundError(T32RegisterError):
    """T32_WriteRegisterObj: 寄存器未找到"""
    code = 0x1042
    message = "寄存器未找到（写入）"


class T32WriteRegisterObjWriteFailedError(T32RegisterError):
    """T32_WriteRegisterObj: 写入寄存器失败"""
    code = 0x1043
    message = "写入寄存器失败"


class T32SetBreakpointFailedError(T32FunctionError):
    """T32_WriteBreakpoint / T32_WriteBreakpointObj: 设置断点失败"""
    code = 0x1050
    message = "设置断点失败"


# ----------------------------------------------------------------------------
# Memory 操作相关错误
# ----------------------------------------------------------------------------

class T32MemoryError(T32FunctionError):
    """内存操作相关错误"""
    pass


class T32ReadMemoryObjParameterFailError(T32MemoryError):
    """T32_ReadMemoryObj: 参数错误"""
    code = 0x1060
    message = "T32_ReadMemoryObj 参数错误"


class T32WriteMemoryObjParameterFailError(T32MemoryError):
    """T32_WriteMemoryObj: 参数错误"""
    code = 0x1070
    message = "T32_WriteMemoryObj 参数错误"


class T32TransferMemoryBundleObjParameterFailError(T32MemoryError):
    """T32_TransferMemoryBundleObj: 参数错误"""
    code = 0x1071
    message = "T32_TransferMemoryBundleObj 参数错误"


class T32TransferMemoryBundleObjTransferFailedError(T32MemoryError):
    """T32_TransferMemoryBundleObj: 数据传输失败"""
    code = 0x1072
    message = "数据传输失败"


# ----------------------------------------------------------------------------
# Variable 操作相关错误
# ----------------------------------------------------------------------------

class T32VariableError(T32FunctionError):
    """变量操作相关错误"""
    pass


class T32ReadVariableAllocFailedError(T32VariableError):
    """T32_ReadVariable*: 内存分配失败"""
    code = 0x1080
    message = "内存分配失败（读取变量）"


class T32ReadVariableAccessFailedError(T32VariableError):
    """T32_ReadVariable*: 访问符号失败"""
    code = 0x1081
    message = "访问符号失败（读取变量）"


# ----------------------------------------------------------------------------
# Breakpoint 操作相关错误
# ----------------------------------------------------------------------------

class T32BreakpointError(T32FunctionError):
    """断点操作相关错误"""
    pass


class T32ReadBreakpointObjParameterFailError(T32BreakpointError):
    """T32_ReadBreakpointObj: 参数错误"""
    code = 0x1091
    message = "T32_ReadBreakpointObj 参数错误"


class T32ReadBreakpointObjNotFoundError(T32BreakpointError):
    """T32_ReadBreakpointObj: 断点未找到"""
    code = 0x1092
    message = "断点未找到（读取）"


class T32WriteBreakpointObjFailedError(T32BreakpointError):
    """T32_WriteBreakpointObj: 设置断点失败"""
    code = 0x10a1
    message = "设置断点失败"


# ----------------------------------------------------------------------------
# MMU 地址转换相关错误
# ----------------------------------------------------------------------------

class T32MmuTranslationError(T32FunctionError):
    """MMU 地址转换相关错误"""
    pass


class T32QueryAddressObjMmuTranslationFailedError(T32MmuTranslationError):
    """T32_QueryAddressObjMmuTranslation: 转换失败"""
    code = 0x10b0
    message = "MMU 地址转换失败"


# ============================================================================
# note 错误码映射字典
# ============================================================================
@lru_cache(maxsize=16)
def error_mapping(error_code: int):
    for cls in T32Error.__subclasses__():
        for subclass in cls.__subclasses__():
            if getattr(subclass, "code", None) == error_code:
                return subclass
        if getattr(cls, "code", None) == error_code:
            return cls
    return None
