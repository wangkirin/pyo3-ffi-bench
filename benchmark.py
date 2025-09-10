import timeit
import time
import pyo3_ffi_benchmark # 导入我们刚刚编译的 Rust 模块

# --- 定义纯 Python 的对比函数 ---

def python_sum_as_i64(a, b):
    """场景 A 的纯 Python 实现"""
    return a + b

def python_sum_list_of_floats(data):
    """场景 B 的纯 Python 实现"""
    return sum(data)

# --- 准备测试数据 ---
NUMBER_OF_CALLS_SIMPLE = 1_000_000 # 对于简单函数，需要大量调用才能看到差异
NUMBER_OF_CALLS_COMPLEX = 1_000   # 对于复杂函数，调用次数可以少一些

LIST_SIZE = 100_000
float_list = [float(i) for i in range(LIST_SIZE)]

print("--- FFI 性能损耗测量 ---")
print(f"简单函数调用次数: {NUMBER_OF_CALLS_SIMPLE:,}")
print(f"复杂函数调用次数: {NUMBER_OF_CALLS_COMPLEX:,}")
print(f"列表/Vec 大小: {LIST_SIZE:,}\n")

# --- 场景 A: 简单整数相加 ---
print("--- 场景 A: 简单整数相加 (a + b) ---")

# 1. 纯 Python
t_python_simple = timeit.timeit(
    "python_sum_as_i64(10, 20)",
    globals=globals(),
    number=NUMBER_OF_CALLS_SIMPLE
)
print(f"纯 Python:         {t_python_simple:.6f} 秒")

# 2. PyO3 调用 Rust
t_rust_simple = timeit.timeit(
    "pyo3_ffi_benchmark.sum_as_i64(10, 20)",
    globals=globals(),
    number=NUMBER_OF_CALLS_SIMPLE
)
print(f"PyO3 -> Rust:      {t_rust_simple:.6f} 秒")

overhead_simple = (t_rust_simple - t_python_simple) / NUMBER_OF_CALLS_SIMPLE
overhead_t_python_simple =  t_python_simple / NUMBER_OF_CALLS_SIMPLE
overhead_t_rust_simple =  t_rust_simple / NUMBER_OF_CALLS_SIMPLE
# Python 函数调用本身也有开销，我们这里测量的是相对开销
ffi_factor_simple = t_rust_simple / t_python_simple
print(f"性能比较: PyO3 调用比纯 Python 慢 {ffi_factor_simple:.2f} 倍")
print(f"单次平均调用的纯Python开销 (近似值): {overhead_t_python_simple * 1e9:.2f} 纳秒\n")
print(f"单次平均调用的Rust开销 (近似值): {overhead_t_rust_simple * 1e9:.2f} 纳秒\n")
print(f"单次调用的 FFI 开销 (近似值): {overhead_simple * 1e9:.2f} 纳秒\n")


# --- 场景 B: 浮点数列表求和 ---
print("--- 场景 B: 计算 {} 个浮点数的总和 ---".format(LIST_SIZE))

# 1. 纯 Python
t_python_complex = timeit.timeit(
    "python_sum_list_of_floats(float_list)",
    globals=globals(),
    number=NUMBER_OF_CALLS_COMPLEX
)
print(f"纯 Python:         {t_python_complex:.6f} 秒")

# 2. PyO3 调用 Rust
t_rust_complex = timeit.timeit(
    "pyo3_ffi_benchmark.sum_list_of_floats(float_list)",
    globals=globals(),
    number=NUMBER_OF_CALLS_COMPLEX
)
print(f"PyO3 -> Rust:      {t_rust_complex:.6f} 秒")

ffi_factor_complex = t_rust_complex / t_python_complex
if t_rust_complex < t_python_complex:
    speedup = t_python_complex / t_rust_complex
    print(f"性能比较: PyO3 -> Rust 比纯 Python 快 {speedup:.2f} 倍")
else:
    slowdown = t_rust_complex / t_python_complex
    print(f"性能比较: PyO3 -> Rust 比纯 Python 慢 {slowdown:.2f} 倍")

overhead_complex_per_call = (t_rust_complex - t_python_complex) / NUMBER_OF_CALLS_COMPLEX
print(f"单次调用的总开销差异 (包含计算): {overhead_complex_per_call * 1e6:.2f} 微秒\n")



# --- 场景 C: 精确分离 FFI 开销 ---
print(f"--- 场景 C: 精确测量 {NUMBER_OF_CALLS_COMPLEX} 次调用的时间分布 ---")

# 我们将手动计时以分离时间
total_rust_internal_duration_ns = 0
final_result = 0.0

# 1. 测量 Python 侧的总时间
start_python_total_time = time.perf_counter()

for _ in range(NUMBER_OF_CALLS_COMPLEX):
    # 调用新函数，它会返回结果和 Rust 内部耗时
    result, rust_duration_ns = pyo3_ffi_benchmark.sum_list_of_floats_with_timing(float_list)
    total_rust_internal_duration_ns += rust_duration_ns
    final_result = result # 只是为了确保变量被使用

end_python_total_time = time.perf_counter()

# --- 计算三个核心时间 ---

# 时间1: Python 测量的总时间 (T_total)
total_python_time_s = end_python_total_time - start_python_total_time

# 时间2: Rust 内部执行时间 (T_rust)
total_rust_internal_time_s = total_rust_internal_duration_ns / 1_000_000_000.0

# 时间3: FFI 开销时间 (T_ffi)
total_ffi_overhead_s = total_python_time_s - total_rust_internal_time_s

# --- 打印结果 ---

print("\n--- 性能分析 (总计) ---")
print(f"Python 测量的总时间 (T_total): {total_python_time_s:.6f} 秒")
print(f"Rust 内部执行时间  (T_rust) : {total_rust_internal_time_s:.6f} 秒")
print(f"FFI 开销时间        (T_ffi)  : {total_ffi_overhead_s:.6f} 秒")

print("\n--- 性能分析 (单次调用平均) ---")
avg_total_ms = (total_python_time_s / NUMBER_OF_CALLS_COMPLEX) * 1000
avg_rust_ms = (total_rust_internal_time_s / NUMBER_OF_CALLS_COMPLEX) * 1000
avg_ffi_ms = (total_ffi_overhead_s / NUMBER_OF_CALLS_COMPLEX) * 1000
print(f"平均总耗时:   {avg_total_ms:.6f} 毫秒")
print(f"平均Rust耗时: {avg_rust_ms:.6f} 毫秒")
print(f"平均FFI开销:  {avg_ffi_ms:.6f} 毫秒")

if total_python_time_s > 0:
    rust_percentage = (total_rust_internal_time_s / total_python_time_s) * 100
    ffi_percentage = (total_ffi_overhead_s / total_python_time_s) * 100
    print(f"\n在总时间中，Rust 核心计算占 {rust_percentage:.2f}%, FFI 开销占 {ffi_percentage:.2f}%")
