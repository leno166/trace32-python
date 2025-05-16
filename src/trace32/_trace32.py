"""
@文件: _trace32.py
@作者: 雷小鸥
@日期: 2025/5/6 15:14
@描述: 基本的与 c 交互的 api
@许可: MIT License
@版本: Version 1.0
"""

import sys
import os
import platform
from ctypes import *
from enum import Enum

from .errors import *


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

match (platform.system(), sizeof(c_void_p)):
    case ("Windows" | "CYGWIN"), 4:
        __t32__ = CDLL(os.path.join(CURRENT_DIR, 'lib', 't32api.dll'))
    case ("Windows" | "CYGWIN"), _:
        __t32__ = CDLL(os.path.join(CURRENT_DIR, 'lib', 't32api64.dll'))
    case "Darwin", 4:
        __t32__ = CDLL(os.path.join(CURRENT_DIR, 'lib', 't32api.dylib'))
    case _, 4:
        __t32__ = CDLL(os.path.join(CURRENT_DIR, 'lib', 't32api64.so'))
    case _, _:
        __t32__ = CDLL(os.path.join(CURRENT_DIR, 'lib', 't32api64.so'))


def set_error_hook() -> None:
    """
    最主要的错误处理, 在 python 执行器抛出错误后执行. 
    防止与 TRACE32 socket 出现问题. 
    """
    def handler(exc_type, exc_value, exc_traceback):
        __t32__.T32_Exit()
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = handler


set_error_hook()

_channels = {}


class DeviceType(Enum):
    OS = 0
    ICE = 1
    ICD = 1  # 注意：这里ICE和ICD共享同一个值，Enum允许这样做但会有一些行为上的影响

    def __str__(self):
        type_names = {
            self.OS: "Operating System",
            self.ICE: "In-Circuit Emulator",
            self.ICD: "In-Circuit Debugger",
        }
        return type_names[self]


