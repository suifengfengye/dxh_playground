
// 1. 获取函数类型的最后一个参数的类型
// type ParamersType = Paramers<T>

type Last<T extends any[]> = T extends [...infer R, infer L] ? L : never

type LastArgType<F extends (...args: any[]) => any> = Last<Parameters<F>>

function foo(a: boolean, b: number, c: string): number {
    return 1
}

type LastArgTypeFoo = LastArgType<typeof foo>

// 2. 如何获取一个函数的返回类型
type FnReturnType = ReturnType<typeof foo>
type MyReturnType<T extends (...args: any[]) => any> = T extends (...args: any[]) => infer R ? R: any
type FnReturnType2 = MyReturnType<typeof foo>

// 3. MyPartial
interface TestType {
    name: string
    age: number
}

type PartialTestType2 = Partial<TestType>
type MyPartial<T> = {[P in keyof T]?: T[P]}
type PartialTestType3 = MyPartial<TestType>

// 4. MyReadonly

type MyReadonly<T> = {
    readonly [P in keyof T]: T[P]
}

type MyReadonlyTestType = MyReadonly<TestType>