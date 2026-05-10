interface User {
    name: string;
    age: number;
}
declare const useVersion: () => string;
declare const _default: {
    add: (a: number, b: number) => number;
    multiply: (a: number, b: number) => number;
    heyi: string;
    VERSION: string;
};

export { type User, _default as default, useVersion };