class T32:
    # --------------------------------------------------------------------------
    # note 基本 API 函数
    # --------------------------------------------------------------------------
    @staticmethod
    def config(key: str, value: str) -> None:
        """
        配置驱动程序

        :param key: 配置项名称
        :param value: 配置项值

        输入参数举例：
            key：NODE
            value：定义 TRACE32 显示驱动程序在哪个主机上运行。默认值为 "localhost"。

            key：PACKLEN
            value：指定用于 UDP 的最大数据包长度。该值不得大于 1024，并且必须适合 "config.t32" 文件中定义的值。TCP 无作用。

            key：TIMEOUT
            value：UDP 超时。定义 API 函数的通信超时时间（以秒为单位）。
                默认值为 5 秒。如果 TRACE32 在此时间内未应答，则 API 函数将返回 T32_COM_RECEIVE_FAIL。TCP 无作用。

            key：HOSTPORT
            value：定义用于接收的 UDP 端口。默认情况下，这是自动分配的。仅当确实需要设置特定的接收端口时，才使用此设置。TCP 无作用。
        """
        err = __t32__.T32_Config((key + "=").encode("GBK"), value.encode("GBK"))
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def init() -> None:
        """
        此函数初始化驱动程序并建立与 TRACE32 显示驱动程序的连接。如果返回零，则表示连接设置成功。
        """
        err = __t32__.T32_Init()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def attach(device_specifier: int | DeviceType) -> None:
        """
        连接 TRACE32 设备

        :param device_specifier: 设备标识符

            T32_DEV_OS: 0 -> 在 TRACE32 的基本操作系统（简称“::”）环境下，默认情况下会禁用所有特定于设备的命令。
            T32_DEV_ICD: 1 -> 调试器 （"B::"），包括基本 OS 命令
            T32_DEV_ICE: 1 -> 与 T32_DEV_ICD 相同
        """
        if isinstance(device_specifier, DeviceType):
            device_specifier = device_specifier.value
        err = __t32__.T32_Attach(device_specifier)
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def terminate(exit_code: int) -> None:
        """
        使用此命令可终止连接的 TRACE32 实例。

        :param exit_code:  TRACE32 实例终止时将要返回给操作系统的退出码, 退出码通常用于指示程序结束的状态
        """
        err = __t32__.T32_Terminate(exit_code)
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def exit() -> None:
        """
        关闭 python 与 TRACE32 的 socket 连结
        """
        err = __t32__.T32_Exit()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def ping() -> None:
        """
        ping TRACE32
        """
        err = __t32__.T32_Ping()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def nop() -> None:
        """
        向 TRACE32 显示驱动程序发送一条空消息并等待其应答。
        """
        err = __t32__.T32_Nop()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def nop_ex(length: int, option: int) -> None:
        """
        :param length: 空消息长度
        :param option: 选项
        """
        err = __t32__.T32_NopEx(length, option)
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def nop_fail() -> None:
        """
        向 TRACE32 显示驱动程序发送一条空的失败消息并等待其应答。
        """
        err = __t32__.T32_NopFail()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def cmd(commands: str) -> None:
        """
        执行 TRACE32 命令

        使用此函数，将 TRACE32 命令传递给 TRACE32 执行。允许使用任何有效的 TRACE32 命令，包括通过 DO 命令的 *.cmm 脚本传值

        当通过 “DO” 命令执行脚本时，函数将立即返回，而不是等待脚本结束。你可以使用 get_practice_state() 主动等待脚本结束。

        在命令执行过程中发生的错误不会立即报告。要获取更详细的错误信息，请调用 get_message() 并检查消息类型。

        :param commands: 要执行的 TRACE32 命令字符串
        """
        err = __t32__.T32_Cmd(commands.encode("GBK"))
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def cmd_f(commands: str, *args) -> None:
        """
        执行带格式说明符的 PRACTICE 命令

        使用此函数，将 TRACE32 命令传递给 TRACE32 执行。允许使用任何有效的 PRACTICE 命令，包括通过 DO 命令的 *.cmm 脚本传值

        当通过 “DO” 命令执行脚本时，函数将立即返回，而不是等待脚本结束。你可以使用 get_practice_state() 主动等待脚本结束。

        在命令执行过程中发生的错误不会立即报告。要获取更详细的错误信息，请调用 get_message() 并检查消息类型。

        :param commands: 要执行的 PRACTICE 命令字符串。可以包含格式化占位符（如 %d, %s, %x 等）
        :param args: 可变参数列表，用于填充命令中的格式化部分。必须与前面命令字符串中的格式化占位符数量和类型匹配。
        """
        err = __t32__.T32_Cmd_f(
            commands.encode("GBK"),
            *(arg.encode("GBK") if isinstance(arg, str) else arg for arg in args),
        )
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def cmd_win() -> None:
        err = __t32__.T32_CmdWin()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def print(string: str, *args) -> None:
        """
        带格式打印到 TRACE32

        :param string: 要打印到 TRACE32 AREA窗口的文本, 可带格式说明符。
        :param args: 可变参数列表，用于填充命令中的格式化部分。必须与前面字符串中的格式化占位符数量和类型匹配。 0 否则错误
        """
        err = __t32__.T32_Printf(
            string.encode("GBK"),
            *(arg.encode("GBK") if isinstance(arg, str) else arg for arg in args),
        )
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def stop() -> None:
        """
        停止 PRACTICE 脚本

        如果 PRATICE 脚本正在运行，则将被停止；
        如果应用程序在 ICE 中运行，则不受此命令影响。要停止应用程序，请使用 T32_Break
        """
        err = __t32__.T32_Stop()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def get_practice_state() -> int:
        """
        检查 PRACTICE 脚本是否正在运行

        返回 PRACTICE 运行状态。使用此命令轮询通过 T32_Cmd 启动的 PRACTICE 脚本是否结束运行

        :return: state
            0: 未运行；
            1: 运行；
            2: 打开对话窗口
        """
        state = c_int(0)
        err = __t32__.T32_GetPracticeState(byref(state))
        if error_mapping(err):
            raise error_mapping(err)()
        return state.value

    @staticmethod
    def eval_get() -> int:
        """
        获取评估结果

        某些 PRACTICE 命令（例如 Eval）和函数会设置一个全局变量来存储返回值、表达式结果或错误状态。此值始终与所使用命令相关。
        函数 eval_get 读取此值。

        note：此功能仅在连接到设备可用

        :return: eval_res: 评估结果缓存
        """
        eval_res = c_uint32(0)
        err = __t32__.T32_EvalGet(byref(eval_res))
        if error_mapping(err):
            raise error_mapping(err)()
        return eval_res.value

    @staticmethod
    def eval_get_string() -> str:
        """
        获取评估结果字符串

        某些 PRACTICE 命令（例如 Eval）和函数会设置一个全局变量来存储返回值、表达式结果或错误状态。此值始终与所使用命令相关。
        函数 eval_get_string 返回字符串形式的最后一次结果

        note：此功能仅在连接到设备可用

        :return: eval_res_str: 评估结果缓存
        """
        buffer = create_string_buffer(1024)
        err = __t32__.T32_EvalGetString(byref(buffer))
        if error_mapping(err):
            raise error_mapping(err)()
        return buffer.value.decode("GBK")

    @staticmethod
    def get_message() -> None | tuple[str, int]:
        """
        大多数 PRACTICE 命令将消息写入 TRACE32 的消息行和 AREA 窗口。此函数读取消息行的内容和消息的类型。

        :return: 0 | （message, status)

            message:
                消息字符串。但它总是为空，只有状态不为 0 时有效。

            status:

                0 : OK，通信成功；必须忽略返回的消息。
                1 : 一般信息
                2 : 错误
                8 : 状态信息
                16: 错误信息
                32: 临时显示
                64: 临时信息
        """
        message, status = create_string_buffer(256), c_uint16(0)
        err = __t32__.T32_GetMessage(message, byref(status))
        if error_mapping(err):
            raise error_mapping(err)()
        if status.value == 0:
            return None
        return message.value.decode("GBK"), status.value

    @staticmethod
    def get_trigger_message() -> None:
        """
        弃用
        """
        err = __t32__.T32_GetTriggerMessage()
        if error_mapping(err):
            raise error_mapping(err)()

    # @staticmethod
    # def get_channel_size() -> None:
    #     err = __t32__.T32_GetChannelSize()
    #     if error_mapping(err):
    #         raise error_mapping(err)()
    #
    # @staticmethod
    # def get_channel_defaults() -> None:
    #     err = __t32__.T32_GetChannelDefaults()
    #     if error_mapping(err):
    #         raise error_mapping(err)()

    @staticmethod
    def set_channel(ip: str, port: int) -> None:
        """
        设置或切换通道连接到不同的仿真器

        比如：多核调试
        """
        if (ip, port) in _channels:
            err = __t32__.T32_SetChannel(_channels[(ip, port)])
            if error_mapping(err):
                raise error_mapping(err)()
            return

        # 1. 获取结构体大小
        size = __t32__.T32_GetChannelSize()
        if size <= 0:
            raise error_mapping(size)()

        # 2. 分配内存
        buffer = create_string_buffer(size)

        # 3. 初始化为默认值
        err = __t32__.T32_GetChannelDefaults(buffer)
        if error_mapping(err):
            raise error_mapping(err)()

        # 4. 切换到新 channel
        err = __t32__.T32_SetChannel(buffer)
        if error_mapping(err):
            raise error_mapping(err)()

        # 5. 缓存这个 channel，后续可复用
        _channels[(ip, port)] = buffer

    @staticmethod
    def api_lock(wait: int) -> bool:
        """
        函数用于锁定对 TRACE32 Remote API 的访问，确保在多客户端环境中只有一个客户端可以执行命令。
        这对于避免多个客户端同时尝试访问或修改同一 TRACE32 实例时可能出现的竞争条件非常重要。

        note TRACE32 Remote API 服务器端的 TIMEOUT= 设置必须增加到大于 n 的值，以允许这种超时行为生效。

        :param wait: 锁定命令的超时时间，以毫秒为单位。

            如果 Timeout 设置为 0，则函数会立即返回：
            如果 Timeout 设置为大于 0 的值 n，则函数将等待最多 n 毫秒来获取锁：

        :return: 成功 | 失败
        """
        res = __t32__.T32_APILock(wait)
        if res == 0:
            return True
        if res == 123:
            return False

        raise error_mapping(res)()

    @staticmethod
    def api_unlock() -> None:
        """
        解锁 TRACE32 Remote API，允许其他客户端访问
        """
        err = __t32__.T32_APIUnlock()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def get_api_revision() -> int:
        """
        返回应用程序端 Remote API（源文件或库）的修订号。它不会报告 TRACE32 软件的修订版号。
        """
        revision = c_uint32(0)
        err = __t32__.T32_GetApiRevision(byref(revision))
        if error_mapping(err):
            raise error_mapping(err)()
        return revision.value

    @staticmethod
    def get_socket_handle() -> int:
        """
        此函数返回一个指针，该指针指向 API 创建的套接字的句柄，以便与 TRACE32 通信。

        例如，它可用于注册异步通知以在此套接字上发送或接收数据。

        :return: socket handle
        """
        handle = c_int(0)
        err = __t32__.T32_GetSocketHandle(byref(handle))
        if error_mapping(err):
            raise error_mapping(err)()
        return handle.value

    # --------------------------------------------------------------------------
    # note 调试器相关函数
    # --------------------------------------------------------------------------

    @staticmethod
    def go() -> None:
        """
        开始调试。该函数将在仿真启动后立即返回。（也就是 TRACE32 上 ▶按钮）

        get_state 函数可用于等待下一个断点。

        在仿真运行时，允许使用所有其他命令。
        """
        err = __t32__.T32_Go()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def break_target() -> None:
        """
        中断实时仿真。（也就是 TRACE32 上 ⏸按钮）

        可用于异步
        """
        err = __t32__.T32_Break()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def step() -> None:
        """
        单步调试。
        """
        err = __t32__.T32_Step()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def set_step_mode(mode: str, jump_func: bool) -> None:
        """
        步进调试

        :param mode: 汇编 | 高级 | 混合 | asm | hll | mix | ASM | HLL | MIX | 0 | 1 | 2
        :param jump_func: 进入函数 | 跳过函数

            0: 汇编语言级步进
            1: 高级语言级步进
            2: 混合模式（汇编语言级步进同时显示对应的高级语言代码行）
            最高位：
                0: 进入函数内部
                1: 跳过函数调用
        """
        step_mode = c_int(0)
        step_mode.value = {
            "汇编": 0,
            "高级": 1,
            "混合": 2,
            0: 0,
            1: 1,
            2: 2,
            "ASM": 0,
            "HLL": 1,
            "MIX": 2,
            "asm": 0,
            "hll": 1,
            "mix": 2,
        }[mode] | ((1 << 7) if jump_func else (0 << 7))

        err = __t32__.T32_StepMode(step_mode)
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def reset_cpu() -> None:
        """
        重置 目标CPU。

        通过执行 PRACTICE 命令 SYStem.UP, Register.RESet 来完成的

        note 可以在目标软件崩溃后获取控制权
        """
        err = __t32__.T32_ResetCPU()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def set_mode(mode) -> None:
        """
        设置 TRACE32 Data.List 窗口的显示模式

        :param mode: 汇编 | 高级 | 混合 | asm | hll | mix | ASM | HLL | MIX | 0 | 1 | 2
        """
        err = __t32__.T32_SetMode(
            {
                "汇编": 0,
                "高级": 1,
                "混合": 2,
                0: 0,
                1: 1,
                2: 2,
                "ASM": 0,
                "HLL": 1,
                "MIX": 2,
                "asm": 0,
                "hll": 1,
                "mix": 2,
            }[mode]
        )
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def get_cpu_info() -> tuple[str, bool, str]:
        """
        获取目标CPU的信息

        :return: cpu_str, has_fpu, endian

            cpu_str: CPU 类型和系列的字符串
            has_fpu: 是否有浮点单元
            endian: 大端 | 小端
        """
        cpu_str = c_char(b"")
        has_fpu, endian, tmp = c_uint16(0), c_uint16(0), c_uint16(0)

        err = __t32__.T32_GetCpuInfo(
            byref(cpu_str), byref(has_fpu), byref(endian), byref(tmp)
        )
        if error_mapping(err):
            raise error_mapping(err)()

        return (
            cpu_str.value.decode("ascii"),
            bool(has_fpu.value),
            "little" if endian.value else "big",
        )

    @staticmethod
    def get_state() -> int:
        """
        获取目标CPU的状态

        :return: 状态码

            0: 调试系统已关闭
            1:
                （仅限ICE）调试系统停止、目标不进行周期（无访问权限）
                （仅限 Intel x86/x64 调试器）目标处于启动停滞状态
            2: 目标已停止运行（Break）
            3: 目标正在运行（Go）
        """
        state = c_int(0)
        err = __t32__.T32_GetState(byref(state))
        if error_mapping(err):
            raise error_mapping(err)()
        return state.value

    @staticmethod
    def read_memory(address: int, access: int, size: int) -> bytes:
        """
        从目标CPU读取内存

        :param address: 字节地址（需根据架构预处理：字寻址需×字长，寄存器需×宽度）
        :param access: 访问类型（若已用T32_SetMemoryAccessClass设置，此参数被忽略）
        :param size: 要读取的字节数
        :return: 读取的字节数据
        """
        buffer = (c_ubyte * size)()
        err = __t32__.T32_ReadMemory(
            c_uint32(address), c_int(access), buffer, c_size_t(size)
        )
        if error_mapping(err):
            raise error_mapping(err)()
        return bytes(buffer)

    @staticmethod
    def write_memory(address: int, access: int, content: int) -> None:
        """
        向目标CPU写入内存

        :param address: 字节地址（需根据架构预处理：字寻址需×字长，寄存器需×宽度）
        :param access: 访问类型（若已用T32_SetMemoryAccessClass设置，此参数被忽略）
        :param content: 要写入的整数值，写入值与输入样式相同。0b...
        """
        size = (content.bit_length() + 7) // 8 or 1
        buffer = content.to_bytes(size, byteorder="big", signed=False)
        err = __t32__.T32_WriteMemory(
            c_uint32(address), c_int(access), (c_ubyte * size)(*buffer), c_size_t(size)
        )
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def write_memory_pipe() -> None:
        """
        弃用
        """
        # __t32__.T32_WriteMemoryPipe()
        pass

    @staticmethod
    def read_memory_ex() -> None:
        """
        未支持
        """
        # __t32__.T32_ReadMemoryEx()
        pass

    @staticmethod
    def write_memory_ex() -> int:
        """
        未支持
        """
        # __t32__.T32_WriteMemoryEx()
        pass

    @staticmethod
    def set_memory_access_class() -> int:
        """ 
        未支持
        """
        # __t32__.T32_SetMemoryAccessClass()
        pass

    @staticmethod
    def get_ram(start: int, access: int) -> int:
        """ 
        获取内存映射, 仅限仿真

        :param start: None | 0, 如果是0则强制从此开始位置搜索.
        :param access: 访问方式
        :return: None | (start, end)
        """
        start_address, end_address, access_type = c_uint32(start), c_uint32(0), c_uint16(access)
        err = __t32__.T32_GetRam(byref(start_address), byref(end_address), byref(access_type))
        if error_mapping(err):
            raise error_mapping(err)()
        return None if access_type.value == 0 else (start_address.value, end_address.value)

    @staticmethod
    def get_source(address: int) -> int:
        """ 
        从内存地址返回给定的源文件 文件名和所在行

        :return: (file, line)
        """
        file, line = create_string_buffer(256), c_uint32(0)
        err = __t32__.T32_GetSource(c_uint32(address), file, byref(line))
        if error_mapping(err):
            raise error_mapping(err)()
        return file.value.decode("GBK"), line.value

    @staticmethod
    def get_selected_source() -> int:
        """ 
        此函数请求 TRACE32/PowerView 中所选源行的源文件名和行号。

        可以在任何包含源文件的 TRACE32 PowerView 窗口中选择源行（例如“A.List”或“Data.List”）。

        如果之前没有进行选择，或者没有选择源行，则函数返回 filename 设置为空字符串 （filename[0]=='\0'）。
        """
        file, line = create_string_buffer(256), c_int32(0)
        err = __t32__.T32_GetSelectedSource(byref(file), file)
        if error_mapping(err):
            raise error_mapping(err)()
        return file.value.decode("GBK"), line.value

    @staticmethod
    def get_symbol(symbol: str) -> tuple[int, int, int]:
        """ 
        根据符号名获取其地址, 大小, 保留字段

        符号可以使 代码中定义的变量, 函数

        :param symbol: 要查询的符号名（如"variable"或源行"\\file\\12"）
        :return: (地址, 大小, 保留值)
        """
        address, size, reserved = c_uint32(0), c_uint32(0), c_uint32(0)
        err = __t32__.T32_GetSymbol(byref(symbol), byref(address), byref(size), byref(reserved))
        if error_mapping(err):
            raise error_mapping(err)()
        return address.value, size.value, reserved.value

    @staticmethod
    def get_symbol_from_address(address: int) -> str:
        """ 
        获取指定地址的符号名(变量或函数名)

        :param address: 要查询的地址
        :return: 符号名
        """
        symbol = create_string_buffer(256)
        err = __t32__.T32_GetSymbolFromAddress(symbol, c_uint32(address), c_int(256))
        if error_mapping(err):
            raise error_mapping(err)()
        return symbol.value.decode("GBK")
    
    @staticmethod
    def read_variable_string(symbol: str) -> str:
        """
        读取指定符号的值的字符串形式

        :param symbol: 符号名
        :return: 符号的字符串值
        """
        buffer = create_string_buffer(256)
        err = __t32__.T32_ReadVariableString(symbol.encode("GBK"), buffer, c_int(sizeof(buffer)))
        if error_mapping(err):
            raise error_mapping(err)()
        return buffer.value.decode("GBK")


    @staticmethod
    def read_variable_value(symbol: str) -> int:
        """
        读取指定符号的整形值

        :param symbol: 符号名
        :return: 符号的整形值
        """
        l_value, h_value = c_uint32(), c_uint32()
        err = __t32__.T32_ReadVariableValue(symbol.encode('GBK'), byref(l_value), byref(h_value))
        if error_mapping(err):
            raise error_mapping(err)()
        return h_value.value << 32 | l_value.value

    @staticmethod
    def write_variable_value(symbol: str, value: int) -> int:
        """ 
        向指定符号(函数 变量)写入整数值

        :param symbol: 符号名
        :param value: 要写入的值
        """
        if not (0 <= value <= 0xFFFFFFFFFFFFFFFF):
            raise ValueError("值超出64位整形范围")
        l_value, h_value = c_uint32(value & 0xFFFFFFFF), c_uint32(value >> 32)
        err = __t32__.T32_WriteVariableValue(symbol.encode('GBK'), byref(l_value), byref(h_value))
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def get_window_content(cmd: str, fmt: str = 'csv', size: int = 1024) -> str:
        """ 
        获取 TRACE32 的窗口内容(支持分块读取)

        :param cmd: 要执行的命令
        :param fmt: 输出格式 asc | asce | ascp | csv | xml
        """
        offset, content = 0, bytearray()
        buffer = create_string_buffer(size)
        while True:
            byte_read = __t32__.T32_GetWindowContent(
                cmd.encode('GBK'), buffer, c_uint32(size), c_uint32(offset), 
                c_uint32({'asc': 0, 'asce': 1, 'ascp': 2, 'csv': 3, 'xml': 4}[fmt])
                )
            if byte_read == -1:
                return buffer.value.decode("GBK")
            if byte_read < 0 and error_mapping(byte_read):
                raise error_mapping(byte_read)()
            content += buffer.raw[:byte_read]

    @staticmethod
    def read_register_by_name() -> int:
        """ 
        
        """
        err = __t32__.T32_ReadRegisterByName()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def write_register_by_name() -> int:
        """ """
        err = __t32__.T32_WriteRegisterByName()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def read_pp() -> int:
        """ 
        读取程序指针所指向的当前值. 仅在程序停止时有效.

        对于 ICE, 状态为 Emulation stopped (参考 T32_GetState)

        程序指针是指向下一步执行的汇编程序行地址的逻辑指针。与 T32_ReadRegister 不同，此函数完全独立于处理器。

        :return: 当前程序在内存中所指向位置
        """
        pointer = c_uint32(0)
        err = __t32__.T32_ReadPP(byref(pointer))
        if error_mapping(err):
            raise error_mapping(err)()
        return pointer.value

    @staticmethod
    def read_register() -> int:
        """ """
        err = __t32__.T32_ReadRegister()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def write_register() -> int:
        """ """
        err = __t32__.T32_WriteRegister()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def read_breakpoint() -> int:
        """ """
        err = __t32__.T32_ReadBreakpoint()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def write_breakpoint() -> int:
        """ """
        err = __t32__.T32_WriteBreakpoint()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def get_breakpoint_list() -> int:
        """ """
        err = __t32__.T32_GetBreakpointList()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def get_trace_state() -> int:
        """ """
        err = __t32__.T32_GetTraceState()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def read_trace() -> int:
        """ """
        err = __t32__.T32_ReadTrace()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def get_last_error_message() -> int:
        """ """
        err = __t32__.T32_GetLastErrorMessage()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def notify_state_enable() -> int:
        """ """
        err = __t32__.T32_NotifyStateEnable()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def notify_event_enable() -> int:
        """ """
        err = __t32__.T32_NotifyEventEnable()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def check_state_notify() -> int:
        """ """
        err = __t32__.T32_CheckStateNotify()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def notification_pending() -> int:
        """ """
        err = __t32__.T32_NotificationPending()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def get_analyzer_status() -> int:
        """ """
        err = __t32__.T32_AnaStatusGet()
        if error_mapping(err):
            raise error_mapping(err)()

    @staticmethod
    def get_analyzer_record() -> int:
        """ """
        err = __t32__.T32_AnaRecordGet

    # --------------------------------------------------------------------------
    # note 面向对象风格的函数
    # --------------------------------------------------------------------------
    """
        对象接口命名规范说明
        对象类型 <objtype> 命名示例：Buffer（缓冲区）| Address（地址）| Register（寄存器）| Memory（内存）| Symbol（符号）
        对象类型定义：
            对象类型定义: T32_<objtype>Obj 表示一个 <objtype> 类型的对象结构
            
            对象句柄类型定义: T32_<objtype>Handle 表示指向某个 <objtype> 对象的句柄或引用
            
            分配对象：T32_Request<objtype>Obj 
                请求分配一个新的 <objtype> 类型对象 
                可选形式：T32_Request<objtype>Obj<initial>（带初始值分配）
            重新分配对象大小：T32_Resize<objtype>Obj 
            释放对象：T32_Release<objtype>Obj 
                可选形式：T32_ReleaseAllObjects（释放所有对象）
            
            获取对象属性：T32_Get<objtype>Obj<attribute> 获取某个 <objtype> 对象的特定属性
            设置对象属性：T32_Set<objtype>Obj<attribute> 设置某个 <objtype> 对象的特定属性
            复制已有对象：T32_Copy<objtype>Obj 复制一个已有的 <objtype> 对象
            从/向对象复制数据：T32_Copy<what>From/To<objtype>Obj 将某类数据从/到 <objtype> 对象中复制
            
            从目标设备读取数据：T32_Read<objtype>Obj 
            按标识符读取对象：T32_Read<objtype>ObjBy<signifier> 通过某种“标识”来读取 <objtype> 对象
            
            向目标设备写入数据：T32_Write<objtype>Obj
            
            从 TRACE32 查询对象信息：T32_Query<objtype>Obj
            向 TRACE32 发送对象信息：T32_Send<objtype>Obj
    """

    # --------------------------------------------------------------------------
    # note 高速调试（FDX）相关函数
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # note 直接和测试（JTAG）访问端口相关函数
    # --------------------------------------------------------------------------
    param_from_uint32 = __t32__.T32_ParamFromUint32
    bundled_access_alloc = __t32__.T32_BundledAccessAlloc
    bundled_access_execute = __t32__.T32_BundledAccessExecute
    bundled_access_free = __t32__.T32_BundledAccessFree
    direct_access_release = __t32__.T32_DirectAccessRelease
    direct_access_reset_all = __t32__.T32_DirectAccessResetAll
    direct_access_set_info = __t32__.T32_DirectAccessSetInfo
    direct_access_get_info = __t32__.T32_DirectAccessGetInfo
    direct_access_get_timestamp = __t32__.T32_DirectAccessGetTimestamp
    direct_access_user_signal = __t32__.T32_DirectAccessUserSignal
    tap_access_set_info = __t32__.T32_TAPAccessSetInfo
    tap_access_set_info2 = __t32__.T32_TAPAccessSetInfo2
    tap_access_shift_raw = __t32__.T32_TAPAccessShiftRaw
    tap_access_shift_ir = __t32__.T32_TAPAccessShiftIR
    tap_access_shift_dr = __t32__.T32_TAPAccessShiftDR
    tap_access_jtag_reset_with_tms = __t32__.T32_TAPAccessJTAGResetWithTMS
    tap_access_jtag_reset_with_trst = __t32__.T32_TAPAccessJTAGResetWithTRST
    tap_access_set_shift_pattern = __t32__.T32_TAPAccessSetShiftPattern
    tap_access_direct = __t32__.T32_TAPAccessDirect
    dap_access_scan = __t32__.T32_DAPAccessScan
    dap_access_init_swd = __t32__.T32_DAPAccessInitSWD
    dap_ap_access_read_write = __t32__.T32_DAPAPAccessReadWrite
    i2c_access = __t32__.T32_I2CAccess
    direct_access_execute_lua = __t32__.T32_DirectAccessExecuteLua

    # --------------------------------------------------------------------------
    # note lua 脚本相关函数
    # --------------------------------------------------------------------------
    Execute_lua = __t32__.T32_ExecuteLua
