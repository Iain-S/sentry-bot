import { describe, expect, test } from "@jest/globals";
import { sum } from "./sum.js";
describe("sum module", () => {
    test("adds 1 + 2 to equal 3", () => {
        expect(sum(1, 3)).toBe(4);
    });
});
