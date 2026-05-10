// src/index.ts
import { VERSION } from "@dxh-fhook/core";

// src/math.ts
var add = (a, b) => {
  return a + b;
};
var multiply = (a, b) => {
  return a * b;
};
var heyi = "dxh";

// src/index.ts
var useVersion = () => {
  return VERSION;
};
var index_default = {
  add,
  multiply,
  heyi,
  VERSION
};
export {
  index_default as default,
  useVersion
};
//# sourceMappingURL=index.mjs.map