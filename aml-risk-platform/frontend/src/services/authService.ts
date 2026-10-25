import type { LoginRequest, RegisterRequest } from "../types/auth";

export async function login(
    data: LoginRequest
) {
    console.log("Login:", data);

    return {
        success: true
    };
}

export async function register(
    data: RegisterRequest
) {
    console.log("Register:", data);

    return {
        success: true
    };
}