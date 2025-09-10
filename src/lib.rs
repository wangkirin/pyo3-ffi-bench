use pyo3::prelude::*;
use std::time::Instant; // 导入 Instant

/// 场景 A: 简单计算 - 两个 i64 相加
#[pyfunction]
fn sum_as_i64(a: i64, b: i64) -> i64 {
    a + b
}

/// 场景 B: 复杂数据处理 - 计算 Vec<f64> 的总和
#[pyfunction]
fn sum_list_of_floats(data: Vec<f64>) -> f64 {
    data.iter().sum()
}

/// 场景 C: 新增函数，返回结果和内部执行时间
/// PyO3 会自动将 Rust 的元组 (f64, u128) 转换为 Python 的 tuple
#[pyfunction]
fn sum_list_of_floats_with_timing(data: Vec<f64>) -> (f64, u128) {
    // 1. 在核心计算开始前记录时间点
    let start = Instant::now();

    // 2. 执行核心计算
    let sum = data.iter().sum();

    // 3. 计算经过的时间
    let duration = start.elapsed();

    // 4. 返回计算结果和纳秒级的耗时
    (sum, duration.as_nanos())
}


/// 将 Rust 函数组合成一个 Python 模块
#[pymodule]
fn pyo3_ffi_benchmark(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_i64, m)?)?;
    m.add_function(wrap_pyfunction!(sum_list_of_floats, m)?)?;
    // 将新函数也添加到模块中
    m.add_function(wrap_pyfunction!(sum_list_of_floats_with_timing, m)?)?;
    Ok(())
}