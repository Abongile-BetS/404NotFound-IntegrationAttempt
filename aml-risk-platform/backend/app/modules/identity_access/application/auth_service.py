class AuthService:
	def to_user_response(self, current_user: dict):
		return {
			"id": current_user.get("sub"),
			"username": current_user.get("preferred_username"),
			"email": current_user.get("email"),
			"roles": current_user.get("realm_access", {}).get("roles", []),
		}
