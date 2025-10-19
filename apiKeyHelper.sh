jwt encode \
--secret "secret" \
'{
    "user_id": "'"${USER}"'",
    "user_email": "'"${USER}"'@example.com",
    "team_id": "engineering",
    "user_role": "proxy_admin",
    "models": ["my-mock-model"]
}'