## Reference
https://cloud.tencent.com/developer/article/2277479
https://zhuanlan.zhihu.com/p/479180596
## Prerequisite knowledge
1.PriorityQueue
- Hoạt động tương tự cấu trúc Queue nhưng nó khác ở chỗ dữ liệu bên trong hàng đợi được sặp xếp theo `Comparator` (default là Min-Heap: nhỏ nhất nằm đầu hàng đợi)

2. TransformingComparator
```java
/**
 * @param transformer what will transform the arguments to compare
 * @param decorated the decorated Comparator
 */
public TransformingComparator(final Transformer<? super I, ? extends O> transformer,
                              final Comparator<O> decorated) {
    this.decorated = decorated;
    this.transformer = transformer;
}

//-----------------------------------------------------------------------
/**
 * Returns the result of comparing the values from the transform operation.
 *
 * @param obj1 the first object to transform then compare
 * @param obj2 the second object to transform then compare
 * @return negative if obj1 is less, positive if greater, zero if equal
 */
public int compare(final I obj1, final I obj2) {
    final O value1 = this.transformer.transform(obj1);
    final O value2 = this.transformer.transform(obj2);
    return this.decorated.compare(value1, value2);
}
```