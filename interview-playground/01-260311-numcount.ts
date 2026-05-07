/**
 * 给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出 和为目标值 的那 两个 整数，并返回它们的数组下标。你可以假设每种输入只会对应一个答案，且数组中同一个元素不能使用两遍。你可以按任意顺序返回答案。
    示例：输入：nums = [2,7,11,15], target = 9输出：[0,1]解释：因为 nums [0] + nums [1] = 2 + 7 = 9，所以返回 [0, 1]。
 * @param nums 
 * @param target 
 * @returns 
 */
const findNums = (nums: number[], target: number): number[] => {
    const map = new Map<number,number>()
    for (let i = 0, len = nums.length; i < len; i++) {
        const num = nums[i]
        if (map.has(target - num)) {
            return [map.get(target - num), i]
        }
        map.set(num, i)
    }
    return []
}

const nums = [2,7,11,15]
const target = 9
console.log(findNums(nums, target))