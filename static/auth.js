const SUPABASE_URL = "YOUR_SUPABASE_URL";
const SUPABASE_PUBLISHABLE_KEY = "YOUR_SUPABASE_PUBLISHABLE_KEY";

const supabaseClient = window.supabase.createClient(
    SUPABASE_URL,
    SUPABASE_PUBLISHABLE_KEY
);


// ==========================================
// LOGIN
// ==========================================

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const email =
            document.getElementById("loginEmail").value.trim();

        const password =
            document.getElementById("loginPassword").value;

        const message =
            document.getElementById("authMessage");

        message.textContent = "Logging in...";

        const { data, error } =
            await supabaseClient.auth.signInWithPassword({
                email: email,
                password: password
            });

        if (error) {

            message.textContent =
                error.message;

            return;
        }

        message.textContent =
            "Login successful. Redirecting...";

        window.location.href = "/";

    });

}


// ==========================================
// SIGNUP
// ==========================================

const signupForm =
    document.getElementById("signupForm");

if (signupForm) {

    signupForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            const name =
                document.getElementById("signupName")
                    .value.trim();

            const email =
                document.getElementById("signupEmail")
                    .value.trim();

            const password =
                document.getElementById("signupPassword")
                    .value;

            const message =
                document.getElementById("authMessage");

            message.textContent =
                "Creating your account...";

            const { data, error } =
                await supabaseClient.auth.signUp({

                    email: email,

                    password: password,

                    options: {
                        data: {
                            full_name: name
                        }
                    }

                });

            if (error) {

                message.textContent =
                    error.message;

                return;
            }

            if (!data.session) {

                message.textContent =
                    "Account created. Please check your email to verify your account.";

                return;
            }

            message.textContent =
                "Account created successfully.";

            window.location.href = "/";

        }
    );

}
