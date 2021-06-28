{
    "dev": {
        "app_function": "app.app",
        "aws_region": "us-east-2",
        "project_name": "serverlesscraft",
        "runtime": "python3.8",
        "s3_bucket": "hello-zappa",
        "aws_environment_variables": {
            "DISCORD_CLIENT_ID": "$DISCORD_CLIENT_ID",
            "DISCORD_PUBLIC_KEY": "$DISCORD_PUBLIC_KEY",
            "DISCORD_CLIENT_SECRET": "$DISCORD_CLIENT_SECRET"
        }
    }
}