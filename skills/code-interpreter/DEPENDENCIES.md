# code-interpreter Dependencies

## 二进制依赖
- `python3`: macOS 自带，或 `brew install python`
  - 推荐版本: 3.10+
  - 验证: `python3 --version`

## Python 包依赖（按需安装）
- `pandas`: 数据分析
- `numpy`: 数值计算
- `matplotlib`: 可视化
- `pdfminer.six`: PDF 文本提取

安装: `pip3 install pandas numpy matplotlib pdfminer.six`

## 运行时依赖
- 本地沙盒执行环境
- 无网络限制（但涉及网络请求需确认）
