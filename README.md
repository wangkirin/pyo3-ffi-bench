# Python/Rust FFI 性能基准测试 (使用 PyO3)



## 核心思路

将总调用时间分解为三个部分来分析：

1.  **Python 测量的总时间 (`T_total`)**: 从 Python 发起调用到收到返回值的完整耗时。
2.  **Rust 内部执行时间 (`T_rust`)**: Rust 函数内部执行核心计算逻辑的纯粹耗时。
3.  **FFI 开销 (`T_ffi`)**: 两者之差 (`T_total - T_rust`)，主要包括函数调用链的开销和 Python 对象与 Rust 类型之间相互转换的成本。

## 环境要求

- **Rust**: 最新稳定版 (通过 `rustup` 安装)
- **Python**: 3.8 或更高版本
- **maturin**: 用于构建和打包 Rust-Python 项目的工具。

## 安装与设置

1.  **进入仓库**
    ```bash
    cd pyo3-ffi-benchmark
    ```

2.  **创建并激活 Python 虚拟环境**
    ```bash
    # 创建 .venv 虚拟环境
    python -m venv .venv

    # 激活 venv (Linux/macOS)
    source .venv/bin/activate

    ```

3.  **安装 maturin**
    ```bash
    pip install maturin
    ```

4.  **编译 Rust 模块**
    此命令会编译 Rust 代码并将其以“可编辑”模式安装到当前的虚拟环境中。
    ```bash
    maturin develop
    ```
    > **注意**: 每次修改 `src/lib.rs` 中的 Rust 代码后，都必须重新运行此命令以使更改生效。

## 运行benchmark

直接运行 `benchmark.py` 脚本即可开始测试：
```bash
python benchmark.py
```

