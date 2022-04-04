from masonite.routes import Route

ROUTES = [
    # auth routes
    Route.get("/login", "auth.LoginController@show").name("login"),
    Route.get("/login/2fa", "auth.LoginController@two_fa").name("login.2fa"),
    Route.post("/login/2fa", "auth.LoginController@check_2fa").name("login.check_2fa"),
    Route.get("/logout", "auth.LoginController@logout").name("logout"),
    Route.post("/login", "auth.LoginController@store").name("login.store"),
    # once logged in
    Route.group(
        [
            Route.get("/", "OTPController@account").name("auth.home"),
            # Route.get("/admin", "OTPController@admin")
            # .name("admin")
            # .middleware("force_2fa"),
            Route.post("/enable", "OTPController@enable"),
            Route.post("/disable", "OTPController@disable"),
            Route.post("/configure", "OTPController@configure"),
            Route.get("/verify", "OTPController@show_verification"),
            Route.post("/verify", "OTPController@verify"),
            Route.post("/refresh-codes", "OTPController@refresh_backup_codes"),
        ],
        middleware=["auth"],
    ),
]
