/**

统计射击比赛成绩

题目描述

给定一个射击比赛成绩单，包含多个选手若干次射击的成绩分数，请对每个选手按其最高3个分数之和进行降序排名，输出降序排名后的选手ID序列。

条件如下

1.一个选手可以有多个射击成绩的分数，且次序不固定

2.如果一个选手成绩少于3个，则认为选手的所有成绩无效，排名忽略该选手.

3.如果选手的成绩之和相等，则成绩之和相等的选手按照其ID降序排列。

输入描述

输入第一行，一个整数N，表示该场比赛总共进行了N次射击，产生N个成绩分数

(2<=N<=100)输入第二行，一个长度为N整数序列，表示参与每次射击的选手ID(0<=ID<=99)

。输入第三行，一个长度为N整数序列，表示参与每次射击的选手对应的成绩(0<=成绩<=100)

输出描述

符合题设条件的降序排名后的选手ID序列。

# 13
# 3,3,7,4,4,4,4,7,7,3,5,5,5
# 53,80,68,24,39,76,66,16,100,55,53,80,55

=> 5,3,7,4

 */

const times = 13
const ids = [3,3,7,4,4,4,4,7,7,3,5,5,5]
const scores = [53,80,68,24,39,76,66,16,100,55,53,80,55]

const sortShot = (times: number, ids: number[], scores: number[]) => {
    const scoreMap = new Map()
    // 1. 根据id聚合
    for (let i = 0; i < times; i++) {
        const idItem = ids[i]
        const scoreItem = scores[i]
        if (!scoreMap.has(idItem)) {
            scoreMap.set(idItem, [])
        }
        const scoreList = scoreMap.get(idItem)
        scoreList.push(scoreItem)
    }
    console.log(scoreMap)
    // 2. 每个id进行统计
    let scoreMapList: Array<Number>[] = []
    scoreMap.forEach((value, key) => {
        if (value.length < 3) {
            return
        }
        let _value = value.sort((a: number, b: number) => {
            if (b > a) {
                return 1
            } else if (a > b) {
                return -1
            }
            return 0
        })
        _value = _value.slice(0, 3)
        console.log('22', _value)
        
        _value = _value.reduce((pre: number, cur: number) => {
            return pre + cur
        }, 0)
        scoreMapList.push([key, _value])
    })
    console.log(scoreMapList)
    // 3. 排序
    scoreMapList = scoreMapList.sort((a: Number[], b: Number[]) => {
        const [aKey, aValue] = a
        const [bKey, bValue] = b
        if (bValue > aValue) {
            return 1
        } else if (aValue > bValue) {
            return -1
        }
        if (bKey > aKey) {
            return 1
        }  else if (aKey > bKey) {
            return -1
        }
        return 0
    })
    return scoreMapList.map((item) => item[0])
}

console.log(sortShot(times, ids, scores))