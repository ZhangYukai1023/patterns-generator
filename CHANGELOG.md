# Changelog

## 2026-06-23

### Added
- **菱形网格 (Diamond Grid) 图案** (`patterns/others.py:generate_diamond_grid`)
  - 新增 `others` 类别下第三种图案，补全需求文档中的遗漏
  - 密集模式：菱形周期性平铺，cell=2×hp，菱形直径=hp，间距比 1:1
  - 孤立模式：单个菱形居中，直径=hp
  - 使用 Manhattan 距离 (`|x|+|y| <= radius`) 实现菱形掩码，纯 numpy 计算
  - 支持旋转（复用 OTHERS_ANGLES = [0:5:180]°）

### Changed
- **Pattern 注册改用 dataclass** (`generate.py`)
  - 原 8 元组 `(folder, dense_label, prefix, subtype, size, angle, has_rotation, gen_fn)`
    替换为 `Pattern` dataclass，提升可读性和 IDE 支持
- **缓存 `_get_sizes()` 结果** (`generate.py`)
  - 通过 `_cached_sizes()` 惰性缓存，避免 7 次重复计算
- **提取 `_rotate_and_crop()` 函数** (`generate.py`)
  - 旋转 + 中心裁剪逻辑从 `generate_all()` 主循环中提取为独立函数
- **优化 `generate_all()` 主循环**
  - 使用 `Pattern` 对象属性替代元组拆包，代码更清晰
  - 将 `needs_expanded` 判断提前为局部变量，避免重复计算

### No Change
- `utils.py` — 功能完整，接口未改
- `config.py` — 配置结构未改（diamond grid 复用 `OTHERS_ANGLES`）
- `.gitignore` — 不变
