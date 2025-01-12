
# tmux normalize layout

由于 tmux 是按当前终端宽高而非窗格划分比例维护布局，在终端窗口经过多次大小调整之后容易出现错位。本插件能够按照不同策略微调当前布局，使布局重新对齐。

**暂不支持 `pane-border-status bottom`。**

调整策略：

1. **均分/equal**。每一级窗格划分都均分宽度或高度。
2. **网格/grid**。所有分隔线都落在最简的均匀网格上。
3. **适应/fit**。每一级划分都寻找最接近的简单比例。例如 `[12, 18, 30] => [1, 2, 3], [13, 17, 30] => [1, 1, 2]`。

均分和网格两种策略的差异可以参考以下图例：

```
均分：
+-----+-----+
|     |     |
|     |     |
|     |     |
+     +--+--+
|     |  |  |
+     +  +--+
|     |  |  |
+-----+--+--+


适应：
+--+-----+
|  |     |
+  +--+--+
|  |  |  |
+  +  +--+
|  |  |  |
+--+--+--+
```