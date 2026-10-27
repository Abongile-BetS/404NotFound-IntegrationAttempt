import { describe, expect, it } from "vitest";
import { paginatedPath } from "./api";

describe("paginatedPath", () => {
    it("uses default pagination", () => {
        expect(paginatedPath("/customers")).toBe("/customers?limit=100&offset=0");
    });

    it("uses provided pagination", () => {
        expect(paginatedPath("/alerts", { limit: 10, offset: 20 })).toBe(
            "/alerts?limit=10&offset=20",
        );
    });
});
